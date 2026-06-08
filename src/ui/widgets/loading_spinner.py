"""Loading Spinner Widget for AI Queries"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QColor, QPen
from typing import Optional


class LoadingSpinner(QWidget):
    """Animated loading spinner for AI queries"""
    
    def __init__(self, size: int = 40, text: str = "Processing...", parent=None):
        super().__init__(parent)
        self.size = size
        self.text = text
        self.angle = 0
        self.setFixedSize(size + 100, size + 50)  # Extra space for text
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(50)  # 20 FPS
        
        # Optional label
        if text:
            self.label = QLabel(text)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setStyleSheet("color: #00B4D8; font-size: 12px;")
    
    def rotate(self):
        """Rotate the spinner"""
        self.angle = (self.angle + 15) % 360
        self.update()
    
    def paintEvent(self, event):
        """Draw the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Center point
        center_x = self.width() // 2
        center_y = (self.height() // 2) - 10  # Offset for text
        
        # Draw spinner arc
        pen = QPen(QColor("#00B4D8"))
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw arc
        rect_x = center_x - self.size // 2
        rect_y = center_y - self.size // 2
        painter.drawArc(
            rect_x, rect_y, 
            self.size, self.size, 
            self.angle * 16, 270 * 16
        )
    
    def stop(self):
        """Stop the spinner animation"""
        self.timer.stop()
    
    def start(self):
        """Start the spinner animation"""
        self.timer.start(50)


class LoadingOverlay(QWidget):
    """Full overlay with spinner and text"""
    
    def __init__(self, text: str = "AI Processing...", parent=None):
        super().__init__(parent)
        self.text = text
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the overlay UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Spinner
        self.spinner = LoadingSpinner(size=50, text="")
        layout.addWidget(self.spinner, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Text label
        self.label = QLabel(self.text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                margin-top: 20px;
            }
        """)
        layout.addWidget(self.label, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(15, 19, 24, 0.9);
                border-radius: 8px;
            }
        """)
    
    def set_text(self, text: str):
        """Update the text"""
        self.text = text
        self.label.setText(text)
    
    def show(self):
        """Show overlay"""
        self.spinner.start()
        super().show()
    
    def hide(self):
        """Hide overlay"""
        self.spinner.stop()
        super().hide()
