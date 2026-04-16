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
        self.setFixedSize(300, 75)
        
        # Layout - compact merged design
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(14, 10, 14, 10)
        self.layout.setSpacing(0)

        # Single merged content label with HTML formatting
        self.content_label = QLabel()
        self.content_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        self.content_label.setWordWrap(True)
        self.content_label.setOpenExternalLinks(False)
        self.layout.addWidget(self.content_label)
        
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
        
        # Update content with merged HTML styling
        color = self.current_border_color
        self.content_label.setText(f"""
            <p style="margin: 0; line-height: 1.4;">
                <span style="color: {color}; font-weight: bold;">{title}</span><br>
                <span style="color: {THEME['text_secondary']}; font-size: 10px;">{message}</span>
            </p>
        """)
        
        # Apply styling
        if type == 'block':
            bg_color = "rgba(139, 0, 0, 0.95)"
        else:
            bg_color = "rgba(13, 31, 53, 0.98)"

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border: 2px solid {self.current_border_color};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
            }}
        """)
       
        
        # Get screen dimensions
        screen = QApplication.screens()[0]
        screen_width = screen.availableGeometry().width()
        screen_height = screen.availableGeometry().height()
        
        # Calculate positions
        end_x = screen_width - self.width() - 20
        end_y = screen_height - self.height() - 20
        start_y = screen_height + 50  # Start below screen
        
        # Set starting position (hidden)
        self.setGeometry(end_x, start_y, self.width(), self.height())
        self.setWindowOpacity(1.0)
        
        # Show the toast
        self.show()
        
        # Slide up animation
        self.slide_animation.setStartValue(self.geometry())
        self.slide_animation.setEndValue(self.geometry().adjusted(0, end_y - start_y, 0, end_y - start_y))
        self.slide_animation.start()
        
        # Start auto-hide timer (3 seconds)
        self.hide_timer.start(5000)
    
    def hide_toast(self):
        """Fade out and hide the toast"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)
        self.fade_animation.start()
    
    def mousePressEvent(self, event):
        """Allow clicking to dismiss"""
        self.hide_toast()
