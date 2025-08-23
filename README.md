# Auralis: IoT-Enabled Adaptive Smart Street Lighting System

Auralis is an innovative IoT-enabled smart street lighting system designed to significantly reduce energy consumption, enhance automation, and improve fault management in both urban and highway environments. The system features adaptive lighting, real-time fault detection, and a dual-communication architecture to ensure scalability and reliability.

---

## 📋 Table of Contents

* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [Technology Stack](#-technology-stack)
* [Market Potential & Applications](#-market-potential--applications)
* [Results & Performance](#-results--performance)
* [Team](#-team)
* [Getting Started](#-getting-started)
* [Contributing](#-contributing)
* [License](#-license)
* [Contact](#-contact)

---

## ✨ Key Features

* **Adaptive Lighting:** Dynamically adjusts LED brightness based on real-time ambient light (LDR) and motion detection (PIR/IR sensors), reducing energy waste.
* **Real-time Fault Detection:** Monitors and reports anomalies in power, network connectivity, sensors, and LED panels, minimizing downtime and streamlining maintenance.
* **Dual-Communication Architecture:** Uses Wi-Fi for high-bandwidth urban deployments and LoRaWAN for long-range, low-power highway and rural applications.
* **High Energy Efficiency:** Achieves up to 80% reduction in energy consumption compared to traditional static street lighting systems.
* **Cost-Effective & Modular:** Built using the ESP32 Devkit V1 and common sensors, making the solution accessible and scalable.
* **Cloud-Based Monitoring:** Uploads real-time operational data and fault alerts to a cloud platform for centralized control.

---

## 🏗️ System Architecture

The system prioritizes ambient light conditions to determine light activation. Once active, occupancy-based lighting adjusts brightness based on motion, while continuous monitoring detects system faults for rapid response.

---

## 🛠️ Technology Stack

**Microcontroller:** ESP32 Devkit V1
**Sensors:**

* Light Dependent Resistor (LDR) for ambient light
* Passive Infrared (PIR) Sensor for motion detection (field deployment)
* Infrared (IR) Sensor for motion detection (prototype)
* Voltage & Current Sensors for fault monitoring

**Communication:**

* Wi-Fi (802.11 b/g/n)
* LoRaWAN

**Lighting:** 400W LED Luminaires with PWM Dimming Control
**Power:** Regulated 12V Power Supply with Buck Converters

---

## 💡 Market Potential & Applications

Auralis aligns with national initiatives like the Smart Cities Mission and AMRUT in India. With over 35 million streetlights in the country, the demand for efficient and intelligent lighting is significant.

**Applications:**

* Smart Cities & Municipalities: Automated, energy-efficient public lighting networks.
* Highway & Rural Roads: Reliable long-range management using LoRaWAN.
* Industrial Parks & SEZs: Automated lighting based on operational hours.
* Gated Communities & Real Estate: Sensor-based lighting with automated fault alerts.

---

## 📊 Results & Performance

Testing on a simulated 1 km, 3-lane road segment showed:

* **Energy Savings:** Reduced power consumption from 144 kWh/day to 28.8 kWh/day in low-traffic scenarios (80% saving).
* **Fault Detection:** Reliable detection and reporting of line, network, module, LED, and sensor faults with response times between 1.28 to 2.5 seconds.

---

## 👥 Team

* [MrTG1B](https://github.com/MrTG1B)
* [violent-glove](https://github.com/violent-glove)
* [prisha-jr](https://github.com/prisha-jr)
* [BairagiArpan](https://github.com/BairagiArpan)

---

## 🚀 Getting Started

**Prerequisites:**

* Arduino IDE or PlatformIO
* ESP32 Board Support Package
* Required libraries (LoRa, Wi-Fi, sensor libraries)

**Installation:**

1. Clone the repository: `git clone https://github.com/MrTG1B/Auralis.git`
2. Open the project in your preferred IDE.
3. Install necessary libraries.
4. Upload the firmware to your ESP32 board.
5. Configure your cloud platform credentials in the `config.h` file.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Contact

* **Project Lead:** MrTG1B - [tirthankardasgupta913913@gmail.com](mailto:tirthankardasgupta913913@gmail.com)
* **Project Link:** [https://github.com/MrTG1B/Auralis](https://github.com/MrTG1B/Auralis)
