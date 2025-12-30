import os
import shutil
import ctypes

class SystemCleaner:
    @staticmethod
    def clean():
        deleted_files = 0
        deleted_size_mb = 0
        
        
        temp_folder = os.environ.get('TEMP')
        if temp_folder:
            for root, dirs, files in os.walk(temp_folder):
                for file in files:
                    try:
                        file_path = os.path.join(root, file)
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files += 1
                        deleted_size_mb += size
                    except: pass 
                
                for dir in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, dir))
                    except: pass

        
        try:
            ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 7)
        except: pass

        mb_cleared = round(deleted_size_mb / (1024 * 1024), 2)
        return f"SYSTEM CLEANED. REMOVED {deleted_files} FILES ({mb_cleared} MB)."