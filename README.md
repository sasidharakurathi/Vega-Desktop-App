# VEGA DESKTOP ASSISTANT

![Version](https://img.shields.io/badge/version-1.0.0-cyan)
![Platform](https://img.shields.io/badge/platform-Windows-blue)

**Vega** is a futuristic, voice-controlled desktop assistant built with **Electron** (Frontend) and **Python** (Backend). It features a sci-fi HUD interface, local offline speech recognition, and deep system automation capabilities.

---

## 🌟 Features

### 🧠 Core Intelligence

* **Local Speech Recognition**: Uses OpenAI's **Whisper (Small.en)** model running locally for privacy and speed.
* **Neural Voice**: High-quality text-to-speech using **Edge-TTS**.
* **Wake Word Detection**: Activates on "Vega" (configurable).

### 💻 System Automation

* **Window Management**: Minimize, Maximize, Close, Snap (Split Screen), and Switch focus to any open app.
* **Hardware Control**: Adjust Brightness, Volume, Toggle WiFi (Admin required), and Media Controls.
* **App Launcher**: Instant access to apps and websites via Windows Search integration.
* **Maintenance**: "Clean System" protocol to purge `%TEMP%` files and empty the Recycle Bin.

### 🎨 Visual Interface

* **Reactive HUD**: Real-time CPU, RAM, Disk, and Network monitoring.
* **Audio Visualizer**: A 3D atomic sphere that reacts to your voice volume in real-time.
* **Dual Modes**:
  * **Full HUD**: Complete system telemetry.
  * **Mini Mode**: A 120px floating widget for minimal distraction.

---

## 🛠️ Installation

### Prerequisites

* **Python 3.10+**
* **Node.js & npm**
* **FFmpeg** (Required for audio processing)

### 1. Clone the Repository
```bash
git clone https://github.com/sasidharakurathi/Vega-Desktop-App.git
cd Vega-Desktop-App
```

### 2. Setup Backend (Python)

It is recommended to use a virtual environment.
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Setup Frontend (Electron)
```bash
npm install
```

### 4. Configuration

Create a `config.json` file in the root directory (or rename `config.example.json`):
```json
{
  "wake_words": ["vega", "hey vega"],
  "mic_index": 1,
  "priority_keywords": "Vega, Open, Close, Minimize, Status",
  "sensitivity": 300
}
```

---

## 🚀 Usage

Start the application (starts both Python backend and Electron window):
```bash
npm start
```

---

## 🗣️ Voice Commands Checklist

| Category | Commands |
|----------|----------|
| **System** | "System Status", "Clean System", "Work Mode", "Exit System" |
| **Windows** | "Minimize Chrome", "Maximize Notepad", "Snap Left", "Close Spotify" |
| **Launch** | "Open YouTube", "Launch VS Code", "Open Settings" |
| **Hardware** | "Set brightness to 50%", "Turn off WiFi", "Mute Volume" |
| **Media** | "Play", "Pause", "Next Song" |
| **UI** | "Switch to Mini Mode", "Full Mode" |

---

## 📂 Project Structure
```
backend/          Python Flask server & logic modules
  server.py       Main entry point & WebSocket handler
  modules/        Logic for Voice, Automation, and Windows API
gui/              HTML/CSS/JS for the Electron interface
main.js           Electron main process
preload.js        Electron preload process
```

---

## 📄 License

This project is open-source. Feel free to modify and distribute.