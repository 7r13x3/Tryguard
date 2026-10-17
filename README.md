# 🛡️ TryGuard

**Automated Ransomware Early-Warning Agent & Active Defense System**

## 📖 Overview
TryGuard is a Python-based Endpoint Detection and Response (EDR) tool designed to detect, neutralize, and recover from ransomware attacks in real-time. It moves beyond simple file monitoring by using behavioral analysis, active defense mechanisms, and automated file recovery to protect critical data.

## ✨ Key Features
- **Shannon Entropy Detection:** Identifies files being encrypted by calculating their data randomness in real-time.
- **Behavioral Threat Scoring:** Processes earn points for malicious behavior (e.g., dropping ransom notes, changing extensions, or high entropy). At 100 points, the Kill Switch triggers.
- **MITRE ATT&CK Mapping:** Alerts are automatically tagged with the relevant MITRE ATT&CK framework ID (e.g., `T1486: Data Encrypted for Impact`).
- **Automated Kill Switch:** Uses `psutil` to instantly suspend the malicious process tree, freezing the ransomware in its tracks.
- **Recovery Vault:** Automatically backs up the protected folder upon startup. If an attack occurs, it restores the encrypted files instantly, resulting in zero data loss.
- **Visual Threat Meter:** A live UI progress bar that shifts from Green (Safe) to Yellow (Warning) to Red (Critical) as the threat score increases.
- **Forensic Reporting:** Generates a detailed `tryguard_forensic_report.json` file upon detecting an attack for post-incident analysis.
- **Modern GUI:** A sleek, minimal, pure-black interface built with CustomTkinter.

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **GUI:** CustomTkinter
- **Monitoring:** Watchdog
- **Process Management:** Psutil

## 🚀 Getting Started

### 1. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/yourusername/tryguard.git
cd tryguard
pip install -r requirements.txt
