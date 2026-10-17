import customtkinter as ctk
from tkinter import filedialog, messagebox
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import math
import os
import psutil
import json
import datetime
import shutil
from collections import Counter

# ==========================================
# 1. THE MATH: Shannon Entropy
# ==========================================
def calculate_entropy(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            if not data: return 0.0
            byte_counts = Counter(data)
            file_size = len(data)
            entropy = 0.0
            for count in byte_counts.values():
                p_x = count / file_size
                entropy += -p_x * math.log2(p_x)
            return entropy
    except Exception:
        return 0.0

# ==========================================
# 2. THE EDR ENGINE
# ==========================================
class RansomwareDetector(FileSystemEventHandler):
    def __init__(self, gui_callback, target_folder, update_meter):
        self.gui_callback = gui_callback
        self.update_meter = update_meter
        self.target_folder = target_folder
        self.vault_folder = os.path.join(target_folder, ".tryguard_vault")
        self.threat_score = 0
        self.alert_triggered = False
        self.affected_files = []
        
        self.ENTROPY_THRESHOLD = 7.2 
        self.CRITICAL_SCORE = 100

    def add_score(self, points, reason, mitre_id=None):
        if self.alert_triggered: return
        self.threat_score += points
        
        # Update the Visual Meter
        self.update_meter(self.threat_score)
        
        mitre_str = f" [MITRE: {mitre_id}]" if mitre_id else ""
        color = "yellow" if self.threat_score < 100 else "red"
        
        self.gui_callback(f"[!] Threat Score +{points}: {reason}{mitre_str} (Total: {self.threat_score})", color)
        
        if self.threat_score >= self.CRITICAL_SCORE:
            self.trigger_alert(f"Critical Threat Score Reached: {self.threat_score}")

    def on_created(self, event):
        if not event.is_directory and not self.alert_triggered:
            filename = os.path.basename(event.src_path).lower()
            if "read_me" in filename or "decrypt" in filename or "restore" in filename:
                self.add_score(60, f"Ransom note created: {filename}", "T1486")
                self.affected_files.append(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and not self.alert_triggered:
            filename = os.path.basename(event.src_path)
            if ".tryguard_vault" in event.src_path: return

            if filename == ".tryguard_canary.txt":
                self.add_score(100, "Canary Tripwire compromised!", "T1486")
                return

            if filename.endswith(('.locked', '.encrypted', '.crypto', '.crypt')):
                self.add_score(40, f"Suspicious extension: {filename}", "T1486")
                self.affected_files.append(event.src_path)
                return

            entropy = calculate_entropy(event.src_path)
            if entropy > self.ENTROPY_THRESHOLD:
                self.add_score(40, f"High entropy detected in: {filename}", "T1486")
                self.affected_files.append(event.src_path)
            else:
                self.gui_callback(f"[*] Modified: {filename} (Safe: {entropy:.2f})", "grey")

    def trigger_alert(self, reason):
        self.alert_triggered = True
        self.gui_callback(f"\n🚨 [CRITICAL ALERT] {reason}", "red")
        
        self.gui_callback("Initiating Process Suspension Protocol...", "white")
        suspended = suspend_ransomware()
        if suspended:
            self.gui_callback("✅ SUCCESS: Malicious process frozen in memory.", "white")
        else:
            self.gui_callback("⚠️ WARNING: Could not find process to suspend.", "red")

        self.gui_callback("Initiating Recovery Vault...", "white")
        restored = self.restore_vault()
        if restored:
            self.gui_callback("✅ SUCCESS: Encrypted files restored from backup.", "white")

        self.generate_forensic_report()

    def restore_vault(self):
        if os.path.exists(self.vault_folder):
            try:
                shutil.copytree(self.vault_folder, self.target_folder, dirs_exist_ok=True)
                return True
            except Exception as e:
                self.gui_callback(f"Restore failed: {e}", "red")
        return False

    def generate_forensic_report(self):
        report = {
            "Timestamp": datetime.datetime.now().isoformat(),
            "Status": "Ransomware Detected & Suspended",
            "Final_Threat_Score": self.threat_score,
            "MITRE_ATT&CK": "T1486 - Data Encrypted for Impact",
            "Affected_Files_Count": len(self.affected_files),
            "Sample_Affected_Files": self.affected_files[:5]
        }
        report_path = os.path.join(self.target_folder, "tryguard_forensic_report.json")
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4)
            self.gui_callback(f"📄 Forensic report saved to: {report_path}", "white")
        except Exception as e:
            self.gui_callback(f"Failed to save report: {e}", "red")

# ==========================================
# 3. THE KILL SWITCH (Process Tree)
# ==========================================
def suspend_ransomware():
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any('fake_ransomware.py' in arg for arg in cmdline):
                p = psutil.Process(proc.info['pid'])
                # Suspend children first
                for child in p.children(recursive=True):
                    child.suspend()
                p.suspend() 
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

# ==========================================
# 4. THE GUI
# ==========================================
ctk.set_appearance_mode("dark")  
app = ctk.CTk(fg_color="#000000") 
app.title("TryGuard - Early Warning Agent")
app.geometry("750x650")

title = ctk.CTkLabel(app, text="TRYGUARD", font=("Consolas", 32, "bold"), text_color="#FFFFFF")
title.pack(pady=(20, 0))
subtitle = ctk.CTkLabel(app, text="Automated Ransomware Response Engine", font=("Consolas", 13), text_color="#888888")
subtitle.pack(pady=(0, 10))

# --- THE THREAT METER ---
meter_frame = ctk.CTkFrame(app, fg_color="#0A0A0A", border_width=1, border_color="#222222", corner_radius=6)
meter_frame.pack(pady=10, padx=30, fill="x")

meter_label = ctk.CTkLabel(meter_frame, text="THREAT LEVEL: SAFE", text_color="#00FF00", font=("Consolas", 14, "bold"))
meter_label.pack(pady=(10, 5))

threat_meter = ctk.CTkProgressBar(meter_frame, width=600, height=15, progress_color="#00FF00", fg_color="#222222")
threat_meter.pack(pady=(0, 15), padx=20)
threat_meter.set(0) # Start at 0

def update_meter(score):
    # Convert 0-100 score to 0.0-1.0 for the progress bar
    percentage = min(score / 100, 1.0)
    threat_meter.set(percentage)
    
    if score >= 100:
        threat_meter.configure(progress_color="#FF4444")
        meter_label.configure(text="THREAT LEVEL: CRITICAL", text_color="#FF4444")
    elif score >= 40:
        threat_meter.configure(progress_color="#FFB300")
        meter_label.configure(text="THREAT LEVEL: WARNING", text_color="#FFB300")

# Folder Selection
folder_frame = ctk.CTkFrame(app, fg_color="#0A0A0A", border_width=1, border_color="#222222", corner_radius=6)
folder_frame.pack(pady=5, padx=30, fill="x")

folder_label = ctk.CTkLabel(folder_frame, text="No target directory selected...", text_color="#666666", font=("Consolas", 12))
folder_label.pack(side="left", padx=15, pady=15)

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_label.configure(text=folder, text_color="#FFFFFF")
        add_log(f"[SYS] Target directory set: {folder}", "grey")

select_btn = ctk.CTkButton(folder_frame, text="BROWSE", command=select_folder, fg_color="#1A1A1A", hover_color="#333333", text_color="#CCCCCC", font=("Consolas", 12, "bold"), width=100, corner_radius=4)
select_btn.pack(side="right", padx=15, pady=10)

# Log Window
log_box = ctk.CTkTextbox(app, height=250, font=("Consolas", 13), fg_color="#050505", text_color="#C0C0C0", border_width=1, border_color="#222222", corner_radius=6)
log_box.pack(pady=10, padx=30, fill="both", expand=True)

log_box.tag_config("grey", foreground="#A0A0A0")
log_box.tag_config("white", foreground="#FFFFFF")
log_box.tag_config("yellow", foreground="#FFB300")
log_box.tag_config("red", foreground="#FF4444")

log_box.insert("end", "[SYS] TryGuard EDR Engine initialized. Awaiting instructions...\n", "grey")
log_box.configure(state="disabled")

def add_log(message, color="grey"):
    log_box.configure(state="normal")
    log_box.insert("end", message + "\n", color)
    log_box.see("end")
    log_box.configure(state="disabled")

observer = None
is_running = False

def start_protection():
    global observer, is_running
    
    target_path = folder_label.cget("text")
    if not target_path or target_path == "No target directory selected...":
        messagebox.showwarning("Warning", "Please select a folder to protect first!")
        return

    if not is_running:
        is_running = True
        start_btn.configure(text="STOP PROTECTION", fg_color="#1A1A1A", hover_color="#333333", text_color="#FF4444", border_width=1, border_color="#FF4444")
        
        # Reset Meter
        threat_meter.set(0)
        threat_meter.configure(progress_color="#00FF00")
        meter_label.configure(text="THREAT LEVEL: SAFE", text_color="#00FF00")

        vault_path = os.path.join(target_path, ".tryguard_vault")
        try:
            if os.path.exists(vault_path): shutil.rmtree(vault_path)
            shutil.copytree(target_path, vault_path, ignore=shutil.ignore_patterns('.tryguard_vault', '.tryguard_canary.txt'))
            add_log("[+] Recovery Vault created (Files backed up).", "white")
        except Exception as e:
            add_log(f"[!] Failed to create vault: {e}", "red")

        canary_path = os.path.join(target_path, ".tryguard_canary.txt")
        try:
            with open(canary_path, 'w') as f:
                f.write("TryGuard Canary File.")
            add_log("[+] Hidden Canary Tripwire planted successfully.", "white")
        except Exception as e:
            add_log(f"[!] Could not plant canary: {e}", "red")

        add_log(f"[+] PROTECTION ACTIVE. Monitoring initiated.", "white")
        
        event_handler = RansomwareDetector(add_log, target_path, update_meter)
        observer = Observer()
        observer.schedule(event_handler, target_path, recursive=True)
        observer.start()
        
    else:
        is_running = False
        if observer:
            observer.stop()
            observer.join()
            
            canary_path = os.path.join(target_path, ".tryguard_canary.txt")
            if os.path.exists(canary_path): os.remove(canary_path)
            
            vault_path = os.path.join(target_path, ".tryguard_vault")
            if os.path.exists(vault_path): shutil.rmtree(vault_path)
            
        start_btn.configure(text="START PROTECTION", fg_color="#222222", hover_color="#333333", text_color="#FFFFFF", border_width=0)
        add_log("\n[-] Protection stopped by user.", "grey")

start_btn = ctk.CTkButton(app, text="START PROTECTION", height=50, font=("Consolas", 16, "bold"), command=start_protection, fg_color="#222222", hover_color="#333333", text_color="#FFFFFF", corner_radius=6)
start_btn.pack(pady=(10, 20), padx=30, fill="x")

app.mainloop()
