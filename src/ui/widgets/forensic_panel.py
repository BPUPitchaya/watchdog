from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from src.ui.theme import THEME


class ForensicAssistantPanel(QWidget):
    """AI chat panel for forensic analysis"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Forensic Assistant AI")
        header.setStyleSheet(f"""
            background-color: {THEME['primary']};
            color: white;
            padding: 12px;
            font-family: {THEME['font_mono']};
            font-size: 14px;
            font-weight: bold;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-top: none;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(8)
        input_widget.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
            border: 1px solid {THEME['border']};
            border-top: none;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        """)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type here to ask AI...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                padding: 8px 12px;
            }}
        """)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("▶")
        send_btn.setFixedSize(30, 30)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        # Connect Enter key to send message
        self.input_field.returnPressed.connect(self.send_message)
        
        layout.addWidget(input_widget)
        
    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            self.chat_area.append(f"<b>You:</b> {text}")
            self.chat_area.append(f"<b><span style='color: {THEME['primary']}'>AI:</span></b> I'm analyzing the packet data...")
            self.input_field.clear()
