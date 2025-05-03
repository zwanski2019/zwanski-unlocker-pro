import sys
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import EnhancedLogger
from utils.updater import AutoUpdater

def main():
    # Initialize application
    app = QApplication(sys.argv)
    
    # Setup logger
    logger = EnhancedLogger()
    logger.info("Starting Zwanski FRP Unlocker Pro...")
    
    # Check for updates
    updater = AutoUpdater()
    has_update, version = updater.check_for_updates()
    if has_update:
        logger.info(f"New version {version} available")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
