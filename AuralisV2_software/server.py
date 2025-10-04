from flask import Flask, request, send_file, send_from_directory, jsonify, Response
import requests
import os
import json
import datetime
import re

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except Exception as _:
    mysql = None
    MySQLError = Exception

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

EXTERNAL_BASE = "https://r6jncd1n-8080.inc1.devtunnels.ms"

DATABASE_PATH = os.path.join("database", "database.json")

def load_database():
    try:
        with open(DATABASE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

# -------------------- MySQL helpers --------------------
def get_env(key: str, default: str):
    # Prefer AURALIS_* then DB_* then default
    return os.environ.get(key) or os.environ.get(key.replace("AURALIS_", "DB_")) or default

DB_HOST = get_env("AURALIS_DB_HOST", "localhost")
DB_PORT = int(get_env("AURALIS_DB_PORT", "3306"))
DB_USER = get_env("AURALIS_DB_USER", "root")
DB_PASS = get_env("AURALIS_DB_PASS", "")
DB_NAME = get_env("AURALIS_DB_NAME", "auralis")

def get_db_connection():
    if mysql is None:
        raise RuntimeError("mysql-connector-python is not installed")
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True,
    )

def run_db_migrations():
    """
    Checks for old table 'areas' and migrates it to 'street_names'.
    This is designed to be run once and is idempotent.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if 'areas' table exists
        cur.execute("SHOW TABLES LIKE 'areas'")
        if cur.fetchone():
            print("[MySQL] Found old 'areas' table. Starting migration to 'street_names' schema.")
            
            # Step 1: Rename 'areas' to 'street_names'.
            try:
                cur.execute("RENAME TABLE areas TO street_names")
                print("[MySQL] -> Renamed table 'areas' to 'street_names'.")
            except MySQLError as e:
                if e.errno == 1050: # Table 'street_names' already exists
                     print("[MySQL] -> Table 'street_names' already exists. Manual data merge may be required. Proceeding with column migration.")
                else:
                    print(f"[MySQL] Could not rename 'areas' table: {e}")
                    raise e

            # Step 2: Check if 'light_posts' table has the old 'area_id' column
            cur.execute("SHOW COLUMNS FROM light_posts LIKE 'area_id'")
            if cur.fetchone():
                print("[MySQL] Found old 'area_id' column in 'light_posts'. Migrating column and foreign key.")

                # Step 2a: Drop the old foreign key constraint if it exists.
                # The original constraint was named 'fk_light_area'.
                try:
                    cur.execute("ALTER TABLE light_posts DROP FOREIGN KEY fk_light_area")
                    print("[MySQL] -> Dropped old foreign key 'fk_light_area'.")
                except MySQLError as e:
                    if e.errno == 1091: # Can't DROP '...'; check that key exists
                        print("[MySQL] -> Foreign key 'fk_light_area' not found, skipping drop.")
                    else:
                        print(f"[MySQL] Error dropping foreign key, may need manual intervention: {e}")

                # Step 2b: Rename the column
                cur.execute("ALTER TABLE light_posts CHANGE COLUMN area_id street_name_id INT NOT NULL")
                print("[MySQL] -> Renamed column 'area_id' to 'street_name_id'.")
                
                # Step 2c: Add the new foreign key constraint
                try:
                    cur.execute("ALTER TABLE light_posts ADD CONSTRAINT fk_light_street FOREIGN KEY (street_name_id) REFERENCES street_names(id) ON DELETE CASCADE")
                    print("[MySQL] -> Added new foreign key 'fk_light_street'.")
                except MySQLError as e:
                    if e.errno == 1826: # Duplicate foreign key constraint name
                        print("[MySQL] -> Foreign key 'fk_light_street' already exists, skipping add.")
                    else:
                        print(f"[MySQL] Error adding new foreign key. Check for orphaned light_posts: {e}")
            
            print("[MySQL] Schema migration check completed.")
        
        cur.close()
        conn.close()
    except MySQLError as e:
        print(f"[MySQL] Migration failed with a database error: {e}")
    except Exception as e:
        print(f"[Migration] An unexpected error occurred: {e}")


def init_db_schema():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            autocommit=True,
        )
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cur.close()
        conn.close()

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS street_names (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                src TEXT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS light_posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                street_name_id INT NOT NULL,
                location_src TEXT NULL,
                lat DOUBLE NULL,
                lon DOUBLE NULL,
                ip VARCHAR(255) NULL,
                voltage VARCHAR(64) NULL,
                current VARCHAR(64) NULL,
                power VARCHAR(64) NULL,
                energy VARCHAR(64) NULL,
                installation_date VARCHAR(64) NULL,
                last_service_date VARCHAR(64) NULL,
                fault_status VARCHAR(64) NULL,
                fault_type VARCHAR(64) NULL,
                CONSTRAINT uq_light UNIQUE (name, street_name_id),
                CONSTRAINT fk_light_street FOREIGN KEY (street_name_id) REFERENCES street_names(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cur.close()
        conn.close()
    except MySQLError as e:
        print(f"[MySQL] init_db_schema error: {e}")
        print(
            "If the database does not exist or you lack privileges, please create it and grant access:\n"
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n"
            f"-- create user if needed and grant privileges to user '{DB_USER}'\n"
            f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'%'; FLUSH PRIVILEGES;"
        )

def migrate_json_if_empty():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM street_names")
        (street_count,) = cur.fetchone()
        if street_count and street_count > 0:
            cur.close()
            conn.close()
            return

        data = load_database() or {}
        for street_name, street_payload in data.items():
            src = street_payload.get("src")
            cur.execute("INSERT IGNORE INTO street_names (name, src) VALUES (%s, %s)", (street_name, src))
            cur.execute("SELECT id, src FROM street_names WHERE name=%s", (street_name,))
            row = cur.fetchone()
            if not row:
                continue
            street_name_id = row[0]
            lp_map = (street_payload.get("lp") or {})
            for lp_name, lp in lp_map.items():
                lat = None
                lon = None
                # try to parse from location_src if it's a google maps iframe with center coords; fallback None
                cur.execute(
                    """
                    INSERT INTO light_posts
                    (name, street_name_id, location_src, lat, lon, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status, fault_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        location_src=VALUES(location_src), lat=VALUES(lat), lon=VALUES(lon), ip=VALUES(ip), voltage=VALUES(voltage),
                        current=VALUES(current), power=VALUES(power), energy=VALUES(energy),
                        installation_date=VALUES(installation_date), last_service_date=VALUES(last_service_date),
                        fault_status=VALUES(fault_status), fault_type=VALUES(fault_type)
                    """,
                    (
                        lp.get("name"),
                        street_name_id,
                        lp.get("location_src"),
                        lat,
                        lon,
                        lp.get("ip"),
                        lp.get("voltage"),
                        lp.get("current"),
                        lp.get("power"),
                        lp.get("energy"),
                        lp.get("installation_date"),
                        lp.get("last_service_date"),
                        lp.get("fault_status"),
                        lp.get("fault_type"),
                    ),
                )
        cur.close()
        conn.close()
        print("[MySQL] Migration from database.json completed (if needed)")
    except MySQLError as e:
        print(f"[MySQL] migrate_json_if_empty error: {e}")
        print("Migration skipped. Ensure DB exists and credentials from .env are correct.")

def dms_to_decimal(dms: str) -> float:
    """
    Convert DMS string like '22°34'42.4"N' to decimal degrees float.
    """
    match = re.match(r"(\d+)°(\d+)'([\d\.]+)\"?([NSEW])", dms.strip())
    if not match:
        raise ValueError(f"Invalid DMS format: {dms}")
    
    deg, minutes, seconds, direction = match.groups()
    deg = float(deg)
    minutes = float(minutes)
    seconds = float(seconds)
    decimal = deg + minutes/60 + seconds/3600
    
    if direction in ['S','W']:
        decimal = -decimal
    return decimal

def decimal_to_dms(value: float, latlon: str) -> str:
    """
    Convert decimal degrees to DMS with N/S/E/W.
    latlon = 'lat' or 'lon' to decide suffix.
    """
    direction = ""
    if latlon == "lat":
        direction = "N" if value >= 0 else "S"
    else:
        direction = "E" if value >= 0 else "W"
    
    value = abs(value)
    d = int(value)
    m_float = (value - d) * 60
    m = int(m_float)
    s = (m_float - m) * 60
    return f"{d}°{m}'{s:.1f}\"{direction}"

@app.route("/")
def home():
    return "<h1>Hello from Flask server hi hello!</h1>"

@app.route("/streetnames")
def proxy_street_names_list():
    # Prefer MySQL if available
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM street_names ORDER BY name ASC")
        streets = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return ("\n".join(streets), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db:
            return ("database.json not found or invalid", 500, {"Content-Type": "text/plain; charset=utf-8"})
        streets = list(db.keys())
        return ("\n".join(streets), 200, {"Content-Type": "text/plain; charset=utf-8"})

@app.route("/street/<path:street>/lp")
def get_street_lps(street):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        street_name_id = row[0]
        cur.execute("SELECT name FROM light_posts WHERE street_name_id=%s ORDER BY name ASC", (street_name_id,))
        names = [r[0] for r in cur.fetchall()]
        cur.close()
        conn.close()
        return ("\n".join(names), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or street not in db:
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        lps = list((db[street].get("lp") or {}).keys())
        return ("\n".join(lps), 200, {"Content-Type": "text/plain; charset=utf-8"})

# UPDATED ENDPOINT FOR THE MAP FEATURE
@app.route("/street/<path:street>/lp_locations")
def get_lp_locations(street):
    """
    Gets all light posts for a street with their name, location, status, and other details.
    This is used by the frontend to draw the interactive map with rich popups.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        # First, get the street_name_id for the given street name
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street,))
        street_row = cur.fetchone()
        if not street_row:
            cur.close()
            conn.close()
            return jsonify({"error": "Street not found"}), 404
        
        street_name_id = street_row["id"]

        # Now, fetch all light posts and their details for that street
        cur.execute(
            """
            SELECT 
                name, lat, lon, fault_status, voltage, current, power, energy, 
                installation_date, last_service_date 
            FROM light_posts 
            WHERE street_name_id=%s
            """,
            (street_name_id,)
        )
        lights = cur.fetchall()
        cur.close()
        conn.close()

        if not lights:
            return jsonify([]), 200 # Return empty list if no lights

        # Format the data for the frontend, renaming 'fault_status' to 'status'
        formatted_lights = []
        for light in lights:
            formatted_lights.append({
                "name": light.get("name"),
                "lat": light.get("lat"),
                "lon": light.get("lon"),
                "status": "faulty" if light.get("fault_status") == "Faulty" else "ok",
                "voltage": light.get("voltage"),
                "current": light.get("current"),
                "power": light.get("power"),
                "energy": light.get("energy"),
                "installation_date": light.get("installation_date"),
                "last_service_date": light.get("last_service_date")
            })
        
        return jsonify(formatted_lights)

    except MySQLError as e:
        print(f"[MySQL] Error in /lp_locations: {e}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        print(f"[App] Error in /lp_locations: {e}")
        return jsonify({"error": "An unexpected server error occurred"}), 500

@app.route("/street/<path:street>/map")
def get_street_map(street):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT src FROM street_names WHERE name=%s", (street,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        src = row[0]
        if not src:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return (src, 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or street not in db:
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        src = db[street].get("src")
        if not src:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return (src, 200, {"Content-Type": "text/plain; charset=utf-8"})

@app.route("/<path:street>/<path:light>/lpdetails")
def get_lp_details(street, light):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return jsonify({"error": "Street not found"}), 404
        street_name_id = row["id"]
        cur.execute(
            "SELECT name, location_src, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status, fault_type FROM light_posts WHERE street_name_id=%s AND name=%s",
            (street_name_id, light),
        )
        lp = cur.fetchone()
        cur.close()
        conn.close()
        if not lp:
            return jsonify({"error": "Light not found"}), 404
        return jsonify(lp)
    except Exception as _:
        db = load_database()
        if not db or street not in db:
            return jsonify({"error": "Street not found"}), 404
        lp = (db[street].get("lp") or {}).get(light)
        if not lp:
            return jsonify({"error": "Light not found"}), 404
        return jsonify(lp)

@app.route("/<path:street>/<path:light>/location_src")
def get_lp_location_src(street, light):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        street_name_id = row["id"]
        cur.execute("SELECT lat, lon, location_src FROM light_posts WHERE street_name_id=%s AND name=%s", (street_name_id, light))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return ("Light not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        lat = row.get("lat")
        lon = row.get("lon")
        if lat is not None and lon is not None:
            return jsonify({"lat": lat, "lon": lon})
        # fallback: try to derive from location_src if present
        src = row.get("location_src")
        if src:
            return jsonify({"lat": None, "lon": None, "location_src": src})
        return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or street not in db:
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        lp = (db[street].get("lp") or {}).get(light)
        if not lp:
            return ("Light not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        return jsonify({"lat": None, "lon": None, "location_src": lp.get("location_src")})

@app.route("/street/<path:street>/faulty_lp")
def get_faulty_lps(street):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        street_name_id = row[0]
        cur.execute("SELECT name FROM light_posts WHERE street_name_id=%s AND fault_status='Faulty' ORDER BY name ASC", (street_name_id,))
        names = [r[0] for r in cur.fetchall()]
        cur.close()
        conn.close()
        if not names:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return ("\n".join(names), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or street not in db:
            return ("Street not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        faulty = db[street].get("faulty_lp") or {}
        if not faulty:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        names = list(faulty.keys())
        return ("\n".join(names), 200, {"Content-Type": "text/plain; charset=utf-8"})

# -------------------- Data update endpoints (store into MySQL) --------------------
@app.route("/admin/street", methods=["POST"])
def create_or_update_street():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    src = payload.get("src")
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO street_names (name, src) VALUES (%s, %s) ON DUPLICATE KEY UPDATE src=VALUES(src)", (name, src))
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light", methods=["POST"])
def create_or_update_light():
    payload = request.get_json(silent=True) or {}
    street_name = payload.get("street_name")
    name = payload.get("name")
    if not street_name or not name:
        return jsonify({"error": "street_name and name are required"}), 400

    # Handle lat/lon conversion
    lat_input = payload.get("lat")
    lon_input = payload.get("lon")
    lat = None
    lon = None

    try:
        if lat_input:
            try:
                lat = float(lat_input)  # numeric decimal
            except ValueError:
                lat = dms_to_decimal(lat_input)  # DMS string

        if lon_input:
            try:
                lon = float(lon_input)
            except ValueError:
                lon = dms_to_decimal(lon_input)
    except Exception as conv_err:
        return jsonify({"error": f"Invalid lat/lon format: {conv_err}"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street_name,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Street not found"}), 404
        street_name_id = row[0]

        cur.execute(
            """
            INSERT INTO light_posts
            (name, street_name_id, location_src, lat, lon, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status, fault_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                location_src=VALUES(location_src), lat=VALUES(lat), lon=VALUES(lon), ip=VALUES(ip), voltage=VALUES(voltage),
                current=VALUES(current), power=VALUES(power), energy=VALUES(energy),
                installation_date=VALUES(installation_date), last_service_date=VALUES(last_service_date),
                fault_status=VALUES(fault_status), fault_type=VALUES(fault_type)
            """,
            (
                name,
                street_name_id,
                payload.get("location_src"),
                lat,
                lon,
                payload.get("ip"),
                payload.get("voltage"),
                payload.get("current"),
                payload.get("power"),
                payload.get("energy"),
                payload.get("installation_date"),
                payload.get("last_service_date"),
                payload.get("fault_status"),
                payload.get("fault_type"),
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/streets", methods=["GET"]) 
def list_streets():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, name, src FROM street_names ORDER BY name ASC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/lights", methods=["GET"]) 
def list_lights():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """
            SELECT lp.id, lp.name, sn.name AS street_name, lp.lat, lp.lon, lp.location_src, lp.ip, lp.voltage, lp.current, lp.power, lp.energy, lp.installation_date, lp.last_service_date, lp.fault_status, lp.fault_type
            FROM light_posts lp
            JOIN street_names sn ON sn.id = lp.street_name_id
            ORDER BY sn.name, lp.name
            """
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/street/<int:street_id>", methods=["DELETE"]) 
def delete_street(street_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM street_names WHERE id=%s", (street_id,))
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light/<int:light_id>", methods=["DELETE"]) 
def delete_light(light_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM light_posts WHERE id=%s", (light_id,))
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/street/<int:street_id>", methods=["PATCH"]) 
def patch_street(street_id):
    payload = request.get_json(silent=True) or {}
    updates = []
    vals = []
    for key in ["name", "src"]:
        if key in payload:
            updates.append(f"{key}=%s"); vals.append(payload[key])
    if not updates:
        return jsonify({"error": "No fields to update"}), 400
    try:
        conn = get_db_connection(); cur = conn.cursor()
        vals.append(street_id)
        cur.execute("UPDATE street_names SET " + ", ".join(updates) + " WHERE id=%s", tuple(vals))
        cur.close(); conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light/<int:light_id>", methods=["PATCH"]) 
def patch_light(light_id):
    payload = request.get_json(silent=True) or {}
    allowed = ["name","location_src","lat","lon","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status", "fault_type"]
    updates = []
    vals = []
    for key in allowed:
        if key in payload:
            updates.append(f"{key}=%s"); vals.append(payload[key])
    if not updates:
        return jsonify({"error": "No fields to update"}), 400
    try:
        conn = get_db_connection(); cur = conn.cursor()
        vals.append(light_id)
        cur.execute("UPDATE light_posts SET " + ", ".join(updates) + " WHERE id=%s", tuple(vals))
        cur.close(); conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/superadmin/ui")
def admin_ui():
    return send_file("SuperAdminUI.html")

@app.route("/dashboard")
def dashboard():
    return send_file("index.html")

@app.route("/dashboard/dashboard.html")
def dashboard_html():
    return send_file(os.path.join("dashboard", "dashboard.html"))

@app.route("/dashboard/dashboard_static/<path:filename>")
def static_files(filename):
    # Serves files from d:\Auralis\AuralisV2_software\static
    return send_from_directory("dashboard/dashboard_static", filename)

@app.route("/assets/images/<path:filename>")
def images(filename):
    # Serves files from d:\Auralis\AuralisV2_software\assets\images
    return send_from_directory(os.path.join("assets", "images"), filename)

@app.route("/shutdown", methods=["POST"])
def shutdown():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is None:
        raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return "Server shutting down..."

def run_server():
    # Initialize MySQL schema and migrate JSON at startup (best-effort)
    try:
        run_db_migrations()
        init_db_schema()
        migrate_json_if_empty()
    except Exception as e:
        print(f"[Startup] DB init/migration skipped: {e}")
        print("Set DB credentials in a .env file, e.g.:\n"
              "AURALIS_DB_HOST=localhost\nAURALIS_DB_PORT=3306\nAURALIS_DB_USER=auralis_user\nAURALIS_DB_PASS=StrongPassword123!\nAURALIS_DB_NAME=auralis")
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

def stop_server():
    try:
        requests.post("http://localhost:8080/shutdown")
    except Exception as e:
        print(f"Error stopping server: {e}")