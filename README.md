# VEGA DESKTOP ASSISTANT

![Version](https://img.shields.io/badge/version-1.0.0-cyan)
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

## 🛠️ Development Setup

### Prerequisites
1. **Python 3.10+** (Ensure "Add Python to PATH" is checked during installation).
2. **Node.js & npm** (For the Electron interface).
3. **FFmpeg**: Required for audio processing.
   * *Download from [ffmpeg.org](https://ffmpeg.org/download.html), extract it, and add the `bin` folder to your System PATH.*
4. **Visual C++ Redistributable**: Required for some Python libraries to compile.

### 1. Clone the Repository
```bash
git clone https://github.com/sasidharakurathi/Vega-Desktop-App.git
cd Vega-Desktop-App
```

### 2. Python Backend Setup (Choose One)
You must choose which version you want to develop.

#### 🔴 Option A: GPU Version (Recommended for NVIDIA Users)
Uses CUDA for faster processing. Size: ~2.5GB.

```bash
# Create virtual environment
python -m venv venv_gpu

# Activate it
.\venv_gpu\Scripts\activate

# Install GPU Dependencies
pip install -r requirements_gpu.txt
```

#### 🔵 Option B: CPU Version (Lightweight / Laptop)
Uses Standard CPU processing. Size: ~200MB.

```bash
# Create virtual environment
python -m venv venv_cpu

# Activate it
.\venv_cpu\Scripts\activate

# Install CPU Dependencies
pip install -r requirements_cpu.txt
```

### 3. Frontend Setup
```bash
npm install
```

### 4. Running in Dev Mode
To test the app without building it:

1. Open `vega_config.json` and set `"ai_device": "auto"`.
2. Ensure your chosen virtual environment is active in your terminal.
3. Run:
```bash
npm start
```

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

On the first run, Vega creates a configuration file in your User Home Directory (`C:\Users\Name\vega_config.json`). You can edit this file to customize the assistant.

```json
{
    "wake_words": ["vega", "system"],
    "priority_keywords": "Vega, Open, Close, Minimize, Status",
    "mic_index": null,       // Set to a number (e.g., 1) if default mic fails
    "sensitivity": 300,      // Lower = More Sensitive (e.g., 200)
    "ai_device": "auto"      // Options: "auto", "cuda", "cpu"
}
```

---

## 🗣️ Voice Commands

| Category | Commands |
|----------|----------|
| **Core** | "Switch to GPU", "Switch to CPU", "Work Mode", "Exit System" |
| **System** | "System Status", "Clean System", "Turn on WiFi", "Mute Volume" |
| **Windows** | "Minimize Chrome", "Maximize Notepad", "Snap Left", "Close Spotify" |
| **Launch** | "Open YouTube", "Launch VS Code", "Open Settings" |
| **UI** | "Switch to Mini Mode", "Full Mode" |
| **Media** | "Play", "Pause", "Next Song" |

---

## ❓ Troubleshooting

### 1. Voice Engine Not Listening / Deaf
**Issue**: The "Reactor" spins, but it never processes text.

**Fix**: Check your microphone. Open `vega_config.json` in your User folder and try changing `mic_index` to `0`, `1`, or `2`. Also, try lowering `sensitivity` to `200`.

### 2. "Access Denied" for WiFi/System Commands
**Issue**: Vega says "WiFi disabled" but nothing happens.

**Fix**: The app needs Admin privileges to toggle hardware. Right-click the app shortcut → Run as Administrator. (The installer sets this by default, but dev mode needs manual approval).

### 3. Build Error: "Unable to commit changes"
**Issue**: `npm run dist` fails at the end.

**Fix**: 
1. Close any running instances of Vega (Check Task Manager).
2. Disable Antivirus "Real-time protection" briefly (Windows Defender often blocks the icon writer).
3. Run VS Code / Terminal as Administrator.

### 4. Error: [Errno 2] No such file ... mel_filters.npz
**Issue**: The installed app crashes immediately.

**Fix**: This means the AI assets weren't copied. Ensure you are using `npm run cpu-dist` or `npm run gpu-dist`, NOT just `electron-builder`. These scripts trigger the Python build process that fixes this path issue.

---

## 📄 License

This project is open-source. Feel free to modify and distribute.