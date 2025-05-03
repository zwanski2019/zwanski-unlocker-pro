import requests
import os
import sys
import subprocess
from packaging import version

class AutoUpdater:
    def __init__(self):
        self.current_version = "1.0.0"
        self.update_url = "https://api.example.com/updates"
        self.update_file = "update.zip"

    def check_for_updates(self):
        try:
            response = requests.get(f"{self.update_url}/version")
            latest_version = response.json()["version"]
            
            if version.parse(latest_version) > version.parse(self.current_version):
                return True, latest_version
            return False, None
        except Exception as e:
            return False, str(e)

    def download_update(self, progress_callback=None):
        try:
            response = requests.get(f"{self.update_url}/download", stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(self.update_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if progress_callback:
                        progress = (f.tell() / total_size) * 100
                        progress_callback(int(progress))
            
            return True
        except Exception:
            return False

    def install_update(self):
        try:
            # Extract and install update
            subprocess.run(["update_installer.exe", self.update_file], check=True)
            os.remove(self.update_file)
            return True
        except Exception:
            return False