from PyQt5 import QtGui, QtCore
import json
import os

class ThemeManager:
    def __init__(self):
        self.themes_path = os.path.join(os.path.dirname(__file__), "..", "assets", "themes")
        self.current_theme = "dark"
        self.load_themes()

    def load_themes(self):
        self.themes = {
            "dark": {
                "background": "#1E1E1E",
                "surface": "#2D2D2D",
                "primary": "#0D47A1",
                "secondary": "#1565C0",
                "text": "#FFFFFF",
                "border": "#555555",
                "success": "#4CAF50",
                "error": "#F44336",
                "warning": "#FFC107"
            },
            "light": {
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "primary": "#1976D2",
                "secondary": "#2196F3",
                "text": "#212121",
                "border": "#BDBDBD",
                "success": "#4CAF50",
                "error": "#F44336",
                "warning": "#FFC107"
            },
            "hacker": {
                "background": "#000000",
                "surface": "#0A0A0A",
                "primary": "#00FF00",
                "secondary": "#00CC00",
                "text": "#00FF00",
                "border": "#004400",
                "success": "#00FF00",
                "error": "#FF0000",
                "warning": "#FFFF00"
            }
        }

    def get_theme(self, name=None):
        return self.themes.get(name or self.current_theme)

    def apply_theme(self, window, name):
        self.current_theme = name
        theme = self.get_theme()
        window.setStyleSheet(self._generate_stylesheet(theme))

    def _generate_stylesheet(self, theme):
        return f"""
            QMainWindow {{
                background: {theme['background']};
            }}
            #contentWidget {{
                background: {theme['surface']};
                border-radius: 10px;
                margin: 0px 10px 10px 10px;
            }}
            QPushButton {{
                background: {theme['primary']};
                color: {theme['text']};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {theme['secondary']};
            }}
            QLabel {{
                color: {theme['text']};
            }}
            QTextEdit {{
                background: {theme['surface']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
            }}
            QGroupBox {{
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 4px;
                margin-top: 1em;
            }}
        """