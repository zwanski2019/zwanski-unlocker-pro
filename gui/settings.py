from PyQt5 import QtWidgets
import json
import os

class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(400, 300)
        self.settings_file = os.path.join(os.getcwd(), "config", "settings.json")
        self.load_settings()
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QFormLayout()
        
        # Language selection
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(["English", "Español", "Français"])
        layout.addRow("Language:", self.lang_combo)
        
        # Theme selection
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        layout.addRow("Theme:", self.theme_combo)
        
        # Auto-update settings
        self.auto_update = QtWidgets.QCheckBox("Check for updates on startup")
        layout.addRow(self.auto_update)
        
        # Debug mode
        self.debug_mode = QtWidgets.QCheckBox("Enable debug logging")
        layout.addRow(self.debug_mode)
        
        # ADB Path
        self.adb_path = QtWidgets.QLineEdit()
        browse_btn = QtWidgets.QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_adb)
        adb_layout = QtWidgets.QHBoxLayout()
        adb_layout.addWidget(self.adb_path)
        adb_layout.addWidget(browse_btn)
        layout.addRow("ADB Path:", adb_layout)
        
        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.save_settings)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        self.load_ui_values()

    def browse_adb(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select ADB executable", "", "Executable files (*.exe);;All files (*.*)"
        )
        if file_name:
            self.adb_path.setText(file_name)

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        except Exception:
            self.settings = {
                "language": "English",
                "theme": "Light",
                "auto_update": True,
                "debug": False,
                "adb_path": "adb.exe"
            }

    def load_ui_values(self):
        self.lang_combo.setCurrentText(self.settings.get("language", "English"))
        self.theme_combo.setCurrentText(self.settings.get("theme", "Light"))
        self.auto_update.setChecked(self.settings.get("auto_update", True))
        self.debug_mode.setChecked(self.settings.get("debug", False))
        self.adb_path.setText(self.settings.get("adb_path", "adb.exe"))

    def save_settings(self):
        self.settings = {
            "language": self.lang_combo.currentText(),
            "theme": self.theme_combo.currentText(),
            "auto_update": self.auto_update.isChecked(),
            "debug": self.debug_mode.isChecked(),
            "adb_path": self.adb_path.text()
        }
        
        os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)
        
        self.accept()