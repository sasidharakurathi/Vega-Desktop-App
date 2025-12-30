import speech_recognition as sr
import pygame
import threading
import queue
import os
import json
import asyncio
import edge_tts
import io
import whisper
import numpy as np
import time
import torch

CONFIG_PATH = os.path.join(os.getcwd(), 'config.json')
VOICE_NAME = "en-US-ChristopherNeural" 
MODEL_TYPE = "small.en"

CORRECTIONS = {
    "mega": "vega",
    "vegas": "vega",
    "beggar": "vega",
    "figure": "vega",
    "vague": "vega",
    "non-work": "work",
    "start work": "work mode",
    "cleaning": "clean",
    "cleaned": "clean",
    "clear": "clean",
    "system status": "status",
    "statue": "status",
    "calculator": "calculator",
    "youtube": "youtube"
}

class NeonVoiceEngine:
    def __init__(self):
        self.config = self.load_config()
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[VEGA] -> DEVICE DETECTED: {device.upper()}")
        
        print(f"[VEGA] -> LOADING LOCAL MODEL ({MODEL_TYPE})...")
        self.model = whisper.load_model(MODEL_TYPE, device=device)
        print("[VEGA] -> MODEL LOADED. SYSTEM READY.")
        
        pygame.mixer.init()
        threading.Thread(target=self._tts_loop, daemon=True).start()

    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r') as f: return json.load(f)
        except: return {}

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
        text = text.lower().strip()
        for mistake, correct in CORRECTIONS.items():
            if mistake in text:
                text = text.replace(mistake, correct)
        return text
    
    def remove_punctuations(self, text):
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
                    
                    audio_data = r.listen(source, timeout=5)
                    
                    if self.is_speaking: return None
                    
                    print("\n[VEGA] -> PROCESSING...")
                    
                    raw_data = audio_data.get_raw_data()
                    audio_np = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0

                    keywords = self.config.get('priority_keywords', "Vega")
                    
                    result = self.model.transcribe(
                        audio_np, 
                        fp16=False, 
                        initial_prompt=keywords
                    )
                    
                    text = result['text'].strip().lower()
                    print(f"[RAW WHISPER]: {text}") 

                    text = self.sanitize_command(text)
                    print(f"[SANITIZED]: {text}")
                    
                    text = self.remove_punctuations(text)
                    print(f"[REMOVED PUNCTUATIONS]: {text}")

                    for trigger in self.config.get('wake_words', ["vega"]):
                        if trigger in text:
                            parts = text.split(trigger, 1)
                            if len(parts) > 1 and parts[1].strip():
                                return parts[1].strip()
                            return "hello" 
                    
                    return None
                    
                except Exception: return None
        except OSError:
            return None

engine_instance = NeonVoiceEngine()