"""AI Mentor page implementation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.theme import THEME


class AIMentorPage:
    """AI Mentor page as a Forensic Analysis Hub."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.mentor_chat_area = None
        self.mentor_chat_layout = None
        self.mentor_input = None
        
    def create(self):
        """Create and return the AI mentor page widget."""
        mentor_page = QWidget()
        mentor_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Main Horizontal Layout: 70% chat, 30% diagnostics
        main_layout = QHBoxLayout(mentor_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # LEFT SIDE - Chat Area (70%)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setSpacing(10)

        # Status Bar Header
        status_bar = QFrame()
        status_bar.setFixedHeight(40)
        status_bar.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['primary']};
            }}
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(15, 5, 15, 5)
        
        # Sentinel Pulse Icon
        pulse_icon = QLabel("●")
        pulse_icon.setStyleSheet(f"""
            QLabel {{
                color: {THEME['primary']};
                font-size: 16px;
            }}
        """)
        status_layout.addWidget(pulse_icon)
        
        # Status Text
        status_text = QLabel("SYSTEM STATUS: MONITORING | AGENT: LLAMA 4 SCOUT")
        status_text.setStyleSheet(f"""
            QLabel {{
                color: {THEME['primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
            }}
        """)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        chat_layout.addWidget(status_bar)

        # Chat Scroll Area
        self.mentor_chat_area = QScrollArea()
        self.mentor_chat_area.setWidgetResizable(True)
        self.mentor_chat_area.setFrameShape(QFrame.Shape.NoFrame)
        self.mentor_chat_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Chat content widget
        chat_content = QWidget()
        self.mentor_chat_layout = QVBoxLayout(chat_content)
        self.mentor_chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mentor_chat_layout.setSpacing(10)
        self.mentor_chat_area.setWidget(chat_content)
        chat_layout.addWidget(self.mentor_chat_area)

        # Input area
        input_container = QWidget()
        input_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
            }}
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 5, 10, 5)
        
        self.mentor_input = QLineEdit()
        self.mentor_input.setPlaceholderText("Ask the AI Mentor about security analysis...")
        self.mentor_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
            }}
        """)
        self.mentor_input.returnPressed.connect(self._send_mentor_message)
        input_layout.addWidget(self.mentor_input)
        
        send_btn = QPushButton("Send")
        send_btn.setFixedWidth(80)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-family: {THEME['font_mono']};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        send_btn.clicked.connect(self._send_mentor_message)
        input_layout.addWidget(send_btn)
        
        chat_layout.addWidget(input_container)
        
        main_layout.addWidget(chat_container, stretch=7)

        # RIGHT SIDE - Diagnostics Panel (30%)
        diagnostics_container = QWidget()
        diagnostics_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        diagnostics_layout = QVBoxLayout(diagnostics_container)
        diagnostics_layout.setContentsMargins(15, 15, 15, 15)
        
        # Diagnostics Header
        diag_header = QLabel("DIAGNOSTICS")
        diag_header.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        diag_header.setStyleSheet(f"color: {THEME['primary']}; font-weight: bold;")
        diagnostics_layout.addWidget(diag_header)
        
        # Diagnostics content
        diag_content = QTextEdit()
        diag_content.setReadOnly(True)
        diag_content.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 11px;
                padding: 10px;
            }}
        """)
        diag_content.setText("""System Diagnostics:
• Packet Monitor: Active
• AI Engine: Online
• Firewall: Enabled
• Threat DB: Updated

Last Scan: 2 minutes ago
Blocked Today: 4 IPs
Analyzed: 1,247 packets""")
        diagnostics_layout.addWidget(diag_content)
        
        # Quick Actions
        actions_header = QLabel("QUICK ACTIONS")
        actions_header.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        actions_header.setStyleSheet(f"color: {THEME['primary']}; font-weight: bold; margin-top: 10px;")
        diagnostics_layout.addWidget(actions_header)
        
        # Action buttons
        for action_text in ["Analyze Last Threat", "Generate Report", "Export Logs"]:
            btn = QPushButton(action_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {THEME['text_secondary']};
                    border: 1px solid {THEME['border']};
                    border-radius: 6px;
                    padding: 8px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                    margin: 2px 0;
                }}
                QPushButton:hover {{
                    background-color: {THEME['primary']};
                    color: {THEME['bg_dark']};
                    border-color: {THEME['primary']};
                }}
            """)
            diagnostics_layout.addWidget(btn)
        
        diagnostics_layout.addStretch()
        main_layout.addWidget(diagnostics_container, stretch=3)

        return mentor_page
        
    def _send_mentor_message(self):
        """Send a message in the AI mentor chat."""
        msg = self.mentor_input.text().strip()
        if not msg:
            return
        
        # Clear input first
        self.mentor_input.clear()
        
        # Add to shared conversation history (this syncs both chats)
        self.dashboard.add_chat_message("user", msg)
        
        # Use process_command to get proper response
        ai_response = self.dashboard.process_command(msg)
        
        # Add AI response to shared history (skip if async processing)
        if ai_response != "__AI_PROCESSING__":
            self.dashboard.add_chat_message("ai", ai_response)
        
        # Scroll to bottom
        self.mentor_chat_area.verticalScrollBar().setValue(
            self.mentor_chat_area.verticalScrollBar().maximum()
        )
        
    def _add_ai_response(self, text):
        """Add an AI response bubble to the chat."""
        ai_bubble = QLabel(text)
        ai_bubble.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
            color: {THEME['text_primary']};
            padding: 10px;
            border-radius: 8px;
            margin: 4px;
            font-family: {THEME['font_mono']};
        """)
        ai_bubble.setWordWrap(True)
        self.mentor_chat_layout.addWidget(ai_bubble)
        
    def sync_message(self, sender, message):
        """Sync a message from the shared conversation history to this chat."""
        if sender == "user":
            # Add user message bubble with "You" prefix
            user_bubble = QLabel(f"You: {message}")
            user_bubble.setStyleSheet(f"""
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
                padding: 10px;
                border-radius: 8px;
                margin: 4px;
                font-family: {THEME['font_mono']};
            """)
            user_bubble.setWordWrap(True)
            self.mentor_chat_layout.addWidget(user_bubble)
        else:  # ai
            # Add AI response bubble
            ai_bubble = QLabel(f"AI Mentor: {message}")
            ai_bubble.setStyleSheet(f"""
                background-color: {THEME['bg_card']};
                color: {THEME['text_primary']};
                padding: 10px;
                border-radius: 8px;
                margin: 4px;
                font-family: {THEME['font_mono']};
            """)
            ai_bubble.setWordWrap(True)
            self.mentor_chat_layout.addWidget(ai_bubble)
        
        # Scroll to bottom
        self.mentor_chat_area.verticalScrollBar().setValue(
            self.mentor_chat_area.verticalScrollBar().maximum()
        )
