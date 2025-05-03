from PyQt5 import QtWidgets, QtCore
import json
import os

class PluginConfigDialog(QtWidgets.QDialog):
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setWindowTitle(f"Configure {plugin.name}")
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()

        # Exploit Methods
        group_exploit = QtWidgets.QGroupBox("Exploit Methods")
        layout_exploit = QtWidgets.QVBoxLayout()
        self.exploit_checkboxes = {}
        
        for method, enabled in self.plugin.config["exploit_methods"].items():
            cb = QtWidgets.QCheckBox(method.replace("_", " ").title())
            cb.setChecked(enabled)
            self.exploit_checkboxes[method] = cb
            layout_exploit.addWidget(cb)
        
        group_exploit.setLayout(layout_exploit)
        layout.addWidget(group_exploit)

        # Backup Settings
        group_backup = QtWidgets.QGroupBox("Backup Settings")
        layout_backup = QtWidgets.QFormLayout()
        
        self.auto_backup = QtWidgets.QCheckBox("Auto Backup")
        self.auto_backup.setChecked(self.plugin.config["backup_settings"]["auto_backup"])
        
        self.keep_backups = QtWidgets.QSpinBox()
        self.keep_backups.setValue(self.plugin.config["backup_settings"]["keep_backups"])
        
        layout_backup.addRow("Auto Backup:", self.auto_backup)
        layout_backup.addRow("Keep Backups:", self.keep_backups)
        
        group_backup.setLayout(layout_backup)
        layout.addWidget(group_backup)

        # Buttons
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def save_config(self):
        # Update exploit methods
        for method, checkbox in self.exploit_checkboxes.items():
            self.plugin.config["exploit_methods"][method] = checkbox.isChecked()

        # Update backup settings
        self.plugin.config["backup_settings"].update({
            "auto_backup": self.auto_backup.isChecked(),
            "keep_backups": self.keep_backups.value()
        })

        # Save to file
        with open(self.plugin.config_path, 'w') as f:
            json.dump(self.plugin.config, f, indent=4)

        self.accept()