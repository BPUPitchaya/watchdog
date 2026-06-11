from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from src.ui.theme import THEME


class ToastNotification(QWidget):
    """Frameless translucent toast notification that slides up from bottom-right"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Frameless, translucent, stay on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.ToolTip
            | Qt.WindowType.WindowDoesNotAcceptFocus
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
        self.content_label.setFont(QFont(THEME["font_mono"].strip("'"), 11))
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

        self.current_border_color = THEME["primary"]

    def show_message(self, title, message, type="info"):
        """Display a toast notification

        Args:
            title: Notification title
            message: Notification message
            type: 'info' (electric blue), 'block' (red), or 'simulation' (purple)
        """
        # Set border color based on type
        if type == "block":
            self.current_border_color = THEME["danger"]  # Red for real threats
        elif type == "simulation":
            self.current_border_color = "#9B59B6"  # Purple for simulations
        else:
            self.current_border_color = THEME["primary"]  # Electric Blue for info

        # Update content with HTML formatting
        color = self.current_border_color
        self.content_label.setText(f"""
            <p style="margin: 0; line-height: 1.4;">
                <span style="color: {color}; font-weight: bold;">{title}</span><br>
                <span style="color: {THEME['text_secondary']}; font-size: 10px;">{message}</span>
            </p>
        """)

        # Apply styling
        if type == "block":
            bg_color = "rgba(139, 0, 0, 0.95)"  # Dark red for threats
        elif type == "simulation":
            bg_color = "rgba(75, 0, 130, 0.95)"  # Deep purple for simulations
        else:
            bg_color = "rgba(13, 31, 53, 0.98)"  # Dark blue for info

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

        # Position in bottom-right corner of screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()
        screen_x = screen_geometry.x()
        screen_y = screen_geometry.y()

        # Calculate positions - bottom right corner with margin
        end_x = screen_x + screen_width - self.width() - 20
        end_y = screen_y + screen_height - self.height() - 20
        start_y = screen_y + screen_height + 50  # Start below screen

        # Define explicit start and end geometries
        start_rect = QRect(end_x, start_y, self.width(), self.height())
        end_rect = QRect(end_x, end_y, self.width(), self.height())

        # Set starting position (hidden)
        self.setGeometry(start_rect)
        self.setWindowOpacity(1.0)

        # Show the toast
        self.show()

        # Slide up animation using predefined start/end geometries
        self.slide_animation.setStartValue(start_rect)
        self.slide_animation.setEndValue(end_rect)
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
