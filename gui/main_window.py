from PyQt5 import QtWidgets, QtGui, QtCore
from core.device_detector import detect_devices, DeviceDetector
from core.plugin_manager import load_plugins
from core.device_monitor import DeviceMonitor
from core.device_info import get_device_info  # Add this import
import asyncio
import os  # Add this import
import time  # Add this import
from core.backup_manager import BackupManager
from translations import Translator
from utils.logger import logger
from utils.updater import AutoUpdater
from utils.theme_manager import ThemeManager
from gui.settings import SettingsWindow
from gui.plugin_manager import PluginManagerWindow
from gui.custom_widgets import AnimatedTitleBar, PulseButton, WaveBackground, DeviceCard

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager()
        # Set window flags to allow custom title bar while maintaining window controls
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | 
                       QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint | 
                       QtCore.Qt.WindowCloseButtonHint)
        
        # Initialize components first
        self.translator = Translator()
        self.backup_manager = BackupManager()
        self.updater = AutoUpdater()
        
        # Setup window
        self.setWindowTitle("Zwanski Unlocker Pro")
        self.resize(800, 600)
        
        # Create main widget
        main_widget = QtWidgets.QWidget()
        main_widget.setObjectName("mainWidget")
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add title bar
        self.title_bar = AnimatedTitleBar(self)
        self.title_bar.title_label.setText("🔓 Zwanski Unlocker Pro")
        self.title_bar.title_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
        """)
        main_layout.addWidget(self.title_bar)
        
        # Create and add content widget
        content_widget = QtWidgets.QWidget()
        content_widget.setObjectName("contentWidget")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(content_widget)
        
        # Set as central widget
        self.setCentralWidget(main_widget)
        
        # Setup the rest of UI
        self.setup_theme()  # Keep this
        self.setup_ui(content_layout)  # Keep this
        
        # Initialize device monitor
        self.device_monitor = DeviceMonitor(parent=self)
        self.device_monitor.device_connected.connect(self.on_device_connected)
        self.device_monitor.device_disconnected.connect(self.on_device_disconnected)
        self.device_monitor.device_state_changed.connect(self.on_device_state_changed)
        self.device_monitor.start()
        
        self.check_updates()

    def setup_theme(self):
        self.setStyleSheet("""
            #mainWidget {
                background: #1E1E1E;
            }
            #contentWidget {
                background: #2D2D2D;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #1976D2; 
            }
            QLabel { 
                color: white;
                font-size: 12pt; 
            }
            QTextEdit {
                background: #3D3D3D;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 8px;
            }
            QGroupBox {
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 1em;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
            }
            QComboBox {
                background: #3D3D3D;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
            }
        """)

    def setup_ui(self, layout):  # Modified to accept layout parameter
        # Create header with version
        header = QtWidgets.QLabel(f"{self.translator.get('device_manager')} v{self.updater.current_version}")
        header.setStyleSheet("font-size: 18pt; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Rest of the setup_ui code remains the same, just use the passed layout parameter
        # Add wave background
        self.wave_bg = WaveBackground(self)
        self.wave_bg.setFixedHeight(100)
        layout.addWidget(self.wave_bg)
        
        # Device info section
        device_info_group = QtWidgets.QGroupBox(self.translator.get("device_info"))
        device_info_layout = QtWidgets.QVBoxLayout()
        self.device_label = QtWidgets.QLabel(self.translator.get("no_device"))
        self.device_info = QtWidgets.QTextEdit()
        self.device_info.setReadOnly(True)
        self.device_info.setMaximumHeight(100)
        device_info_layout.addWidget(self.device_label)
        device_info_layout.addWidget(self.device_info)
        device_info_group.setLayout(device_info_layout)
        layout.addWidget(device_info_group)
        
        # Button container
        button_container = QtWidgets.QHBoxLayout()
        
        # Create all buttons with icons
        buttons = {
            "refresh": ("🔄", "detect_devices", self.on_detect),
            "exploit": ("⚡", "run_exploit", self.on_exploit),
            "backup": ("📦", "backup_device", self.on_backup),
            "restore": ("♻️", "restore_backup", self.on_restore),
            "screenshot": ("📸", "take_screenshot", self.on_screenshot)
        }
        
        for name, (icon, text, handler) in buttons.items():
            btn = PulseButton(f"{icon} {self.translator.get(text)}")
            btn.clicked.connect(handler)
            setattr(self, f"{name}_button", btn)
            button_container.addWidget(btn)
        
        layout.addLayout(button_container)
        
        # Add theme switcher
        theme_combo = QtWidgets.QComboBox()
        theme_combo.addItems(["Dark", "Light", "Hacker"])
        theme_combo.currentTextChanged.connect(lambda t: self.theme_manager.apply_theme(self, t.lower()))
        layout.addWidget(theme_combo)
        
        # Progress section
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Log section
        log_group = QtWidgets.QGroupBox(self.translator.get("operation_log"))
        log_layout = QtWidgets.QVBoxLayout()
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        log_layout.addWidget(self.log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Set the layout to the container
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        # Store buttons config for later use
        self.buttons = buttons
        
        # Status bar
        self.statusBar().showMessage(self.translator.get("ready"))

    def show_settings(self):
        settings_window = SettingsWindow(self)
        if settings_window.exec_() == QtWidgets.QDialog.Accepted:
            self.reload_settings()

    def reload_settings(self):
        """Reload application settings after changes"""
        try:
            # Reload translator
            self.translator.load_translations()
            
            # Update UI text
            self.setWindowTitle(self.translator.get("app_title"))
            self.device_info_group.setTitle(self.translator.get("device_info"))
            self.log_group.setTitle(self.translator.get("operation_log"))
            
            # Update button text
            for name, (icon, text, _) in self.buttons.items():
                button = getattr(self, f"{name}_button")
                button.setText(f"{icon} {self.translator.get(text)}")
            
            # Reload device monitor settings
            if hasattr(self, 'device_monitor'):
                self.device_monitor.reload_settings()
            
            # Update status bar
            self.statusBar().showMessage(self.translator.get("settings_updated"))
            
        except Exception as e:
            logger.error(f"Failed to reload settings: {e}")
            self.statusBar().showMessage(self.translator.get("settings_reload_failed"))

    def show_plugin_manager(self):
        plugin_window = PluginManagerWindow(self)
        plugin_window.exec_()

    def check_updates(self):
        has_update, version = self.updater.check_for_updates()
        if has_update:
            reply = QtWidgets.QMessageBox.question(
                self, 
                self.translator.get("update_available"),
                self.translator.get("update_prompt").format(version=version),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                self.perform_update(version)

    def perform_update(self, version):
        progress_dialog = QtWidgets.QProgressDialog(
            self.translator.get("downloading_update"),
            self.translator.get("cancel"),
            0, 100, self
        )
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        
        def update_progress(value):
            progress_dialog.setValue(value)
        
        if self.updater.download_update(update_progress):
            if self.updater.install_update():
                QtWidgets.QMessageBox.information(
                    self,
                    self.translator.get("update_success"),
                    self.translator.get("update_restart")
                )
                self.close()
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    self.translator.get("update_failed"),
                    self.translator.get("update_failed_message")
                )

    def on_screenshot(self):
        devices = detect_devices()
        if not devices:
            self.append_log(self.translator.get("no_device"))
            return
            
        screenshot_path = os.path.join(os.getcwd(), "screenshots", f"screen_{time.strftime('%Y%m%d_%H%M%S')}.png")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        try:
            subprocess.run(["adb", "-s", devices[0], "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
            subprocess.run(["adb", "-s", devices[0], "pull", "/sdcard/screen.png", screenshot_path], check=True)
            subprocess.run(["adb", "-s", devices[0], "shell", "rm", "/sdcard/screen.png"], check=True)
            self.append_log(f"✅ {self.translator.get('screenshot_saved')}: {screenshot_path}")
        except subprocess.CalledProcessError:
            self.append_log(f"❌ {self.translator.get('screenshot_failed')}")

    def append_log(self, text):
        self.log.append(f"[{QtCore.QTime.currentTime().toString('HH:mm:ss')}] {text}")

    def update_device_info(self, device_id):
        info = get_device_info(device_id)
        if info:
            self.device_info.setText("\n".join(f"{k}: {v}" for k, v in info.items()))
        else:
            self.device_info.setText(self.translator.get("device_info_error"))

    def on_detect(self):
        devices = detect_devices()
        if devices:
            device_id = devices[0]
            self.device_label.setText(f"📱 {device_id}")
            self.append_log(self.translator.get("device_detected"))
            self.update_device_info(device_id)
        else:
            self.device_label.setText(self.translator.get("no_device"))
            self.device_info.clear()
            self.append_log(self.translator.get("no_device_found"))

    def on_exploit(self):
        devices = detect_devices()
        if not devices:
            self.append_log("❌ Connect a device first")
            return

        plugins = load_plugins()
        for plugin in plugins:
            if devices[0] in plugin.supported_devices():
                self.append_log(f"👉 Using plugin: {plugin.name}")
                result = plugin.exploit(devices[0], progress_callback=self.append_log)
                self.append_log(f"Result: {result}")
                return

        self.append_log("❌ No compatible plugin found")

    def on_backup(self):
        devices = detect_devices()
        if not devices:
            self.append_log("❌ No device connected")
            return
            
        device_id = devices[0]
        result = self.backup_manager.create_backup(device_id, self.append_log)
        
        if result["status"] == "success":
            self.append_log(f"✅ Backup created: {result['path']}")
        else:
            self.append_log(f"❌ Backup failed: {result['message']}")

    def on_restore(self):
        devices = detect_devices()
        if not devices:
            self.append_log("❌ No device connected")
            return
            
        file_dialog = QtWidgets.QFileDialog()
        backup_file, _ = file_dialog.getOpenFileName(
            self,
            "Select Backup File",
            self.backup_manager.backup_dir,
            "Android Backup (*.ab)"
        )
        
        if backup_file:
            result = self.backup_manager.restore_backup(
                backup_file, 
                devices[0], 
                self.append_log
            )
            
            if result["status"] == "success":
                self.append_log("✅ Backup restored successfully")
            else:
                self.append_log(f"❌ Restore failed: {result['message']}")


    def on_device_connected(self, device_id):
        self.device_label.setText(f"📱 {device_id}")
        self.append_log(f"✅ {self.translator.get('device_connected')}: {device_id}")
        self.update_device_info(device_id)
        
    def on_device_disconnected(self, device_id):
        if self.device_label.text().endswith(device_id):
            self.device_label.setText(self.translator.get("no_device"))
            self.device_info.clear()
        self.append_log(f"❌ {self.translator.get('device_disconnected')}: {device_id}")
        
    def on_device_state_changed(self, device_id, new_state):
        self.append_log(f"ℹ️ {device_id}: {new_state}")
        if new_state == "unauthorized":
            self.append_log(self.translator.get("allow_usb_debugging"))

    def closeEvent(self, event):
        self.device_monitor.stop()
        self.device_monitor.wait()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

