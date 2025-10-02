from flask import Flask, request, send_file, send_from_directory, jsonify, Response
import requests
import os
import json
import datetime

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
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
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
DB_HOST = os.environ.get("AURALIS_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("AURALIS_DB_PORT", "3306"))
DB_USER = os.environ.get("AURALIS_DB_USER", "root")
DB_PASS = os.environ.get("AURALIS_DB_PASS", "")
DB_NAME = os.environ.get("AURALIS_DB_NAME", "auralis")

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
            CREATE TABLE IF NOT EXISTS areas (
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
                area_id INT NOT NULL,
                location_src TEXT NULL,
                ip VARCHAR(255) NULL,
                voltage VARCHAR(64) NULL,
                current VARCHAR(64) NULL,
                power VARCHAR(64) NULL,
                energy VARCHAR(64) NULL,
                installation_date VARCHAR(64) NULL,
                last_service_date VARCHAR(64) NULL,
                fault_status VARCHAR(64) NULL,
                CONSTRAINT uq_light UNIQUE (name, area_id),
                CONSTRAINT fk_light_area FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        )
        cur.close()
        conn.close()
    except MySQLError as e:
        print(f"[MySQL] init_db_schema error: {e}")

def migrate_json_if_empty():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM areas")
        (area_count,) = cur.fetchone()
        if area_count and area_count > 0:
            cur.close()
            conn.close()
            return

        data = load_database() or {}
        for area_name, area_payload in data.items():
            src = area_payload.get("src")
            cur.execute("INSERT IGNORE INTO areas (name, src) VALUES (%s, %s)", (area_name, src))
            cur.execute("SELECT id, src FROM areas WHERE name=%s", (area_name,))
            row = cur.fetchone()
            if not row:
                continue
            area_id = row[0]
            lp_map = (area_payload.get("lp") or {})
            for lp_name, lp in lp_map.items():
                cur.execute(
                    """
                    INSERT INTO light_posts
                    (name, area_id, location_src, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        location_src=VALUES(location_src), ip=VALUES(ip), voltage=VALUES(voltage),
                        current=VALUES(current), power=VALUES(power), energy=VALUES(energy),
                        installation_date=VALUES(installation_date), last_service_date=VALUES(last_service_date),
                        fault_status=VALUES(fault_status)
                    """,
                    (
                        lp.get("name"),
                        area_id,
                        lp.get("location_src"),
                        lp.get("ip"),
                        lp.get("voltage"),
                        lp.get("current"),
                        lp.get("power"),
                        lp.get("energy"),
                        lp.get("installation_date"),
                        lp.get("last_service_date"),
                        lp.get("fault_status"),
                    ),
                )
        cur.close()
        conn.close()
        print("[MySQL] Migration from database.json completed (if needed)")
    except MySQLError as e:
        print(f"[MySQL] migrate_json_if_empty error: {e}")


@app.route("/")
def home():
    return "<h1>Hello from Flask server hi hello!</h1>"

@app.route("/arealist")
def proxy_arealist():
    # Prefer MySQL if available
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM areas ORDER BY name ASC")
        areas = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return ("\n".join(areas), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db:
            return ("database.json not found or invalid", 500, {"Content-Type": "text/plain; charset=utf-8"})
        areas = list(db.keys())
        return ("\n".join(areas), 200, {"Content-Type": "text/plain; charset=utf-8"})

@app.route("/area/<path:area>/lp")
def get_area_lps(area):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM areas WHERE name=%s", (area,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        area_id = row[0]
        cur.execute("SELECT name FROM light_posts WHERE area_id=%s ORDER BY name ASC", (area_id,))
        names = [r[0] for r in cur.fetchall()]
        cur.close()
        conn.close()
        return ("\n".join(names), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or area not in db:
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        lps = list((db[area].get("lp") or {}).keys())
        return ("\n".join(lps), 200, {"Content-Type": "text/plain; charset=utf-8"})

@app.route("/area/<path:area>/map")
def get_area_map(area):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT src FROM areas WHERE name=%s", (area,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        src = row[0]
        if not src:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return (src, 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or area not in db:
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        src = db[area].get("src")
        if not src:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return (src, 200, {"Content-Type": "text/plain; charset=utf-8"})

@app.route("/<path:area>/<path:light>/lpdetails")
def get_lp_details(area, light):
    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM areas WHERE name=%s", (area,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return jsonify({"error": "Area not found"}), 404
        area_id = row["id"]
        cur.execute(
            "SELECT name, location_src, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status FROM light_posts WHERE area_id=%s AND name=%s",
            (area_id, light),
        )
        lp = cur.fetchone()
        cur.close()
        conn.close()
        if not lp:
            return jsonify({"error": "Light not found"}), 404
        return jsonify(lp)
    except Exception as _:
        db = load_database()
        if not db or area not in db:
            return jsonify({"error": "Area not found"}), 404
        lp = (db[area].get("lp") or {}).get(light)
        if not lp:
            return jsonify({"error": "Light not found"}), 404
        return jsonify(lp)

@app.route("/<path:area>/<path:light>/location_src")
def get_lp_location_src(area, light):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM areas WHERE name=%s", (area,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        area_id = row[0]
        cur.execute("SELECT location_src FROM light_posts WHERE area_id=%s AND name=%s", (area_id, light))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            return ("Light not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        src = row[0]
        if not src:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return (src, 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or area not in db:
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        lp = (db[area].get("lp") or {}).get(light)
        if not lp:
            return ("Light not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        src = lp.get("location_src")
        if not src:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return (src, 200, {"Content-Type": "text/plain; charset=utf-8"})

@app.route("/area/<path:area>/faulty_lp")
def get_faulty_lps(area):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM areas WHERE name=%s", (area,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        area_id = row[0]
        cur.execute("SELECT name FROM light_posts WHERE area_id=%s AND fault_status='Faulty' ORDER BY name ASC", (area_id,))
        names = [r[0] for r in cur.fetchall()]
        cur.close()
        conn.close()
        if not names:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        return ("\n".join(names), 200, {"Content-Type": "text/plain; charset=utf-8"})
    except Exception as _:
        db = load_database()
        if not db or area not in db:
            return ("Area not found", 404, {"Content-Type": "text/plain; charset=utf-8"})
        faulty = db[area].get("faulty_lp") or {}
        if not faulty:
            return ("", 204, {"Content-Type": "text/plain; charset=utf-8"})
        names = list(faulty.keys())
        return ("\n".join(names), 200, {"Content-Type": "text/plain; charset=utf-8"})

# -------------------- Data update endpoints (store into MySQL) --------------------
@app.route("/admin/area", methods=["POST"])
def create_or_update_area():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    src = payload.get("src")
    if not name:
        return jsonify({"error": "name is required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO areas (name, src) VALUES (%s, %s) ON DUPLICATE KEY UPDATE src=VALUES(src)", (name, src))
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/light", methods=["POST"])
def create_or_update_light():
    payload = request.get_json(silent=True) or {}
    area = payload.get("area")
    name = payload.get("name")
    if not area or not name:
        return jsonify({"error": "area and name are required"}), 400
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM areas WHERE name=%s", (area,))
        row = cur.fetchone()
        if not row:
            return jsonify({"error": "Area not found"}), 404
        area_id = row[0]
        cur.execute(
            """
            INSERT INTO light_posts
            (name, area_id, location_src, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                location_src=VALUES(location_src), ip=VALUES(ip), voltage=VALUES(voltage),
                current=VALUES(current), power=VALUES(power), energy=VALUES(energy),
                installation_date=VALUES(installation_date), last_service_date=VALUES(last_service_date),
                fault_status=VALUES(fault_status)
            """,
            (
                name,
                area_id,
                payload.get("location_src"),
                payload.get("ip"),
                payload.get("voltage"),
                payload.get("current"),
                payload.get("power"),
                payload.get("energy"),
                payload.get("installation_date"),
                payload.get("last_service_date"),
                payload.get("fault_status"),
            ),
        )
        cur.close()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        init_db_schema()
        migrate_json_if_empty()
    except Exception as e:
        print(f"[Startup] DB init/migration skipped: {e}")
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

def stop_server():
    try:
        requests.post("http://localhost:8080/shutdown")
    except Exception as e:
        print(f"Error stopping server: {e}")
