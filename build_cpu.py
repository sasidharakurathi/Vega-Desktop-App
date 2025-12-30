import PyInstaller.__main__
import whisper
import os
import shutil

# SETUP
BASE_DIR = os.getcwd()
WHISPER_PATH = os.path.dirname(whisper.__file__)
ASSETS_PATH = os.path.join(WHISPER_PATH, 'assets')
CONFIG_FILE = 'vega_config.json'
sep = ';' if os.name == 'nt' else ':'

print("[-] BUILDING CPU VERSION (LIGHT)...")

if os.path.exists("backend/dist"): shutil.rmtree("backend/dist")
if os.path.exists("backend/build_cpu"): shutil.rmtree("backend/build_cpu")

PyInstaller.__main__.run([
    'backend/server.py',
    '--name=vega_engine',
    '--onedir',
    '--console',
    '--clean',
    '--noconfirm',
    f'--add-data={ASSETS_PATH}{sep}whisper/assets',
    f'--add-data={CONFIG_FILE}{sep}.',
    '--hidden-import=engineio.async_drivers.threading',
    '--collect-all=openai-whisper',
    
    # OUTPUT TO GENERIC DIST FOLDER
    '--distpath=backend/dist', 
    '--workpath=backend/build_cpu'
])

# MANUAL CONFIG COPY
try:
    # Update path here too
    shutil.copy(CONFIG_FILE, os.path.join(BASE_DIR, 'backend', 'dist', 'vega_engine', CONFIG_FILE))
    print("[-] CONFIG COPIED.")
except Exception as e:
    print(f"[!] Config Copy Failed: {e}")