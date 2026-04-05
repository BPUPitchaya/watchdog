from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont

from src.ui.theme import THEME


class ToastNotification(QWidget):
    """Frameless translucent toast notification that slides up from bottom-right"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Frameless, translucent, stay on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Size and position
        self.setFixedSize(320, 100)
        
        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 12, 16, 12)
        self.layout.setSpacing(4)
        
        # Title label
        self.title_label = QLabel()
        self.title_label.setFont(QFont(THEME['font_mono'].strip("'"), 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {THEME['text_primary']};")
        self.layout.addWidget(self.title_label)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        self.message_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        self.message_label.setWordWrap(True)
        self.layout.addWidget(self.message_label)
        
        # Animation objects
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(400)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        
        # Timer for auto-hide
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_toast)
        
        self.current_border_color = THEME['primary']
    
    def show_message(self, title, message, type='info'):
        """Display a toast notification
        
        Args:
            title: Notification title
            message: Notification message
            type: 'info' (electric blue) or 'block' (red)
        """
        # Set border color based on type
        if type == 'block':
            self.current_border_color = THEME['danger']  # Red
        else:
            self.current_border_color = THEME['primary']  # Electric Blue
        
        # Update content
        self.title_label.setText(title)
        self.message_label.setText(message)
        
        # Apply styling with border
        self.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(13, 31, 53, 0.95);
                border: 2px solid {self.current_border_color};
                border-radius: 12px;
            }}
        """)
        
        # Position at bottom-right of screen
        screen = QApplication.primaryScreen().geometry()
        end_x = screen.width() - self.width() - 20
        end_y = screen.height() - self.height() - 20
        start_x = end_x
        start_y = screen.height() + 50  # Start below screen
        
        # Set starting position (hidden)
        self.setGeometry(start_x, start_y, self.width(), self.height())
        self.setWindowOpacity(1.0)
        
        # Show the toast
        self.show()
        
        # Slide up animation
        self.slide_animation.setStartValue(self.geometry())
        self.slide_animation.setEndValue(self.geometry().adjusted(0, end_y - start_y, 0, end_y - start_y))
        self.slide_animation.start()
        
        # Start auto-hide timer (3 seconds)
        self.hide_timer.start(3000)
    
    def hide_toast(self):
        """Fade out and hide the toast"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
    
    def mousePressEvent(self, event):
        """Allow clicking to dismiss"""
        self.hide_toast()
