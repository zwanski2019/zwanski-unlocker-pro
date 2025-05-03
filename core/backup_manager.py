import subprocess
import os
import datetime
from utils.logger import logger

class BackupManager:
    def __init__(self):
        self.backup_dir = os.path.join(os.getcwd(), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, device_id, progress_callback=None):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{device_id}_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            if progress_callback:
                progress_callback("Starting device backup...")
            
            # Create backup using adb
            cmd = ["adb", "-s", device_id, "backup", "-all", "-f", f"{backup_path}.ab"]
            subprocess.run(cmd, check=True)
            
            if progress_callback:
                progress_callback("Backup completed successfully")
            
            return {"status": "success", "path": f"{backup_path}.ab"}
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {"status": "error", "message": str(e)}

    def restore_backup(self, backup_path, device_id, progress_callback=None):
        try:
            if progress_callback:
                progress_callback("Starting backup restoration...")
            
            cmd = ["adb", "-s", device_id, "restore", backup_path]
            subprocess.run(cmd, check=True)
            
            if progress_callback:
                progress_callback("Restore completed successfully")
            
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return {"status": "error", "message": str(e)}