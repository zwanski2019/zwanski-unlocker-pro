import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger
from utils.updater import AutoUpdater

def setup_environment():
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    # Create necessary directories
    dirs = ['logs', 'backups', 'core/frp_plugins', 'config']
    for dir_path in dirs:
        os.makedirs(os.path.join(project_root, dir_path), exist_ok=True)

if __name__ == '__main__':
    try:
        setup_environment()
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        logger.critical(f"Application failed to start: {e}")
        sys.exit(1)