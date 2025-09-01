import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial.tools.list_ports
import subprocess
import threading
import time

FIRMWARE_FILES = {
    "bootloader": "bootloader.bin",
    "partition": "partition-table.bin",
    "app": "app.bin"
}
BAUD = "921600"

class ESP32FlasherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auralis ESP32 Flasher & Configurator")
        self.root.geometry("500x400")

        self.port_var = tk.StringVar()
        self.id_var = tk.StringVar()
        self.cloud_var = tk.StringVar()

        ttk.Label(root, text="Select ESP32 Port:").pack(pady=5)
        self.port_combo = ttk.Combobox(root, textvariable=self.port_var, width=40)
        self.port_combo.pack(pady=5)

        ttk.Button(root, text="Refresh Ports", command=self.refresh_ports).pack(pady=5)

        ttk.Button(root, text="Upload Firmware", command=self.flash_firmware).pack(pady=10)

        ttk.Label(root, text="Device ID:").pack(pady=5)
        ttk.Entry(root, textvariable=self.id_var, width=40).pack(pady=5)

        ttk.Label(root, text="Local Cloud Address:").pack(pady=5)
        ttk.Entry(root, textvariable=self.cloud_var, width=40).pack(pady=5)

        ttk.Button(root, text="Save Config", command=self.save_config).pack(pady=10)

        self.log_text = tk.Text(root, height=10, width=60)
        self.log_text.pack(pady=5)

        self.refresh_ports()

    def refresh_ports(self):
        ports = [p.device for p in serial.tools.list_ports.comports()]
        self.port_combo["values"] = ports
        if ports:
            self.port_combo.current(0)

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def flash_firmware(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "No COM port selected!")
            return

        def run_flash():
            try:
                self.log("Starting firmware upload...")
                cmd = [
                    "esptool.py", "--chip", "esp32",
                    "--port", port, "--baud", BAUD,
                    "write_flash", "-z",
                    "0x1000", FIRMWARE_FILES["bootloader"],
                    "0x8000", FIRMWARE_FILES["partition"],
                    "0x10000", FIRMWARE_FILES["app"]
                ]
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in iter(process.stdout.readline, ''):
                    self.log(line.strip())
                process.wait()
                if process.returncode == 0:
                    self.log("✅ Firmware flashed successfully!")
                else:
                    self.log("❌ Flashing failed.")
            except Exception as e:
                self.log(f"Error: {e}")

        threading.Thread(target=run_flash).start()

    def save_config(self):
        port = self.port_var.get()
        if not port:
            messagebox.showerror("Error", "No COM port selected!")
            return
        device_id = self.id_var.get()
        cloud = self.cloud_var.get()

        if not device_id or not cloud:
            messagebox.showerror("Error", "Please enter Device ID and Cloud Address")
            return

        try:
            ser = serial.Serial(port, 115200, timeout=2)
            time.sleep(2)  # wait for ESP32 reboot
            ser.write(f"CONFIG:{device_id},{cloud}\n".encode())
            self.log("Sent config to ESP32.")
            resp = ser.readline().decode().strip()
            if resp:
                self.log("ESP32 response: " + resp)
            ser.close()
        except Exception as e:
            self.log(f"Error sending config: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32FlasherApp(root)
    root.mainloop()
