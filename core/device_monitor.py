from PyQt5.QtCore import QThread, pyqtSignal
import time
import subprocess
from typing import Dict, Optional

class DeviceMonitor(QThread):
    device_connected = pyqtSignal(str)
    device_disconnected = pyqtSignal(str)
    device_state_changed = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.known_devices = {}
        self.retry_count = 3
        self.retry_delay = 2
        
    def run(self):
        while self.running:
            try:
                current_devices = self._get_connected_devices()
                
                # Check for new or changed devices
                for device_id, state in current_devices.items():
                    if device_id not in self.known_devices:
                        self.device_connected.emit(device_id)
                    elif self.known_devices[device_id] != state:
                        self.device_state_changed.emit(device_id, state)
                
                # Check for disconnected devices
                for device_id in list(self.known_devices.keys()):
                    if device_id not in current_devices:
                        self.device_disconnected.emit(device_id)
                        del self.known_devices[device_id]
                
                self.known_devices = current_devices
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(1)
    
    def _get_connected_devices(self) -> Dict[str, str]:
        devices = {}
        for attempt in range(self.retry_count):
            try:
                output = subprocess.check_output(["adb", "devices", "-l"]).decode()
                for line in output.split('\n')[1:]:
                    if '\t' in line:
                        device_id, state = line.split('\t')[:2]
                        devices[device_id.strip()] = state.strip()
                return devices
            except subprocess.CalledProcessError:
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                continue
        return devices

    def stop(self):
        self.running = False