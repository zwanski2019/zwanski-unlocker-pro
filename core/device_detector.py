import subprocess
import re
import time
import os  # Add this import
from typing import List, Dict, Optional
from utils.logger import logger
from .device_rules import DeviceRules

class DeviceDetector:
    def __init__(self):
        self.adb_path = self._find_binary("adb.exe")
        self.fastboot_path = self._find_binary("fastboot.exe")
        self.known_states = ["device", "recovery", "bootloader", "sideload"]
        self.max_retries = 3
        self.retry_delay = 1

    def _find_binary(self, binary_name):
        """Find ADB or Fastboot binary in common locations"""
        search_paths = [
            os.path.join(os.path.dirname(__file__), "..", "platform-tools"),
            os.path.join(os.path.dirname(__file__), "binaries"),
            os.path.join(os.getenv("LOCALAPPDATA"), "Android", "Sdk", "platform-tools"),
            os.path.join(os.getenv("PROGRAMFILES"), "Android", "android-sdk", "platform-tools"),
        ]
        
        for path in search_paths:
            binary_path = os.path.join(path, binary_name)
            if os.path.isfile(binary_path):
                return binary_path
                
        # If not found, return just the binary name (will use system PATH)
        return binary_name

    def detect_devices(self) -> List[Dict[str, str]]:
        for attempt in range(self.max_retries):
            try:
                devices = self._try_detect_devices()
                if devices:
                    return devices
            except Exception as e:
                logger.error(f"Detection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
        return []

    def _try_detect_devices(self) -> List[Dict[str, str]]:
        devices = []
        
        # Check ADB devices
        try:
            output = subprocess.check_output([self.adb_path, "devices", "-l"]).decode()
            for line in output.split('\n')[1:]:
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 2:
                    device_id = parts[0]
                    state = parts[1]
                    
                    if state in self.known_states:
                        device_info = self.get_device_info(device_id, state)
                        if device_info:
                            devices.append(device_info)
        except Exception as e:
            logger.error(f"ADB detection error: {e}")

        # Check Fastboot devices
        try:
            output = subprocess.check_output([self.fastboot_path, "devices"]).decode()
            for line in output.split('\n'):
                if not line.strip():
                    continue
                    
                parts = line.split()
                if len(parts) >= 1:
                    device_id = parts[0]
                    devices.append({
                        "id": device_id,
                        "state": "fastboot",
                        "type": "unknown",
                        "model": "unknown"
                    })
        except Exception as e:
            logger.error(f"Fastboot detection error: {e}")

        return devices

    def get_device_info(self, device_id: str, state: str) -> Optional[Dict[str, str]]:
        try:
            if state == "device":
                cmd = [self.adb_path, "-s", device_id, "shell", "getprop"]
                output = subprocess.check_output(cmd).decode()
                
                model = re.search(r'\[ro\.product\.model\]:\s*\[(.*?)\]', output)
                brand = re.search(r'\[ro\.product\.brand\]:\s*\[(.*?)\]', output)
                
                model_id = model.group(1) if model else "unknown"
                device_rules = DeviceRules.identify_device(model_id)
                
                return {
                    "id": device_id,
                    "state": state,
                    "model": model_id,
                    "brand": brand.group(1) if brand else "unknown",
                    "manufacturer": device_rules["manufacturer"],
                    "series": device_rules["series"],
                    "security_level": device_rules["security_level"],
                    "frp_method": device_rules["frp_method"]
                }
            else:
                return {
                    "id": device_id,
                    "state": state,
                    "model": "unknown",
                    "type": "unknown"
                }
        except Exception as e:
            logger.error(f"Failed to get device info: {e}")
            return None

    def wait_for_device(self, device_id: str = None, timeout: int = 30) -> bool:
        try:
            cmd = [self.adb_path]
            if device_id:
                cmd.extend(["-s", device_id])
            cmd.append("wait-for-device")
            
            process = subprocess.Popen(cmd)
            process.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            logger.error(f"Wait for device failed: {e}")
            return False

    def is_device_connected(self, device_id: str) -> bool:
        devices = self.detect_devices()
        return any(device["id"] == device_id for device in devices)


# Create a singleton instance
detector = DeviceDetector()

# Export the detect_devices function
def detect_devices() -> List[Dict[str, str]]:
    return detector.detect_devices()

