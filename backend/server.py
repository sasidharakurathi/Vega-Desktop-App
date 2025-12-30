import threading
import time
import psutil
import json
import os
import sys # Added sys
import re
import speech_recognition as sr
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# --- NEW IMPORTS ---
from modules.voice import engine_instance as voice 
from modules.cleaner import SystemCleaner
from modules.launcher import AppLauncher
from modules.automation import SystemAutomation
from modules.window_manager import WindowManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vega_secret'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# LINK VOICE TO SOCKET
voice.set_socket(socketio)

latest_log = "[SYSTEM STARTUP] -> WEBSOCKETS INITIALIZED"
last_command = "WAITING..."

# --- CONFIGURATION PATHS ---
CONFIG_FILENAME = 'vega_config.json'
USER_CONFIG_PATH = os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)

# Determine bundled config path (for fallback/defaults)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.getcwd()
BUNDLED_CONFIG_PATH = os.path.join(BASE_DIR, 'vega_config.json')

def load_server_config():
    # 1. Try User Config
    if os.path.exists(USER_CONFIG_PATH):
        try:
            with open(USER_CONFIG_PATH, 'r') as f: return json.load(f)
        except: pass
    
    # 2. Try Bundled Config
    if os.path.exists(BUNDLED_CONFIG_PATH):
        try:
            with open(BUNDLED_CONFIG_PATH, 'r') as f: return json.load(f)
        except: pass
        
    # 3. Default Fallback
    return {
        "wake_words": ["vega"],
        "priority_keywords": "Vega, Open, Close",
        "mic_index": None,
        "sensitivity": 300
    }

class ProcessMonitor:
    def __init__(self):
        self.procs = {}
        self.cpu_count = psutil.cpu_count() or 1

    def get_top_cpu_procs(self, limit=5):
        for p in psutil.process_iter(['pid', 'name']):
            try:
                if p.pid not in self.procs:
                    p.cpu_percent() 
                    self.procs[p.pid] = p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        dead_pids = [pid for pid, p in self.procs.items() if not p.is_running() or "system idle pro" in p.name().lower()]
        for pid in dead_pids: del self.procs[pid]

        results = []
        for pid, p in self.procs.items():
            try:
                cpu_raw = p.cpu_percent()
                cpu_normalized = cpu_raw / self.cpu_count
                mem = p.memory_percent()
                results.append({"pid": pid, "name": p.name(), "cpu_percent": cpu_normalized, "memory_percent": mem})
            except: pass
        
        return sorted(results, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

proc_mon = ProcessMonitor()

def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    bat_percent = battery.percent if battery else 100
    try:
        disk = psutil.disk_usage(os.path.abspath(os.sep))
        disk_percent = disk.percent
    except: disk_percent = 0
    top_procs = proc_mon.get_top_cpu_procs(10)
    net_io = psutil.net_io_counters()
    
    return {
        "cpu_load": cpu,
        "ram_usage": f"{round(ram.used / (1024**3), 1)} / {round(ram.total / (1024**3), 0)} GB",
        "ram_percent": ram.percent,
        "battery_level": bat_percent,
        "disk_usage": disk_percent,
        "active_processes": top_procs,
        "net_sent": f"{net_io.bytes_sent / (1024**3):.2f} GB",
        "net_recv": f"{net_io.bytes_recv / (1024**3):.2f} GB",
        "voice_active": voice.is_speaking,
        "last_command": last_command
    }

def background_stats_pusher():
    last_net = psutil.net_io_counters()
    while True:
        time.sleep(1)
        curr_net = psutil.net_io_counters()
        sent_bytes = curr_net.bytes_sent - last_net.bytes_sent
        recv_bytes = curr_net.bytes_recv - last_net.bytes_recv
        last_net = curr_net
        total_speed_kb = (sent_bytes + recv_bytes) / 1024
        net_percent = min((total_speed_kb / 5120) * 100, 100)
        
        stats = get_system_stats()
        stats['net_speed_kb'] = f"{total_speed_kb:.1f} KB/s"
        stats['net_percent'] = net_percent
        
        socketio.emit('stats_update', stats)
        socketio.emit('log_update', {"log": latest_log}) 
        
def save_current_config():
    """Helper to save the current in-memory voice config to disk"""
    try:
        # Get the updated config from the voice engine
        current_data = voice.config 
        
        with open(USER_CONFIG_PATH, 'w') as f:
            json.dump(current_data, f, indent=4)
            
        print(f"[CONFIG] Auto-saved device preference: {current_data.get('ai_device')}")
    except Exception as e:
        print(f"[ERROR] Failed to auto-save config: {e}")

def background_voice_listener():
    global last_command, latest_log
    print("[NEON] -> VOICE LOOP STARTED")
    voice.speak("System Online.")
    
    while True:
        raw_input = voice.listen()

        if raw_input:
            user_input = raw_input.replace(",", "").replace(".", "").replace("?", "").replace("!", "").strip()
            last_command = user_input.upper()
            latest_log = f"[USER] -> {last_command}"
            socketio.emit('command_recognized', {"command": last_command})
            socketio.emit('log_update', {"log": latest_log})
            
            if raw_input == "hello":
                voice.speak("Greetings. Awaiting command.")
                
            # --- COMMAND LOGIC ---
            elif "hud mode" in user_input or "mini mode" in user_input:
                voice.speak("Entering compact mode.")
                socketio.emit('toggle_hud_mode', {"state": True})
                latest_log = "[SYS] -> HUD MODE ACTIVE"

            elif "full mode" in user_input or "expand mode" in user_input:
                voice.speak("Restoring interface.")
                socketio.emit('toggle_hud_mode', {"state": False})
                latest_log = "[SYS] -> INTERFACE RESTORED"

            elif "open" in user_input or "launch" in user_input:
                target = user_input.replace("open", "").replace("launch", "")
                import re
                junk_words = ["can", "you", "please", "could", "me", "the", "my", "app"]
                for junk in junk_words:
                    pattern = r'\b' + re.escape(junk) + r'\b'
                    target = re.sub(pattern, '', target)
                target = target.strip()
                
                if target in ["youtube", "google", "github"]:
                    voice.speak(f"Opening {target}.")
                    msg = AppLauncher.open_website(target)
                elif target:
                    voice.speak(f"Opening {target}.")
                    msg = AppLauncher.launch_app(target)
                else: msg = "APP NAME NOT SPECIFIED."
                latest_log = f"[VEGA] -> {msg}"

            elif "volume" in user_input or "mute" in user_input:
                if "mute" in user_input or "silent" in user_input:
                    msg = SystemAutomation.set_volume("mute")
                    voice.speak("Muting audio.")
                elif "unmute" in user_input:
                    msg = SystemAutomation.set_volume("unmute")
                    voice.speak("Audio restored.")
                elif "up" in user_input or "increase" in user_input:
                    msg = SystemAutomation.set_volume("up")
                    voice.speak("Volume up.")
                elif "down" in user_input or "decrease" in user_input:
                    msg = SystemAutomation.set_volume("down")
                    voice.speak("Volume down.")
                else: msg = "VOLUME COMMAND UNCLEAR."
                latest_log = f"[VEGA] -> {msg}"

            elif "screenshot" in user_input or "capture" in user_input:
                voice.speak("Taking screenshot.")
                msg = SystemAutomation.take_screenshot()
                latest_log = f"[VEGA] -> {msg}"

            elif "work" in user_input: 
                voice.speak("Engaging Work Mode.")
                res = SystemAutomation.engage_work_mode()
                latest_log = f"[VEGA] -> {res}"

            elif "clean" in user_input:
                voice.speak("Scanning system files.")
                res = SystemCleaner.clean()
                voice.speak(res) 
                latest_log = f"[VEGA] -> {res}"

            elif "status" in user_input:
                 cpu = psutil.cpu_percent(interval=0.5)
                 ram = psutil.virtual_memory()
                 battery = psutil.sensors_battery()
                 report = f"Systems operational. CPU load is {cpu} percent. Memory usage is {ram.percent} percent. "
                 if battery: report += f"Battery level is {battery.percent} percent."
                 voice.speak(report)
                 latest_log = f"[VEGA] -> {report}"

            elif "exit" in user_input or "stop system" in user_input:
                voice.speak("Terminating system.")
                time.sleep(3) 
                socketio.emit('system_shutdown')
                time.sleep(1)
                os._exit(0)
                
            elif "minimize" in user_input or "maximize" in user_input or "switch to" in user_input:
                target = user_input.replace("minimize", "").replace("maximize", "").replace("switch to", "")
                junk = ["vega", "window", "the", "app", "please", "can", "you", "current", "active"]
                for j in junk: target = target.replace(j, "")
                target = target.strip()
                if "minimize" in user_input: msg = WindowManager.minimize_window(target)
                elif "maximize" in user_input: msg = WindowManager.maximize_window(target)
                elif "switch to" in user_input: msg = WindowManager.switch_focus(target)
                voice.speak(msg)
                latest_log = f"[VEGA] -> {msg}"

            elif "snap" in user_input:
                if "left" in user_input: msg = WindowManager.snap_window("left")
                elif "right" in user_input: msg = WindowManager.snap_window("right")
                elif "up" in user_input: msg = WindowManager.snap_window("up")
                elif "down" in user_input: msg = WindowManager.snap_window("down")
                else: msg = "SNAP DIRECTION UNCLEAR."
                voice.speak(msg)
                latest_log = f"[VEGA] -> {msg}"
            
            elif "close" in user_input:
                target = user_input.replace("close", "")
                junk = ["vega", "window", "the", "app", "please", "can", "you"]
                for j in junk: target = target.replace(j, "")
                target = target.strip()
                if target: msg = WindowManager.close_window(target)
                else: msg = "I DON'T KNOW WHAT TO CLOSE."
                voice.speak(msg)
                latest_log = f"[VEGA] -> {msg}"
            
            elif "brightness" in user_input or "dim" in user_input or "brighten" in user_input:
                import re
                numbers = re.findall(r'\d+', user_input)
                if numbers:
                    level = int(numbers[0])
                    msg = SystemAutomation.set_brightness(level)
                else:
                    if "dim" in user_input: msg = SystemAutomation.set_brightness(30)
                    elif "brighten" in user_input or "max" in user_input: msg = SystemAutomation.set_brightness(100)
                    else: msg = "PLEASE SPECIFY A BRIGHTNESS LEVEL."
                voice.speak(msg)
                latest_log = f"[VEGA] -> {msg}"

            elif "wifi" in user_input:
                if "on" in user_input or "enable" in user_input:
                    voice.speak("Enabling Wi-Fi.")
                    msg = SystemAutomation.toggle_wifi("on")
                elif "off" in user_input or "disable" in user_input:
                    voice.speak("Disabling Wi-Fi.")
                    msg = SystemAutomation.toggle_wifi("off")
                else: msg = "DO YOU WANT WIFI ON OR OFF?"
                latest_log = f"[VEGA] -> {msg}"

            elif "bluetooth" in user_input:
                voice.speak("Opening Bluetooth settings.")
                msg = SystemAutomation.toggle_bluetooth("open")
                latest_log = f"[VEGA] -> {msg}"
                
            elif "play" in user_input or "pause" in user_input or "next" in user_input or "previous" in user_input:
                if "next" in user_input or "skip" in user_input:
                    msg = SystemAutomation.control_media("next")
                    voice.speak("Skipping track.")
                elif "previous" in user_input or "back" in user_input:
                    msg = SystemAutomation.control_media("previous")
                    voice.speak("Previous track.")
                elif "play" in user_input or "pause" in user_input:
                    msg = SystemAutomation.control_media("play")
                latest_log = f"[VEGA] -> {msg}"
                
            elif "switch to gpu" in user_input or "gpu mode" in user_input:
                voice.speak("Initializing GPU core.")
                msg = voice.switch_device_mode("gpu")
                
                # SAVE THE PREFERENCE TO DISK
                if "Switched" in msg:
                    save_current_config() # <--- Helper function we will create below
                    
                voice.speak(msg)
                latest_log = f"[SYS] -> {msg}"

            elif "switch to cpu" in user_input or "cpu mode" in user_input:
                voice.speak("Switching to CPU core.")
                msg = voice.switch_device_mode("cpu")
                
                # SAVE THE PREFERENCE TO DISK
                if "Switched" in msg:
                    save_current_config() # <--- Helper function we will create below
                    
                voice.speak(msg)
                latest_log = f"[SYS] -> {msg}"
                
            socketio.emit('log_update', {"log": latest_log})
            time.sleep(0.5)

@socketio.on('connect')
def handle_connect():
    emit('log_update', {"log": "[NET] -> UI CONNECTED SUCCESSFULLY"})

@socketio.on('get_settings')
def handle_get_settings():
    mics = sr.Microphone.list_microphone_names()
    mic_list = [{"index": i, "name": m} for i, m in enumerate(mics)]
    config = load_server_config()
    emit('settings_data', {"config": config, "mics": mic_list})

@socketio.on('save_settings')
def handle_save_settings(data):
    global latest_log
    try:
        # Save to User Home Directory (Persist across updates)
        with open(USER_CONFIG_PATH, 'w') as f: json.dump(data, f, indent=4)
        
        # Hot-Reload Voice Engine
        voice.reload_config(data)
        
        latest_log = "[SYS] -> CONFIGURATION UPDATED"
        emit('log_update', {"log": latest_log})
        voice.speak("Configuration saved.")
    except Exception as e:
        latest_log = f"[ERROR] -> SAVE FAILED: {str(e)}"

@socketio.on('trigger_command')
def handle_ui_command(data):
    global latest_log
    cmd_id = data.get('id')
    if cmd_id == "work_mode":
        voice.speak("Work mode active.")
        msg = SystemAutomation.engage_work_mode()
        latest_log = f"[BUTTON] -> {msg}"
    elif cmd_id == "clean_system":
        voice.speak("Cleaning.")
        msg = SystemCleaner.clean()
        latest_log = f"[BUTTON] -> {msg}"
    emit('log_update', {"log": latest_log})

if __name__ == '__main__':
    threading.Thread(target=background_stats_pusher, daemon=True).start()
    threading.Thread(target=background_voice_listener, daemon=True).start()
    socketio.run(app, host='127.0.0.1', port=5000, allow_unsafe_werkzeug=True)