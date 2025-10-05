from flask import Flask, request, send_file, send_from_directory, jsonify, Response
from flask_socketio import SocketIO, emit, join_room, leave_room
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-insecure')
socketio = SocketIO(app, cors_allowed_origins="*")


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

# --- PROFESSIONAL SOCKET.IO IMPLEMENTATION ---

def get_street_data(street_name):
    """A helper function to fetch all light post data for a given street name."""
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street_name,))
        street_row = cur.fetchone()
        if not street_row:
            cur.close(); conn.close()
            return None
        
        street_name_id = street_row["id"]
        cur.execute(
            """
            SELECT 
                lp.id, lp.name, lp.lat, lp.lon, lp.fault_status, lp.voltage, lp.current, 
                lp.power, lp.energy, lp.installation_date, lp.last_service_date, lp.fault_type,
                lp.location_src, lp.ip, lp.on_time, lp.off_time
            FROM light_posts lp
            WHERE lp.street_name_id=%s
            ORDER BY LENGTH(lp.name), lp.name ASC
            """,
            (street_name_id,)
        )
        lights = cur.fetchall()
        # Convert time objects to strings for JSON serialization
        for light in lights:
            if isinstance(light.get('on_time'), datetime.timedelta):
                light['on_time'] = str(light['on_time'])
            if isinstance(light.get('off_time'), datetime.timedelta):
                light['off_time'] = str(light['off_time'])

        cur.close()
        conn.close()
        return lights
    except Exception as e:
        print(f"[SocketIO Helper] Error fetching data for {street_name}: {e}")
        return None

def push_street_update(street_name):
    """Fetches fresh data for a street and pushes it to the corresponding room."""
    print(f"[SocketIO] Preparing to push update for room: {street_name}")
    street_data = get_street_data(street_name)
    if street_data is not None:
        socketio.emit('street_data_update', street_data, room=street_name)
        print(f"[SocketIO] Successfully pushed data update to room: {street_name}")

def broadcast_street_list_update():
    """Broadcasts a global event to all clients to refresh their street list."""
    socketio.emit('street_list_updated')
    print("[SocketIO] Broadcast 'street_list_updated' to all clients.")

@socketio.on('connect')
def handle_connect():
    print('[SocketIO] Client connected successfully.')

@socketio.on('disconnect')
def handle_disconnect():
    print('[SocketIO] Client disconnected.')

@socketio.on('join_room')
def handle_join_room(street_name):
    join_room(street_name)
    print(f'[SocketIO] Client {request.sid} joined room: {street_name}')
    # Immediately push the latest data to the client that just joined
    push_street_update(street_name)


@socketio.on('leave_room')
def handle_leave_room(street_name):
    leave_room(street_name)
    print(f'[SocketIO] Client {request.sid} left room: {street_name}')


# -------------------- MySQL helpers --------------------
def get_env(key: str, default: str):
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

def init_db_schema():
    try:
        conn = mysql.connector.connect( host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, autocommit=True)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cur.close(); conn.close()
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS street_names (
                id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE NOT NULL, src TEXT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS light_posts (
                id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, street_name_id INT NOT NULL,
                location_src TEXT NULL, lat DOUBLE NULL, lon DOUBLE NULL, ip VARCHAR(255) NULL,
                voltage VARCHAR(64) NULL, current VARCHAR(64) NULL, power VARCHAR(64) NULL,
                energy VARCHAR(64) NULL, installation_date VARCHAR(64) NULL, last_service_date VARCHAR(64) NULL,
                fault_status VARCHAR(64) NULL, fault_type VARCHAR(64) NULL,
                on_time TIME NULL, off_time TIME NULL,
                CONSTRAINT uq_light UNIQUE (name, street_name_id),
                CONSTRAINT fk_light_street FOREIGN KEY (street_name_id) REFERENCES street_names(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;""")
        cur.close(); conn.close()
    except MySQLError as e:
        print(f"[MySQL] init_db_schema error: {e}")

def dms_to_decimal(dms: str) -> float:
    match = re.match(r"(\d+)°(\d+)'([\d\.]+)\"?([NSEW])", dms.strip())
    if not match: raise ValueError(f"Invalid DMS format: {dms}")
    deg, minutes, seconds, direction = match.groups()
    decimal = float(deg) + float(minutes)/60 + float(seconds)/3600
    if direction in ['S','W']: decimal = -decimal
    return decimal

@app.route("/")
def home():
    return "<h1>Auralis Real-Time Server is Running</h1>"

# -------------------- HTTP GET Endpoints --------------------

# **FIX:** Restored the essential /streetnames endpoint for the dashboard.
@app.route("/streetnames")
def proxy_street_names_list():
    """Public endpoint for the dashboard to get a simple list of street names."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM street_names ORDER BY name ASC")
        streets = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return ("\n".join(streets), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as e:
        print(f"Error in /streetnames: {e}")
        return ("Server error while fetching street names.", 500)

@app.route("/admin/streets", methods=["GET"]) 
def list_streets():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, name, src FROM street_names ORDER BY name ASC")
        rows = cur.fetchall()
        cur.close(); conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/lights", methods=["GET"]) 
def list_lights():
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT lp.id, lp.name, sn.name AS street_name, lp.lat, lp.lon, lp.location_src, lp.ip, 
                   lp.voltage, lp.current, lp.power, lp.energy, lp.installation_date, 
                   lp.last_service_date, lp.fault_status, lp.fault_type, lp.on_time, lp.off_time
            FROM light_posts lp
            JOIN street_names sn ON sn.id = lp.street_name_id
            ORDER BY sn.name, LENGTH(lp.name), lp.name ASC
            """)
        rows = cur.fetchall()
        # Convert time objects to strings for JSON serialization
        for row in rows:
            if isinstance(row.get('on_time'), datetime.timedelta):
                row['on_time'] = str(row['on_time'])
            if isinstance(row.get('off_time'), datetime.timedelta):
                row['off_time'] = str(row['off_time'])

        cur.close(); conn.close()
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/street/<path:street>/lp_locations")
def get_lp_locations_http(street):
    """HTTP endpoint to get initial data for a street map dashboard."""
    data = get_street_data(street) # Uses the same fixed helper function
    if data is None:
        return jsonify({"error": "Street not found or database error"}), 404
    return jsonify(data)

from flask import request, jsonify

@app.route("/fault_search", methods=["POST"])
def fault_search():
    try:
        # Parse the JSON body
        data = request.get_json()
        if not data or "street_name" not in data:
            return jsonify({"error": "Missing 'street_name' in request"}), 400

        street_name = data["street_name"]

        # Get street data using helper
        street_data = get_street_data(street_name)
        if street_data is None:
            return jsonify({"error": "Street not found or database error"}), 404

        # Respond with the result
        return jsonify({"status": "ok", "data": street_data})

    except Exception as e:
        print(f"Error in /fault_search: {e}")
        return jsonify({"error": "Internal server error"}), 500

# -------------------- Admin Data Mutation Endpoints (Now with SocketIO) --------------------

@app.route("/admin/street", methods=["POST"])
def create_street():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name: return jsonify({"error": "name is required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO street_names (name, src) VALUES (%s, %s) ON DUPLICATE KEY UPDATE src=VALUES(src)", (name, payload.get("src")))
        cur.close(); conn.close()
        broadcast_street_list_update()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/street/<int:street_id>", methods=["DELETE"]) 
def delete_street(street_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM street_names WHERE id=%s", (street_id,))
        cur.close(); conn.close()
        broadcast_street_list_update()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/street/<int:street_id>", methods=["PATCH"]) 
def patch_street(street_id):
    payload = request.get_json(silent=True) or {}
    updates, vals = [], []
    for key in ["name", "src"]:
        if key in payload:
            updates.append(f"{key}=%s"); vals.append(payload[key])
    if not updates: return jsonify({"error": "No fields to update"}), 400
    try:
        conn = get_db_connection(); cur = conn.cursor()
        vals.append(street_id)
        cur.execute("UPDATE street_names SET " + ", ".join(updates) + " WHERE id=%s", tuple(vals))
        cur.close(); conn.close()
        broadcast_street_list_update()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light", methods=["POST"])
def create_light():
    payload = request.get_json(silent=True) or {}
    street_name = payload.get("street_name")
    if not street_name or not payload.get("name"):
        return jsonify({"error": "street_name and name are required"}), 400
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street_name,))
        row = cur.fetchone()
        if not row: 
            cur.close(); conn.close()
            return jsonify({"error": "Street not found"}), 404
        street_name_id = row[0]
        
        sql = """INSERT INTO light_posts (name, street_name_id, location_src, lat, lon, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status, fault_type, on_time, off_time)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 ON DUPLICATE KEY UPDATE location_src=VALUES(location_src), lat=VALUES(lat), lon=VALUES(lon), ip=VALUES(ip), voltage=VALUES(voltage), current=VALUES(current), power=VALUES(power), energy=VALUES(energy), installation_date=VALUES(installation_date), last_service_date=VALUES(last_service_date), fault_status=VALUES(fault_status), fault_type=VALUES(fault_type), on_time=VALUES(on_time), off_time=VALUES(off_time)"""
        
        lat, lon = payload.get('lat'), payload.get('lon') 
        params = (payload.get('name'), street_name_id, payload.get('location_src'), lat, lon, payload.get('ip'), payload.get('voltage'), payload.get('current'), payload.get('power'), payload.get('energy'), payload.get('installation_date'), payload.get('last_service_date'), payload.get('fault_status'), payload.get('fault_type'), payload.get('on_time'), payload.get('off_time'))
        cur.execute(sql, params)
        cur.close(); conn.close()
        push_street_update(street_name)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light/<int:light_id>", methods=["DELETE"]) 
def delete_light(light_id):
    street_name_to_notify = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT sn.name FROM street_names sn JOIN light_posts lp ON lp.street_name_id = sn.id WHERE lp.id = %s", (light_id,))
        result = cur.fetchone()
        if result: street_name_to_notify = result[0]
        cur.execute("DELETE FROM light_posts WHERE id=%s", (light_id,))
        cur.close(); conn.close()
        if street_name_to_notify: push_street_update(street_name_to_notify)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light/<int:light_id>", methods=["PATCH"]) 
def patch_light(light_id):
    payload = request.get_json(silent=True) or {}
    street_name_to_notify = None
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT sn.name FROM street_names sn JOIN light_posts lp ON lp.street_name_id = sn.id WHERE lp.id = %s", (light_id,))
        result = cur.fetchone()
        if result: street_name_to_notify = result[0]
        
        allowed = ["name","location_src","lat","lon","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status", "fault_type", "on_time", "off_time"]
        updates, vals = [], []
        for key in allowed:
            if key in payload:
                updates.append(f"{key}=%s"); vals.append(payload[key])
        if not updates: return jsonify({"error": "No valid fields to update"}), 400
        
        vals.append(light_id)
        cur.execute("UPDATE light_posts SET " + ", ".join(updates) + " WHERE id=%s", tuple(vals))
        cur.close(); conn.close()
        if street_name_to_notify: push_street_update(street_name_to_notify)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Static Files & Server Start --------------------
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
    if func is None: raise RuntimeError("Not running with the Werkzeug Server")
    func()
    return "Server shutting down..."

def run_server():
    try:
        init_db_schema()
    except Exception as e:
        print(f"[Startup] DB init skipped: {e}")
    socketio.run(app, host="0.0.0.0", port=8080, debug=True, use_reloader=True)

def stop_server():
    try:
        requests.post("http://localhost:8080/shutdown")
    except Exception as e:
        print(f"Error stopping server: {e}")

if __name__ == '__main__':
    run_server()

