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
	return Table(
		title=title,
		title_style="title",
		box=box.ROUNDED if box else None,
		show_lines=False,
		pad_edge=False,
		header_style="bold white on dark_blue"
	)

def list_areas():
	conn = get_conn()
	cur = conn.cursor()
	cur.execute("SELECT id, name, src FROM areas ORDER BY name")
	rows = cur.fetchall()
	cur.close()
	conn.close()
	c = _console()
	if c and Table:
		t = _table("Areas", ["ID", "Name", "Map Src"])
		for h in ["ID", "Name", "Map Src"]:
			t.add_column(h)
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
		SELECT lp.id, lp.name, a.name AS area, lp.ip, lp.voltage, lp.current, lp.power, lp.energy, lp.fault_status
		FROM light_posts lp
		JOIN areas a ON a.id = lp.area_id
		ORDER BY a.name, lp.name
		"""
	)
	rows = cur.fetchall()
	cur.close()
	conn.close()
	c = _console()
	if c and Table:
		t = _table("Lights", ["ID","Name","Area","IP","V","I","P","E","Fault"])
		for h in ["ID","Name","Area","IP","V","I","P","E","Fault"]:
			t.add_column(h)
		for row in rows:
			id_, name, area, ip, v, i, p, e, fs = row
			t.add_row(str(id_), name or "", area or "", ip or "", v or "", i or "", p or "", e or "", fs or "")
		c.print(t)
	else:
		for row in rows:
			print(row)

def add_area(name: str, src: str | None):
	conn = get_conn()
	cur = conn.cursor()
	cur.execute("INSERT INTO areas (name, src) VALUES (%s, %s) ON DUPLICATE KEY UPDATE src=VALUES(src)", (name, src))
	print("OK")
	cur.close()
	conn.close()

def update_area(area_id: Optional[int], area_name: Optional[str], new_name: Optional[str], src: Optional[str]):
	if not area_id and not area_name:
		raise SystemExit("Provide --id or --name to identify area")
	conn = get_conn()
	cur = conn.cursor()
	if area_id is None:
		cur.execute("SELECT id FROM areas WHERE name=%s", (area_name,))
		row = cur.fetchone()
		if not row:
			cur.close(); conn.close(); raise SystemExit("Area not found")
		area_id = row[0]
	sets = []
	vals = []
	if new_name is not None:
		sets.append("name=%s"); vals.append(new_name)
	if src is not None:
		sets.append("src=%s"); vals.append(src)
	if not sets:
		cur.close(); conn.close(); print("No changes"); return
	vals.append(area_id)
	cur.execute("UPDATE areas SET " + ", ".join(sets) + " WHERE id=%s", tuple(vals))
	print("OK")
	cur.close(); conn.close()

def add_light(area: str, name: str, **kwargs: Dict[str, Any]):
	conn = get_conn()
	cur = conn.cursor()
	cur.execute("SELECT id FROM areas WHERE name=%s", (area,))
	row = cur.fetchone()
	if not row:
		raise SystemExit("Area not found")
	area_id = row[0]
	cur.execute(
		"""
		INSERT INTO light_posts (name, area_id, location_src, ip, voltage, current, power, energy, installation_date, last_service_date, fault_status)
		VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
		ON DUPLICATE KEY UPDATE location_src=VALUES(location_src), ip=VALUES(ip), voltage=VALUES(voltage), current=VALUES(current), power=VALUES(power), energy=VALUES(energy), installation_date=VALUES(installation_date), last_service_date=VALUES(last_service_date), fault_status=VALUES(fault_status)
		""",
		(
			name,
			area_id,
			kwargs.get("location_src"),
			kwargs.get("ip"),
			kwargs.get("voltage"),
			kwargs.get("current"),
			kwargs.get("power"),
			kwargs.get("energy"),
			kwargs.get("installation_date"),
			kwargs.get("last_service_date"),
			kwargs.get("fault_status"),
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
	for key in ["name","location_src","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status"]:
		val = kwargs.get(key)
		if val is not None:
			sets.append(f"{key}=%s"); vals.append(val)
	if not sets:
		cur.close(); conn.close(); print("No changes"); return
	vals.append(light_id)
	cur.execute("UPDATE light_posts SET " + ", ".join(sets) + " WHERE id=%s", tuple(vals))
	print("OK")
	cur.close(); conn.close()

def delete_area(area_id: int):
	conn = get_conn()
	cur = conn.cursor()
	cur.execute("DELETE FROM areas WHERE id=%s", (area_id,))
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
		cur.execute("SELECT COUNT(*) FROM areas")
		areas_count = cur.fetchone()[0]
		cur.execute("SELECT COUNT(*) FROM light_posts")
		lights_count = cur.fetchone()[0]
		cur.close()
		conn.close()
		curr = (areas_count, lights_count)
		if curr != prev_counts:
			print(f"Areas: {areas_count}, Lights: {lights_count}")
			prev_counts = curr
		time.sleep(interval)


def main():
	parser = argparse.ArgumentParser(description="Auralis Admin CLI")
	sub = parser.add_subparsers(dest="cmd", required=True)

	sub.add_parser("list-areas")
	sub.add_parser("list-lights")

	p_add_area = sub.add_parser("add-area")
	p_add_area.add_argument("name")
	p_add_area.add_argument("--src", default=None)

	p_upd_area = sub.add_parser("update-area")
	p_upd_area.add_argument("--id", type=int)
	p_upd_area.add_argument("--name")
	p_upd_area.add_argument("--new-name")
	p_upd_area.add_argument("--src")

	p_add_light = sub.add_parser("add-light")
	p_add_light.add_argument("area")
	p_add_light.add_argument("name")
	for arg in ["location_src","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status"]:
		p_add_light.add_argument(f"--{arg}")

	p_upd_light = sub.add_parser("update-light")
	p_upd_light.add_argument("light_id", type=int)
	for arg in ["name","location_src","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status"]:
		p_upd_light.add_argument(f"--{arg}")

	p_del_area = sub.add_parser("del-area")
	p_del_area.add_argument("area_id", type=int)

	p_del_light = sub.add_parser("del-light")
	p_del_light.add_argument("light_id", type=int)

	p_mon = sub.add_parser("monitor")
	p_mon.add_argument("--interval", type=int, default=5)

	args = parser.parse_args()

	if args.cmd == "list-areas":
		list_areas()
	elif args.cmd == "list-lights":
		list_lights()
	elif args.cmd == "add-area":
		add_area(args.name, args.src)
	elif args.cmd == "update-area":
		update_area(args.id, args.name, args.new_name, args.src)
	elif args.cmd == "add-light":
		kwargs = {k: getattr(args, k) for k in ["location_src","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status"]}
		add_light(args.area, args.name, **kwargs)
	elif args.cmd == "update-light":
		kwargs = {k: getattr(args, k) for k in ["name","location_src","ip","voltage","current","power","energy","installation_date","last_service_date","fault_status"]}
		update_light(args.light_id, **kwargs)
	elif args.cmd == "del-area":
		delete_area(args.area_id)
	elif args.cmd == "del-light":
		delete_light(args.light_id)
	elif args.cmd == "monitor":
		monitor(args.interval)

if __name__ == "__main__":
	main()
