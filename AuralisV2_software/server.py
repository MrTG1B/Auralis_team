from flask import Flask, request, send_file, send_from_directory
import requests
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Hello from Flask server hi hello!</h1>"

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
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)

def stop_server():
    try:
        requests.post("http://localhost:8080/shutdown")
    except Exception as e:
        print(f"Error stopping server: {e}")
