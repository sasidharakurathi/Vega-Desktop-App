import pyautogui
import time
import webbrowser

class AppLauncher:
    @staticmethod
    def launch_app(app_name):
        try:
            pyautogui.press('win')
            time.sleep(0.3)
            pyautogui.write(app_name, interval=0.01)
            time.sleep(1.0)
            pyautogui.press('enter')
            return f"SEARCHING WINDOWS FOR: {app_name.upper()}"
        except Exception as e:
            return f"ERROR LAUNCHING APP: {str(e)}"

    @staticmethod
    def open_website(site_name):
        site_name = site_name.lower()
        if "youtube" in site_name: webbrowser.open("https://www.youtube.com")
        elif "google" in site_name: webbrowser.open("https://www.google.com")
        elif "github" in site_name: webbrowser.open("https://github.com")
        else: 
            webbrowser.open(f"https://www.google.com/search?q={site_name}")
            return f"SEARCHING GOOGLE FOR {site_name.upper()}."
        return "WEBSITE OPENED."