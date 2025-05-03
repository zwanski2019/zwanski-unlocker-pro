from PyQt5 import QtWidgets, QtCore, QtGui, QtSvg
import math

class AnimatedTitleBar(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(40)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        # Title text with animation
        self.title_label = QtWidgets.QLabel("🔓 Zwanski Unlocker Pro")
        self.title_label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
        """)
        layout.addWidget(self.title_label)
        layout.addStretch()
        
        # Window controls
        controls_layout = QtWidgets.QHBoxLayout()
        controls_layout.setSpacing(4)
        
        # Create window control buttons
        for icon_name, slot, hover_color in [
            ("−", self.parent().showMinimized, "#FFA000"),  # Minimize
            ("□", self.parent().showMaximized, "#2196F3"),  # Maximize
            ("×", self.parent().close, "#F44336")  # Close
        ]:
            btn = QtWidgets.QPushButton(icon_name)
            btn.setFixedSize(30, 30)
            btn.clicked.connect(slot)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: #FFFFFF;
                    font-family: 'Segoe UI';
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background: {hover_color};
                    border-radius: 15px;
                }}
            """)
            controls_layout.addWidget(btn)
        
        layout.addLayout(controls_layout)
        
        # Start animation
        self.animation = QtCore.QVariantAnimation()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(2000)
        self.animation.setLoopCount(-1)
        self.animation.valueChanged.connect(self.update)
        self.animation.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        if hasattr(self, 'animation'):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            value = self.animation.currentValue()
            gradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0, QtGui.QColor(76, 175, 80, int(255 * value)))
            gradient.setColorAt(0.5, QtGui.QColor(139, 195, 74, int(255 * (1 - value))))
            gradient.setColorAt(1, QtGui.QColor(76, 175, 80, int(255 * value)))
            
            painter.setPen(QtGui.QPen(gradient, 2))
            painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

class ScrollingText(QtWidgets.QLabel):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
        """)
        
        self.pos = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(50)
        
    def update_position(self):
        self.pos = (self.pos + 1) % (self.width() + 200)
        self.update()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Create gradient
        gradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QtGui.QColor(76, 175, 80))
        gradient.setColorAt(0.5, QtGui.QColor(139, 195, 74))
        gradient.setColorAt(1, QtGui.QColor(76, 175, 80))
        
        # Set font
        font = QtGui.QFont("Segoe UI", 16, QtGui.QFont.Bold)
        painter.setFont(font)
        
        # Draw text with gradient
        painter.setPen(QtGui.QPen(QtGui.QBrush(gradient), 1))
        painter.drawText(self.width() - self.pos, 25, self.text())

class WindowControlButton(QtWidgets.QPushButton):
    def __init__(self, icon_name, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.setIcon(QtGui.QIcon(f":/icons/{icon_name}"))
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)

class PulseButton(QtWidgets.QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QtCore.QVariantAnimation()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setDuration(1000)
        self.animation.valueChanged.connect(self.update)
        self.animation.finished.connect(self.animation.start)
        self.animation.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isEnabled():
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            value = self.animation.currentValue()
            alpha = int(255 * (1.0 - value))
            size = int(min(self.width(), self.height()) * value)
            
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, alpha), 2))
            painter.drawEllipse(self.rect().center(), size, size)

class DeviceCard(QtWidgets.QWidget):
    def __init__(self, device_info, parent=None):
        super().__init__(parent)
        self.device_info = device_info
        self.setup_ui()
        self.start_animations()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Device icon
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(64, 64)
        layout.addWidget(self.icon_label, alignment=QtCore.Qt.AlignCenter)
        
        # Device info
        info_layout = QtWidgets.QFormLayout()
        for key, value in self.device_info.items():
            label = QtWidgets.QLabel(f"{key.title()}:")
            value_label = QtWidgets.QLabel(value)
            info_layout.addRow(label, value_label)
        layout.addLayout(info_layout)
        
        self.setStyleSheet("""
            DeviceCard {
                background: rgba(45, 45, 45, 0.8);
                border-radius: 10px;
                padding: 10px;
            }
            QLabel {
                color: white;
            }
        """)

    def start_animations(self):
        self.glow_animation = QtCore.QVariantAnimation()
        self.glow_animation.setStartValue(0.0)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.setDuration(2000)
        self.glow_animation.setLoopCount(-1)
        self.glow_animation.valueChanged.connect(self.update)
        self.glow_animation.start()

    def paintEvent(self, event):
        super().paintEvent(event)
        if hasattr(self, 'glow_animation'):
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            
            value = self.glow_animation.currentValue()
            gradient = QtGui.QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0, QtGui.QColor(0, 119, 255, int(50 * value)))
            gradient.setColorAt(1, QtGui.QColor(0, 191, 255, int(50 * (1 - value))))
            
            painter.setBrush(gradient)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRoundedRect(self.rect(), 10, 10)

class WaveBackground(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QtCore.QVariantAnimation()
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(2 * math.pi)
        self.animation.setDuration(3000)
        self.animation.valueChanged.connect(self.update)
        self.animation.finished.connect(self.animation.start)
        self.animation.start()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        phase = self.animation.currentValue()
        points = []
        for x in range(0, self.width(), 5):
            y = math.sin(x * 0.02 + phase) * 20 + self.height() / 2
            points.append(QtCore.QPointF(x, y))
        
        path = QtGui.QPainterPath()
        path.moveTo(points[0])
        for point in points[1:]:
            path.lineTo(point)
        
        gradient = QtGui.QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QtGui.QColor(0, 119, 255))
        gradient.setColorAt(1, QtGui.QColor(0, 191, 255))
        
        painter.setPen(QtGui.QPen(gradient, 2))
        painter.drawPath(path)