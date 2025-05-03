import subprocess
import os
from datetime import datetime

class ScreenshotManager:
    def __init__(self):
        self.screenshot_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def take_screenshot(self, device_id):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{device_id}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            # Take screenshot using adb
            subprocess.run(["adb", "-s", device_id, "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
            subprocess.run(["adb", "-s", device_id, "pull", "/sdcard/screen.png", filepath], check=True)
            subprocess.run(["adb", "-s", device_id, "shell", "rm", "/sdcard/screen.png"], check=True)
            
            return {"status": "success", "path": filepath}
        except Exception as e:
            return {"status": "error", "message": str(e)}