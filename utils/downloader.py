import requests
import os
from utils.logger import logger

def download_tool(tool_name: str, url: str, dest_folder: str = "tools") -> str:
    """
    Download an external tool (zip or exe) for flashing/unlocking.
    Returns the local file path.
    """
    os.makedirs(dest_folder, exist_ok=True)
    local_path = os.path.join(dest_folder, f"{tool_name}{os.path.splitext(url)[1]}")
    logger.info(f"Downloading {tool_name} from {url} …")
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Saved to {local_path}")
        return local_path
    except Exception as e:
        logger.error(f"Failed to download {tool_name}: {e}")
        return ""
