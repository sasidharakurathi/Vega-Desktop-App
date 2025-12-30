import pygetwindow as gw
import pyautogui
import time

class WindowManager:
    
    @staticmethod
    def _find_window(app_name):
        app_name = app_name.lower().strip()
        windows = gw.getAllWindows()
        
        for win in windows:
            title = win.title.lower()
            if title == "": continue 
            
            if app_name in title:
                return win
        return None

    @staticmethod
    def close_window(app_name):
        win = WindowManager._find_window(app_name)
        if win:
            try:
                win.close()
                return f"CLOSED {app_name.upper()}."
            except Exception as e:
                return f"ERROR CLOSING {app_name.upper()}."
        return f"CANNOT FIND WINDOW: {app_name.upper()}"

    @staticmethod
    def minimize_window(app_name):
        win = WindowManager._find_window(app_name)
        if win:
            if win.isMinimized: 
                return f"{app_name} IS ALREADY MINIMIZED."
            try:
                win.minimize()
                return f"MINIMIZED {app_name.upper()}."
            except: 
                return f"ERROR MINIMIZING {app_name.upper()}."
        return f"CANNOT FIND WINDOW: {app_name.upper()}"

    @staticmethod
    def maximize_window(app_name):
        win = WindowManager._find_window(app_name)
        if win:
            if win.isMaximized:
                return f"{app_name} IS ALREADY MAXIMIZED."
            try:
                win.maximize()
                return f"MAXIMIZED {app_name.upper()}."
            except:
                return f"ERROR MAXIMIZING {app_name.upper()}."
        return f"CANNOT FIND WINDOW: {app_name.upper()}"

    @staticmethod
    def switch_focus(app_name):
        win = WindowManager._find_window(app_name)
        if win:
            try:
                if win.isMinimized:
                    win.restore()
                win.activate()
                return f"SWITCHED TO {app_name.upper()}."
            except:
                try:
                    win.minimize()
                    win.restore()
                    return f"FORCED FOCUS ON {app_name.upper()}."
                except:
                    return f"ERROR SWITCHING FOCUS."
        return f"CANNOT FIND WINDOW: {app_name.upper()}"

    @staticmethod
    def snap_window(direction):
        direction = direction.lower()
        if "left" in direction:
            pyautogui.hotkey('win', 'left')
            return "SNAPPED LEFT."
        elif "right" in direction:
            pyautogui.hotkey('win', 'right')
            return "SNAPPED RIGHT."
        elif "up" in direction or "top" in direction:
            pyautogui.hotkey('win', 'up')
            return "SNAPPED UP."
        elif "down" in direction or "bottom" in direction:
            pyautogui.hotkey('win', 'down')
            return "SNAPPED DOWN."
        return "UNKNOWN DIRECTION."