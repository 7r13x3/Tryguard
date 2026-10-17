# 🛡️ TryGuard

**Automated Ransomware Early-Warning Agent & Active Defense System**

## 📖 Overview
TryGuard is a Python-based Endpoint Detection and Response (EDR) tool designed to detect and neutralize ransomware in real time. It moves beyond simple file monitoring by using behavioral analysis and active defense mechanisms to protect critical files.

## ✨ Key Features
- **Shannon Entropy Detection:** Identifies files being encrypted by calculating their data randomness.
- **Canary Tripwires:** Plants hidden files that trigger an immediate alert if tampered with.
- **Automated Kill Switch:** Uses `psutil` to instantly suspend the malicious process, preventing further encryption.
- **Pure Black GUI:** A clean, terminal-inspired interface built with CustomTkinter.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **GUI:** CustomTkinter
- **Monitoring:** Watchdog
- **Process Management:** Psutil

## 🚀 Getting Started
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tryguard.git
