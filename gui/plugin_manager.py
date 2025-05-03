from PyQt5 import QtWidgets, QtCore
import os
import json
from core.plugin_manager import load_plugins

class PluginManagerWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Plugin Manager")
        self.resize(600, 400)
        self.plugins_dir = os.path.join(os.getcwd(), "core", "frp_plugins")
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Plugin list
        self.plugin_list = QtWidgets.QTableWidget()
        self.plugin_list.setColumnCount(4)
        self.plugin_list.setHorizontalHeaderLabels(["Name", "Version", "Status", "Supported Devices"])
        self.plugin_list.horizontalHeader().setStretchLastSection(True)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        self.enable_btn = QtWidgets.QPushButton("Enable")
        self.disable_btn = QtWidgets.QPushButton("Disable")
        self.update_btn = QtWidgets.QPushButton("Check Updates")
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        
        for btn in [self.enable_btn, self.disable_btn, self.update_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            btn.clicked.connect(self.on_button_click)
        
        layout.addWidget(self.plugin_list)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.refresh_plugins()

    def refresh_plugins(self):
        self.plugin_list.setRowCount(0)
        plugins = load_plugins()
        
        for plugin in plugins:
            row = self.plugin_list.rowCount()
            self.plugin_list.insertRow(row)
            
            self.plugin_list.setItem(row, 0, QtWidgets.QTableWidgetItem(plugin.name))
            self.plugin_list.setItem(row, 1, QtWidgets.QTableWidgetItem(getattr(plugin, 'version', 'N/A')))
            self.plugin_list.setItem(row, 2, QtWidgets.QTableWidgetItem("Enabled"))
            self.plugin_list.setItem(row, 3, QtWidgets.QTableWidgetItem(
                ", ".join(plugin.supported_devices())
            ))

    def on_button_click(self):
        sender = self.sender()
        if sender == self.refresh_btn:
            self.refresh_plugins()
        elif sender == self.update_btn:
            self.check_updates()
        else:
            self.toggle_plugin(sender == self.enable_btn)

    def toggle_plugin(self, enable):
        current_row = self.plugin_list.currentRow()
        if current_row >= 0:
            plugin_name = self.plugin_list.item(current_row, 0).text()
            status = "Enabled" if enable else "Disabled"
            self.plugin_list.setItem(current_row, 2, QtWidgets.QTableWidgetItem(status))

    def check_updates(self):
        # Implement plugin update check logic here
        QtWidgets.QMessageBox.information(self, "Updates", "No updates available")