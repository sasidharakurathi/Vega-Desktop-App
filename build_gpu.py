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

print("[-] BUILDING GPU VERSION (HEAVY)...")

if os.path.exists("backend/dist"): shutil.rmtree("backend/dist")
if os.path.exists("backend/build_gpu"): shutil.rmtree("backend/build_gpu")

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
    '--collect-all=torch', 
    
    # OUTPUT TO GENERIC DIST FOLDER
    '--distpath=backend/dist', 
    '--workpath=backend/build_gpu'
])

# MANUAL CONFIG COPY
try:
    shutil.copy(CONFIG_FILE, os.path.join(BASE_DIR, 'backend', 'dist', 'vega_engine', CONFIG_FILE))
    print("[-] CONFIG COPIED.")
except Exception as e:
    print(f"[!] Config Copy Failed: {e}")