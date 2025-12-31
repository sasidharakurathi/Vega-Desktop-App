# VEGA DESKTOP ASSISTANT

![Version](https://img.shields.io/badge/version-1.0.1-cyan)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-blue)
![Build](https://img.shields.io/badge/build-Electron%20%2B%20Python-green)

**Vega** is a futuristic, voice-controlled desktop assistant built with **Electron** (Frontend) and **Python** (Backend). It features a sci-fi HUD interface, purely offline speech recognition (OpenAI Whisper), and deep system automation capabilities.

Uniquely, Vega features a **Hybrid AI Engine** that allows users to switch between a high-performance **GPU Mode** (CUDA) and a battery-saving **CPU Mode** on the fly.

---

## 📥 Downloads

Select the version that matches your hardware.

| Version | Description | Hardware Req | Link |
| :--- | :--- | :--- | :--- |
| **Vega AI (GPU Edition)** | Extreme performance using NVIDIA CUDA. | NVIDIA GTX 1050 or higher | [**Download GPU Installer**](https://github.com/sasidharakurathi/Vega-Desktop-App/releases) |
| **Vega AI (CPU Edition)** | Lightweight version for laptops/non-NVIDIA PCs. | Intel i5 / AMD Ryzen 5 | [**Download CPU Installer**](https://github.com/sasidharakurathi/Vega-Desktop-App/releases) |

---

## 🌟 Key Features

### 🧠 Core Intelligence
* **Offline Privacy**: No data is sent to the cloud. All processing happens on your machine.
* **Hybrid Engine**: 
    * **GPU Mode**: Lightning-fast response times using CUDA (Requires NVIDIA GPU).
    * **CPU Mode**: Lightweight, energy-efficient mode usable on any laptop.
* **Neural Voice**: High-quality text-to-speech using **Edge-TTS**.
* **Wake Word**: Activates on "Vega", "System", or custom words.

### 💻 System Automation
* **Window Management**: Minimize, Maximize, Close, Snap (Split Screen), and Switch focus to any app.
* **Hardware Control**: Adjust Brightness, Volume, Toggle WiFi (Admin required), and Bluetooth.
* **App Launcher**: Instant access to apps and websites via Windows Search integration.
* **Self-Maintenance**: "Clean System" protocol to purge `%TEMP%` files and empty Recycle Bin.

### 🎨 Visual Interface
* **Reactive HUD**: Real-time monitoring of CPU, RAM, Disk, Network, and Battery.
* **Audio Visualizer**: A 3D atomic sphere that pulses and glows based on voice volume.
* **Dual UI Modes**:
  * **Full HUD**: Complete system telemetry.
  * **Mini Mode**: A tiny 120px floating reactor widget for minimal distraction.

---

## 🛠️ Full Development Setup (Windows)

### Prerequisites
- **Python 3.10+** (3.12 recommended for Windows). Be sure to check "Add Python to PATH".
- **Node.js & npm**.
- **FFmpeg**: install and add `ffmpeg/bin` to your PATH.
- **Visual C++ Redistributable**.

### Clone
```bash
git clone https://github.com/sasidharakurathi/Vega-Desktop-App.git
cd Vega-Desktop-App
```

### Python Environments (pick one)
Only one environment (CPU or GPU) is required.

CPU (light):
```powershell
python -m venv .\venv_cpu
.\venv_cpu\Scripts\Activate.ps1
pip install -r requirements_cpu.txt
```

GPU (NVIDIA/CUDA):
```powershell
python -m venv .\venv_gpu
.\venv_gpu\Scripts\Activate.ps1
pip install -r requirements_gpu.txt
```

> Note: Activate the chosen venv in the **same terminal** where you run `npm start` to ensure Electron spawns the correct `python` binary for dev mode.

### Frontend (Electron)
```bash
npm install
```

### Run in Dev Mode
1. Activate your venv in the terminal.
2. Run:
```bash
npm start
```

- In DEV mode, `main.js` spawns `python backend/server.py` automatically. You usually do not need to start the backend separately.
- Backend listens on `127.0.0.1:5000` (Socket.IO) and emits `stats_update`, `log_update`, and `command_recognized` events.

---

## 📦 Building the Installer (.exe)

Vega includes custom build scripts to package the correct AI engine.

### To Build the CPU (Light) Version
1. Activate your CPU environment: `.\venv_cpu\Scripts\activate`
2. Run the build command:
```bash
npm run cpu-dist
```
**Output**: The installer will be in `dist/`.

### To Build the GPU (Performance) Version
1. Activate your GPU environment: `.\venv_gpu\Scripts\activate`
2. Run the build command:
```bash
npm run gpu-dist
```
**Output**: The installer will be in `dist/`.

---

## ⚙️ Configuration (vega_config.json)

On first run Vega writes a user `vega_config.json` in your Home directory (e.g., `C:\Users\YourName\vega_config.json`). You can also edit the copy bundled with the repo (`vega_config.json`) for default values.

Sample `vega_config.json`:
```json
{
  "wake_words": ["vega", "system"],
  "priority_keywords": "Vega, Open, Close, Minimize, Status",
  "mic_index": null,
  "sensitivity": 300,
  "ai_device": "auto"
}
```
- `mic_index`: set to a number (0,1,2...) if the default microphone is wrong.
- `sensitivity`: lower = more sensitive (try 200 if detection is poor).
- `ai_device`: `"auto"`, `"cpu"` or `"cuda"`.

---

## 🗣️ Example Voice Commands (detailed)
Use short natural phrases. Below are concrete examples with expected behavior (these are implemented in `backend/server.py`):

- Modes & core control
  - "Switch to GPU" — Initialize GPU core/engine and save preference.
  - "Switch to CPU" — Switch to CPU engine and save.
  - "Work mode" — Engage productivity focused automation (e.g., mute notifications).

- UI / HUD
  - "Mini mode" / "HUD mode" — Enter compact 120px widget mode.
  - "Full mode" / "Expand mode" — Restore full HUD.

- Launch / navigation
  - "Open YouTube" — Opens YouTube in default browser.
  - "Open VS Code" — Tries to launch Visual Studio Code by name.

- Window management
  - "Minimize Chrome", "Maximize Notepad", "Close Spotify".
  - "Snap left" / "Snap right" — Window snapping.
  - "Switch to [app name]" — Attempts to change focus to application.

- System & hardware
  - "System status" — Spoken summary of CPU, memory, battery.
  - "Clean system" — Runs cleanup tasks (temp files/recycle bin).
  - "Mute volume", "Volume up", "Set brightness 50".
  - "Turn WiFi off" / "Turn WiFi on" — Requires admin privileges.
- Special / Easter Egg
  - "Protocol 2026" or "Happy New Year" — Triggers the **Protocol 2026** visual sequence and spoken countdown (emits `activate_protocol_2026` in the backend).
- Media
  - "Play" / "Pause" / "Next" / "Previous".

> Tip: If Vega doesn't recognize a phrase, try removing filler words ("please", "could you") and keep the intent short.

---

## 🔧 Running / Debugging
- Run backend only (debug logs):
```powershell
.\venv_cpu\Scripts\Activate.ps1  # or .\venv_gpu\Scripts\Activate.ps1
python backend/server.py
```
- Check Electron console/logs by running `npm start` from a terminal where the venv is active.
- If the app won't start, verify `python` is available in your PATH (the venv python should be active for dev runs) and that `backend/dist/vega_engine` exists after builds.

---

## 🧪 Packaging & Build Notes
- `build_cpu.py` / `build_gpu.py` create a PyInstaller `onedir` build at `backend/dist/vega_engine`.
- `npm run cpu-dist` and `npm run gpu-dist` both run the respective PyInstaller script and then `electron-builder` to make the Windows installer.
- If a runtime file is missing after install (e.g., `mel_filters.npz`), it usually means antivirus blocked a file during packaging — re-run packaging with Defender temporarily disabled.

---

## 🧾 Project Layout
- `main.js` — Electron entry (starts the Python backend in dev).
- `gui/` — HTML / assets / frontend JS.
- `backend/server.py` — Flask + Socket.IO + voice command routing.
- `backend/modules/` — engine components (voice, automation, launcher, window_manager, cleaner).
- `build_cpu.py` / `build_gpu.py` — PyInstaller scripts.
- `requirements_cpu.txt` / `requirements_gpu.txt` — pip dependency lists.

---

## ❓ Troubleshooting
1) Voice not listening:
- Try different `mic_index` values in `vega_config.json`.
- Reduce `sensitivity` to 200.

2) Admin / hardware commands failing:
- Run the app as Administrator (right-click -> Run as administrator).

3) Build failures / missing runtime assets:
- Close all instances of Vega.
- Disable Realtime AV while building.
- Run `npm run cpu-dist` / `gpu-dist` (these ensure the Python engine is built and included).

4) Electron errors / stuck processes:
- Check Task Manager for `python.exe` or `Vega` instances and kill them before retrying.

---

## Contributing
Please open issues for bugs or enhancement requests. PRs are welcome — keep them small and well-documented.

---

## 📄 License
Open-source. Feel free to modify and redistribute.