import os
import subprocess
import pyautogui
import time
import screen_brightness_control as sbc

class SystemAutomation:
    
    
    @staticmethod
    def control_media(action):
        action = action.lower()
        if "play" in action or "pause" in action or "stop" in action:
            pyautogui.press("playpause")
            return "TOGGLED MEDIA PLAYBACK."
        elif "next" in action or "skip" in action:
            pyautogui.press("nexttrack")
            return "SKIPPED TO NEXT TRACK."
        elif "previous" in action or "back" in action:
            pyautogui.press("prevtrack")
            pyautogui.press("prevtrack")
            return "WENT BACK TO PREVIOUS TRACK."
        return "MEDIA COMMAND UNCLEAR."

    
    @staticmethod
    def set_brightness(level):
        try:
            level = max(0, min(100, int(level)))
            sbc.set_brightness(level)
            return f"BRIGHTNESS SET TO {level}%."
        except Exception as e:
            return f"ERROR SETTING BRIGHTNESS: {str(e)}"

    
    @staticmethod
    def toggle_wifi(action):
        action = action.lower()
        try:
            
            if "on" in action or "enable" in action:
                cmd = 'powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList \'Enable-NetAdapter -Name \\"Wi-Fi\\" -Confirm:$false\'"'
                subprocess.run(cmd, shell=True, check=True)
                return "WIFI ENABLED."
            elif "off" in action or "disable" in action:
                cmd = 'powershell -Command "Start-Process powershell -Verb RunAs -ArgumentList \'Disable-NetAdapter -Name \\"Wi-Fi\\" -Confirm:$false\'"'
                subprocess.run(cmd, shell=True, check=True)
                return "WIFI DISABLED."
        except Exception as e:
            return f"WIFI ERROR: {str(e)}"

    @staticmethod
    def toggle_bluetooth(action):
        try:
            subprocess.run("start ms-settings:bluetooth", shell=True)
            return "OPENING BLUETOOTH SETTINGS."
        except Exception as e:
            return f"BLUETOOTH ERROR: {str(e)}"

    
    @staticmethod
    def engage_work_mode():
        distractions = ["discord.exe", "spotify.exe", "steam.exe"]
        for app in distractions:
            os.system(f"taskkill /f /im {app}")
        try:
            subprocess.Popen("notepad.exe")
        except: pass
        return "WORK MODE ENGAGED."

    @staticmethod
    def set_volume(action):
        if action == "mute":
            pyautogui.press("volumemute")
            return "AUDIO MUTED."
        elif action == "unmute":
            pyautogui.press("volumemute")
            return "AUDIO RESTORED."
        elif action == "up":
            for _ in range(5): pyautogui.press("volumeup")
            return "VOLUME INCREASED."
        elif action == "down":
            for _ in range(5): pyautogui.press("volumedown")
            return "VOLUME DECREASED."
        return "VOLUME ADJUSTED."

    @staticmethod
    def take_screenshot():
        filename = f"screenshot_{int(time.time())}.png"
        pyautogui.screenshot(filename)
        return f"SCREENSHOT SAVED."