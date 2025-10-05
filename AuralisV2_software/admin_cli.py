import os
import time
import argparse
from typing import Any, Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

try:
    import mysql.connector
except Exception as e:
    print("mysql-connector-python is required. Install with: pip install mysql-connector-python")
    raise

try:
    from rich.console import Console
    from rich.table import Table
    from rich.theme import Theme
    from rich import box
except Exception as e:
    print("rich is recommended for premium CLI UI. Install with: pip install rich")
    Console = None
    Table = None
    Theme = None
    box = None

DB_HOST = os.environ.get("AURALIS_DB_HOST") or os.environ.get("DB_HOST") or "localhost"
DB_PORT = int(os.environ.get("AURALIS_DB_PORT") or os.environ.get("DB_PORT") or "3306")
DB_USER = os.environ.get("AURALIS_DB_USER") or os.environ.get("DB_USER") or "root"
DB_PASS = os.environ.get("AURALIS_DB_PASS") or os.environ.get("DB_PASS") or ""
DB_NAME = os.environ.get("AURALIS_DB_NAME") or os.environ.get("DB_NAME") or "auralis"

def get_conn():
    return mysql.connector.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        autocommit=True,
    )

def _console() -> Optional[Console]:
    if Console is None or Theme is None:
        return None
    return Console(theme=Theme({
        "title": "bold cyan",
        "ok": "bold green",
        "warn": "yellow",
        "err": "bold red"
    }))

def _table(title: str, headers: List[str]) -> Optional[Table]:
    if Table is None:
        return None
    table = Table(
        title=title,
        title_style="title",
        box=box.ROUNDED if box else None,
        show_lines=False,
        pad_edge=False,
        header_style="bold white on dark_blue"
    )
    for header in headers:
        table.add_column(header)
    return table

def list_streets():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, src FROM street_names ORDER BY name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    c = _console()
    if c and Table:
        t = _table("Streets", ["ID", "Name", "Map Src"])
        for (id_, name, src) in rows:
            t.add_row(str(id_), name or "", (src or "")[:120] + ("…" if src and len(src) > 120 else ""))
        c.print(t)
    else:
        for row in rows:
            print(row)

def list_lights():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT lp.id, lp.name, sn.name AS street, lp.ip, lp.fault_status, lp.fault_type
        FROM light_posts lp
        JOIN street_names sn ON sn.id = lp.street_name_id
        ORDER BY sn.name, lp.name
        """
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    c = _console()
    if c and Table:
        headers = ["ID", "Name", "Street", "IP", "Fault Status", "Fault Type"]
        t = _table("Light Posts", headers)
        for row in rows:
            # Unpack all values from the row and convert them to strings for display
            t.add_row(*(str(val) if val is not None else "" for val in row))
        c.print(t)
    else:
        for row in rows:
            print(row)

def add_street(name: str, src: str | None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO street_names (name, src) VALUES (%s, %s) ON DUPLICATE KEY UPDATE src=VALUES(src)", (name, src))
    print("OK")
    cur.close()
    conn.close()

def update_street(street_id: Optional[int], street_name: Optional[str], new_name: Optional[str], src: Optional[str]):
    if not street_id and not street_name:
        raise SystemExit("Provide --id or --name to identify the street")
    conn = get_conn()
    cur = conn.cursor()
    if street_id is None:
        cur.execute("SELECT id FROM street_names WHERE name=%s", (street_name,))
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close(); raise SystemExit("Street not found")
        street_id = row[0]
    sets = []
    vals = []
    if new_name is not None:
        sets.append("name=%s"); vals.append(new_name)
    if src is not None:
        sets.append("src=%s"); vals.append(src)
    if not sets:
        cur.close(); conn.close(); print("No changes"); return
    vals.append(street_id)
    cur.execute("UPDATE street_names SET " + ", ".join(sets) + " WHERE id=%s", tuple(vals))
    print("OK")
    cur.close(); conn.close()

def add_light(street: str, name: str, **kwargs: Dict[str, Any]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM street_names WHERE name=%s", (street,))
    row = cur.fetchone()
    if not row:
        raise SystemExit("Street not found")
    street_name_id = row[0]
    cur.execute(
        """
        INSERT INTO light_posts (name, street_name_id, location_src, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status, fault_type)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE 
            location_src=VALUES(location_src), ip=VALUES(ip), voltage=VALUES(voltage), current=VALUES(current), 
            power=VALUES(power), energy=VALUES(energy), installation_date=VALUES(installation_date), 
            last_service_date=VALUES(last_service_date), fault_status=VALUES(fault_status), fault_type=VALUES(fault_type)
        """,
        (
            name,
            street_name_id,
            kwargs.get("location_src"),
            kwargs.get("ip"),
            kwargs.get("voltage"),
            kwargs.get("current"),
            kwargs.get("power"),
            kwargs.get("energy"),
            kwargs.get("installation_date"),
            kwargs.get("last_service_date"),
            kwargs.get("fault_status"),
            kwargs.get("fault_type"),
        ),
    )
    print("OK")
    cur.close()
    conn.close()

def update_light(light_id: int, **kwargs: Dict[str, Any]):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM light_posts WHERE id=%s", (light_id,))
    row = cur.fetchone()
    if not row:
        cur.close(); conn.close(); raise SystemExit("Light not found")
    sets = []
    vals = []
    # Added 'fault_type' to the list of updatable fields
    allowed_keys = ["name", "location_src", "ip", "voltage", "current", "power", "energy", "installation_date", "last_service_date", "fault_status", "fault_type"]
    for key in allowed_keys:
        val = kwargs.get(key)
        if val is not None:
            sets.append(f"{key}=%s"); vals.append(val)
    if not sets:
        cur.close(); conn.close(); print("No changes"); return
    vals.append(light_id)
    cur.execute("UPDATE light_posts SET " + ", ".join(sets) + " WHERE id=%s", tuple(vals))
    print("OK")
    cur.close(); conn.close()

def delete_street(street_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM street_names WHERE id=%s", (street_id,))
    print("OK")
    cur.close()
    conn.close()

def delete_light(light_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM light_posts WHERE id=%s", (light_id,))
    print("OK")
    cur.close()
    conn.close()

def monitor(interval: int):
    print("Monitoring changes. Press Ctrl+C to stop.")
    prev_counts = None
    while True:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM street_names")
        streets_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM light_posts")
        lights_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        curr = (streets_count, lights_count)
        if curr != prev_counts:
            print(f"Streets: {streets_count}, Lights: {lights_count}")
            prev_counts = curr
        time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description="Auralis Admin CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-streets", help="List all streets")
    sub.add_parser("list-lights", help="List all light posts")

    p_add_street = sub.add_parser("add-street", help="Add a new street")
    p_add_street.add_argument("name")
    p_add_street.add_argument("--src", default=None)

    p_upd_street = sub.add_parser("update-street", help="Update an existing street")
    p_upd_street.add_argument("--id", type=int)
    p_upd_street.add_argument("--name", help="Current name of the street to identify it")
    p_upd_street.add_argument("--new-name", help="New name for the street")
    p_upd_street.add_argument("--src", help="New map source URL")

    p_add_light = sub.add_parser("add-light", help="Add or update a light post")
    p_add_light.add_argument("street", help="The name of the street this light belongs to")
    p_add_light.add_argument("name", help="The name of the light post")
    light_args = ["location_src", "ip", "voltage", "current", "power", "energy", "installation_date", "last_service_date", "fault_status", "fault_type"]
    for arg in light_args:
        p_add_light.add_argument(f"--{arg}")

    p_upd_light = sub.add_parser("update-light", help="Update specific fields of a light post")
    p_upd_light.add_argument("light_id", type=int, help="The ID of the light to update")
    for arg in light_args: # Re-use the same args
        p_upd_light.add_argument(f"--{arg}")

    p_del_street = sub.add_parser("del-street", help="Delete a street and all its lights")
    p_del_street.add_argument("street_id", type=int)

    p_del_light = sub.add_parser("del-light", help="Delete a specific light post")
    p_del_light.add_argument("light_id", type=int)

    p_mon = sub.add_parser("monitor", help="Monitor database for changes")
    p_mon.add_argument("--interval", type=int, default=5)

    args = parser.parse_args()
    cmd_map = {
        "list-streets": lambda: list_streets(),
        "list-lights": lambda: list_lights(),
        "add-street": lambda: add_street(args.name, args.src),
        "update-street": lambda: update_street(args.id, args.name, args.new_name, args.src),
        "add-light": lambda: add_light(args.street, args.name, **{k: getattr(args, k) for k in light_args}),
        "update-light": lambda: update_light(args.light_id, **{k: getattr(args, k) for k in light_args}),
        "del-street": lambda: delete_street(args.street_id),
        "del-light": lambda: delete_light(args.light_id),
        "monitor": lambda: monitor(args.interval),
    }
    
    action = cmd_map.get(args.cmd)
    if action:
        action()

if __name__ == "__main__":
    main()
