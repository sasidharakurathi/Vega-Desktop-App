import speech_recognition as sr
import pygame
import threading
import queue
import os
import sys # Added sys
import json
import asyncio
import edge_tts
import io
import whisper
import numpy as np
import time
import torch
import shutil

# --- CONFIGURATION PATHS ---
CONFIG_FILENAME = 'vega_config.json'
USER_CONFIG_PATH = os.path.join(os.path.expanduser("~"), CONFIG_FILENAME)

# Fallback path (Local folder or bundled exe folder)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.getcwd()
BUNDLED_CONFIG_PATH = os.path.join(BASE_DIR, 'vega_config.json')

VOICE_NAME = "en-US-ChristopherNeural" 
MODEL_TYPE = "small.en"

CORRECTIONS = {
    "mega": "vega", "vegas": "vega", "beggar": "vega", "figure": "vega", "vague": "vega",
    "non-work": "work", "start work": "work mode", "cleaning": "clean", "cleaned": "clean", "clear": "clean",
    "system status": "status", "statue": "status", "calculator": "calculator", "youtube": "youtube"
}

class VegaVoiceEngine:
    def __init__(self):
        self.config = self.load_server_config()
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.socketio = None # Placeholder for socket reference
        
        preferred_device = self.config.get('ai_device', 'auto')
        
        if preferred_device == "cuda" and torch.cuda.is_available():
            self.current_device = "cuda"
        elif preferred_device == "cpu":
            self.current_device = "cpu"
        else:
            # Default 'auto' behavior
            self.current_device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f"[VEGA] -> DEVICE DETECTED: {self.current_device.upper()}")
        
        print(f"[VEGA] -> LOADING LOCAL MODEL ({MODEL_TYPE})...")
        self.model = whisper.load_model(MODEL_TYPE, device=self.current_device)
        print("[VEGA] -> MODEL LOADED. SYSTEM READY.")
        
        pygame.mixer.init()
        threading.Thread(target=self._tts_loop, daemon=True).start()

    def set_socket(self, socket):
        self.socketio = socket

    def load_server_config(self):
        # 1. Check if User Config exists (C:\Users\Name\vega_config.json)
        if os.path.exists(USER_CONFIG_PATH):
            try:
                with open(USER_CONFIG_PATH, 'r') as f: 
                    print(f"[CONFIG] Loaded User Config: {USER_CONFIG_PATH}")
                    return json.load(f)
            except: 
                print("[CONFIG] Error reading User Config")

        # 2. If User Config is MISSING, try to Copy from Bundled (First Run)
        if os.path.exists(BUNDLED_CONFIG_PATH):
            try:
                print(f"[CONFIG] First Run Detected. Copying defaults to: {USER_CONFIG_PATH}")
                shutil.copy(BUNDLED_CONFIG_PATH, USER_CONFIG_PATH)
                
                # Now load the newly created file
                with open(USER_CONFIG_PATH, 'r') as f: return json.load(f)
            except Exception as e:
                print(f"[CONFIG] Failed to copy config: {e}")
                # If copy fails, just load the bundled one directly
                with open(BUNDLED_CONFIG_PATH, 'r') as f: return json.load(f)

        # 3. Total Fallback (Should not happen if build is correct)
        print("[CONFIG] No config found. Using Hardcoded Defaults.")
        return {
            "wake_words": ["vega", "system"],
            "priority_keywords": "Vega, Open, Close",
            "mic_index": None,
            "sensitivity": 300
        }

    # --- NEW METHOD REQUESTED ---
    def reload_config(self, new_data=None):
        if new_data:
            self.config = new_data
        else:
            self.config = self.load_server_config()
        print("[VEGA] -> VOICE ENGINE CONFIG UPDATED")
        
    def load_model(self, device):
        print(f"[VEGA] -> LOADING MODEL ON: {device.upper()}...")
        try:
            # Unload old model if exists to free RAM/VRAM
            if hasattr(self, 'model'): 
                del self.model
                if device == "cuda": torch.cuda.empty_cache()
            
            self.model = whisper.load_model(MODEL_TYPE, device=device)
            self.current_device = device
            print(f"[VEGA] -> SWITCHED TO {device.upper()}. SYSTEM READY.")
            if self.socketio:
                self.socketio.emit('log_update', {'log': f"[SYS] -> AI CORE SWITCHED TO {device.upper()}"})
        except Exception as e:
            print(f"[ERROR] FAILED TO LOAD ON {device}: {e}")
            # Fallback to CPU if CUDA fails
            if device == "cuda":
                print("[VEGA] -> FALLING BACK TO CPU")
                self.load_model("cpu")

    def switch_device_mode(self, mode):
        # Mode can be "gpu" or "cpu"
        new_device = None
        
        if mode == "gpu":
            if torch.cuda.is_available():
                new_device = "cuda"
            else:
                return "GPU not detected on this system."
        elif mode == "cpu":
            new_device = "cpu"

        if new_device:
            if new_device == self.current_device:
                return f"Already running on {new_device.upper()}."
            
            self.load_model(new_device)
            
            # Update memory config (Server will handle saving to disk)
            self.config['ai_device'] = new_device 
            return f"Switched to {new_device.upper()} mode."
            
        return "Unknown mode."

    async def _generate_audio_memory(self, text):
        communicate = edge_tts.Communicate(text, VOICE_NAME)
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
        return audio_data

    def _tts_loop(self):
        while True:
            try:
                text = self.speech_queue.get()
                if text is None: break 

                self.is_speaking = True
                print(f"[VEGA SPEAK]: {text}")

                mp3_bytes = asyncio.run(self._generate_audio_memory(text))
                mem_file = io.BytesIO(mp3_bytes)

                pygame.mixer.music.load(mem_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                self.is_speaking = False
                pygame.mixer.music.unload()
                self.speech_queue.task_done()

            except Exception as e:
                print(f"[TTS ERROR]: {e}")
                self.is_speaking = False

    def speak(self, text):
        self.speech_queue.put(text)

    def sanitize_command(self, text):
        return text.replace(",", "").replace(".", "").replace("?", "").replace("!", "").strip()

    def listen(self):
        if self.is_speaking:
            time.sleep(0.5) 
            return None

        r = sr.Recognizer()
        r.energy_threshold = self.config.get('sensitivity', 300)
        r.dynamic_energy_threshold = True 
        r.pause_threshold = 1.2
        r.non_speaking_duration = 0.4

        try:
            mic_index = self.config.get('mic_index')
            with sr.Microphone(device_index=mic_index, sample_rate=16000) as source:
                
                print("[VEGA] -> LISTENING...", end="\r") 
                
                try:
                    # Capture Audio
                    audio_data = r.listen(source, timeout=5)
                    
                    if self.is_speaking: return None
                    
                    # --- MANUAL VISUALIZER DATA EMIT ---
                    if self.socketio:
                        # Calculate rough volume for the visualizer "pulse" effect
                        # We use a snippet of the raw data to estimate volume
                        raw_chunk = audio_data.frame_data[:2048] # Just take a sample
                        import audioop
                        rms = audioop.rms(raw_chunk, 2)
                        level = min(100, int(rms / 50))
                        self.socketio.emit('audio_level', {'level': level})

                    print("\n[VEGA] -> PROCESSING...")
                    
                    raw_data = audio_data.get_raw_data()
                    audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0

                    keywords = self.config.get('priority_keywords', "Vega")
                    
                    try:
                        result = self.model.transcribe(
                            audio_np, 
                            fp16=False, 
                            initial_prompt=keywords
                        )
                        text = result['text'].strip().lower()
                        print(f"[RAW WHISPER]: {text}") 
                    except Exception as e:
                        print(f"[WHISPER ERROR]: {e}")
                        return None 

                    text = self.sanitize_command(text)
                    print(f"[SANITIZED TEXT]: {text}") 

                    for trigger in self.config.get('wake_words', ["vega"]):
                        if trigger in text:
                            parts = text.split(trigger, 1)
                            if len(parts) > 1 and parts[1].strip():
                                return parts[1].strip()
                            print("teststsfdfsdf")
                            return "hello" 
                    
                    return None
                    
                except Exception: return None
        except OSError:
            return None

engine_instance = VegaVoiceEngine()