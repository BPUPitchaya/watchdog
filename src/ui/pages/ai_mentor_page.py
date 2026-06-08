"""AI Mentor page implementation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.theme import THEME
from src.ui.widgets.loading_spinner import LoadingOverlay


class AIMentorPage:
    """AI Mentor page as a Forensic Analysis Hub."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.mentor_chat_area = None
        self.mentor_chat_layout = None
        self.mentor_input = None
        self.loading_overlay = None
        
    def create(self):
        """Create and return the AI mentor page widget."""
        mentor_page = QWidget()
        mentor_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")

        page_layout = QVBoxLayout(mentor_page)
        page_layout.setContentsMargins(16, 16, 16, 16)
        page_layout.setSpacing(12)

        # ===== PAGE HEADER =====
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        page_title = QLabel("AI Assistant")
        page_title.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        page_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600;")
        header_layout.addWidget(page_title)

        page_subtitle = QLabel("Forensic Analysis Hub")
        page_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        page_subtitle.setStyleSheet(f"color: {THEME['text_secondary']};")
        page_subtitle.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(page_subtitle)
        header_layout.addStretch()

        page_layout.addLayout(header_layout)

        # Content row: 70% chat, 30% diagnostics
        content_widget = QWidget()
        main_layout = QHBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)
        page_layout.addWidget(content_widget)

        # LEFT SIDE - Chat Area (70%)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setSpacing(10)

        # Status Bar Header
        status_bar = QFrame()
        status_bar.setFixedHeight(36)
        status_bar.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_card']};
                border-radius: 6px;
            }}
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(15, 5, 15, 5)
        
        # Sentinel Pulse Icon
        pulse_icon = QLabel("●")
        pulse_icon.setStyleSheet(f"""
            QLabel {{
                color: {THEME['primary']};
                font-size: 10px;
            }}
        """)
        status_layout.addWidget(pulse_icon)
        
        # Status Text
        status_text = QLabel("SYSTEM STATUS: MONITORING | AGENT: LLAMA 4 SCOUT")
        status_text.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 11px;
            }}
        """)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        # AI Toggle Button
        self.ai_toggle_btn = QPushButton("ON" if self.dashboard and self.dashboard.ai_client else "OFF")
        self.ai_toggle_btn.setFixedSize(40, 22)
        self.ai_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ai_toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#22C55E' if self.dashboard and self.dashboard.ai_client else '#EF4444'};
                color: white;
                border: none;
                border-radius: 4px;
                font-family: {THEME['font_mono']};
                font-size: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {'#16A34A' if self.dashboard and self.dashboard.ai_client else '#DC2626'};
            }}
        """)
        self.ai_toggle_btn.clicked.connect(self._toggle_ai)
        status_layout.addWidget(self.ai_toggle_btn)
        
        chat_layout.addWidget(status_bar)

        # AI Model Selector
        model_widget = QWidget()
        model_layout = QHBoxLayout(model_widget)
        model_layout.setContentsMargins(10, 8, 10, 8)
        model_layout.setSpacing(10)
        model_widget.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
            border-radius: 6px;
        """)
        
        model_label = QLabel("AI Model:")
        model_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        model_layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        self.model_selector.addItems([
            "llama3.2:1b (~1GB RAM - 8GB Macs)",
            "llama3.2:3b (~2GB RAM - 8-16GB Macs)",
            "llama3:8b (~4-5GB RAM - 16GB+ Macs)",
            "phi4 (~6GB RAM - Best Quality)"
        ])
        self.model_selector.setCurrentIndex(1)  # Default to 3b
        self.model_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 4px 8px;
                font-size: 11px;
                min-width: 180px;
            }}
            QComboBox:focus {{
                border: 1px solid {THEME['primary']};
            }}
        """)
        self.model_selector.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_selector)
        
        # RAM indicator
        self.ram_label = QLabel(" 8GB+")
        self.ram_label.setStyleSheet(f"color: {THEME['success']}; font-size: 10px;")
        model_layout.addWidget(self.ram_label)
        
        # Help link
        help_label = QLabel("<a href='#' style='color: #2DD4BF; text-decoration: underline; font-size: 11px;'>How to find the best AI Model</a>")
        help_label.setStyleSheet("color: {THEME['primary']};")
        help_label.setToolTip("Click for AI model selection guide")
        help_label.mousePressEvent = lambda e: self._show_model_help()
        model_layout.addWidget(help_label)
        
        model_layout.addStretch()
        chat_layout.addWidget(model_widget)

        # Chat Scroll Area
        self.mentor_chat_area = QScrollArea()
        self.mentor_chat_area.setWidgetResizable(True)
        self.mentor_chat_area.setFrameShape(QFrame.Shape.NoFrame)
        self.mentor_chat_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
            }}
        """)
        
        # Chat content widget
        chat_content = QWidget()
        self.mentor_chat_layout = QVBoxLayout(chat_content)
        self.mentor_chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mentor_chat_layout.setSpacing(10)
        self.mentor_chat_area.setWidget(chat_content)
        chat_layout.addWidget(self.mentor_chat_area)
        
        # Loading overlay (hidden by default)
        self.loading_overlay = LoadingOverlay("AI Processing...", self.mentor_chat_area)
        self.loading_overlay.setGeometry(0, 0, self.mentor_chat_area.width(), self.mentor_chat_area.height())
        self.loading_overlay.hide()

        # Input area
        input_container = QWidget()
        input_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border-radius: 6px;
            }}
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(8, 6, 8, 6)
        
        self.mentor_input = QLineEdit()
        self.mentor_input.setPlaceholderText("Ask the AI Mentor about security analysis...")
        self.mentor_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 6px 10px;
                font-family: {THEME['font_mono']};
                font-size: 12px;
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
            }}
        """)
        self.mentor_input.returnPressed.connect(self._send_mentor_message)
        input_layout.addWidget(self.mentor_input)
        
        send_btn = QPushButton("Send")
        send_btn.setFixedWidth(64)
        send_btn.setMinimumHeight(34)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px;
                font-family: {THEME['font_mono']};
                font-weight: 600;
                font-size: 12px;
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
                border-radius: 8px;
            }}
        """)
        diagnostics_layout = QVBoxLayout(diagnostics_container)
        diagnostics_layout.setContentsMargins(12, 12, 12, 12)
        
        # Diagnostics Header
        diag_header = QLabel("Diagnostics")
        diag_header.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        diag_header.setStyleSheet(f"color: {THEME['text_secondary']}; font-weight: 600;")
        diagnostics_layout.addWidget(diag_header)
        
        # Diagnostics content
        diag_content = QTextEdit()
        diag_content.setReadOnly(True)
        diag_content.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_dark']};
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 11px;
                padding: 8px;
                border: none;
                border-radius: 6px;
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
        actions_header = QLabel("Quick Actions")
        actions_header.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        actions_header.setStyleSheet(f"color: {THEME['text_secondary']}; font-weight: 600; margin-top: 8px;")
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
                    padding: 6px 10px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                    margin: 2px 0;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {THEME['bg_dark']};
                    color: {THEME['text_primary']};
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
        
        # Show loading overlay
        if self.loading_overlay:
            self.loading_overlay.setGeometry(0, 0, self.mentor_chat_area.width(), self.mentor_chat_area.height())
            self.loading_overlay.show()
            self.loading_overlay.raise_()
        
        # Use process_command to get proper response
        ai_response = self.dashboard.process_command(msg)
        
        # Hide loading overlay
        if self.loading_overlay:
            self.loading_overlay.hide()
        
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
    
    def _on_model_changed(self, index):
        """Handle AI model selection change."""
        models = ["llama3.2:1b", "llama3.2:3b", "llama3:8b", "phi4"]
        selected_model = models[index]
        
        # Update RAM indicator
        ram_labels = ["8GB", "8GB+", "16GB+", "16GB++"]
        colors = [THEME['success'], THEME['success'], THEME['warning'], THEME['danger']]
        self.ram_label.setText(ram_labels[index])
        self.ram_label.setStyleSheet(f"color: {colors[index]}; font-size: 10px;")
        
        # Notify dashboard to update model and sync forensic panel
        if self.dashboard and hasattr(self.dashboard, 'update_ai_model'):
            self.dashboard.update_ai_model(selected_model)
            # Add system message to chat
            system_msg = QLabel(f"System: AI model switched to {selected_model}")
            system_msg.setStyleSheet(f"""
                color: {THEME['primary']};
                font-size: 11px;
                font-style: italic;
                padding: 5px;
            """)
            self.mentor_chat_layout.addWidget(system_msg)
            self.mentor_chat_area.verticalScrollBar().setValue(
                self.mentor_chat_area.verticalScrollBar().maximum()
            )
            # Sync forensic panel if available
            if hasattr(self.dashboard, 'forensic_panel') and self.dashboard.forensic_panel:
                self.dashboard.forensic_panel.set_model(index)

    def set_model(self, index):
        """Set model from external source (sync from forensic panel or settings)."""
        # Block signals to prevent loop
        self.model_selector.blockSignals(True)
        self.model_selector.setCurrentIndex(index)
        self.model_selector.blockSignals(False)

    def apply_theme(self):
        """Re-apply current theme to AI mentor page components."""
        from src.ui.theme import THEME
        
        # Update model selector
        if hasattr(self, 'model_selector'):
            self.model_selector.setStyleSheet(f"""
                QComboBox {{
                    background-color: {THEME['bg_card']};
                    border: 1px solid {THEME['border']};
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 8px;
                    font-family: {THEME['font_mono']};
                    font-size: 12px;
                }}
            """)
        
        # Update RAM indicator
        if hasattr(self, 'ram_label'):
            self.ram_label.setStyleSheet(f"color: {THEME['success']}; font-size: 10px;")
        
        # Update mentor chat area
        if hasattr(self, 'mentor_chat_area'):
            self.mentor_chat_area.setStyleSheet(f"""
                QScrollArea {{
                    background-color: {THEME['bg_dark']};
                    border: none;
                    border-radius: 8px;
                }}
            """)

    def _show_model_help(self):
        """Show help dialog for selecting the best AI model based on RAM."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
        
        dialog = QDialog(self.dashboard)
        dialog.setWindowTitle("AI Model Selection Guide")
        dialog.setFixedSize(450, 500)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME['bg_dark']};
            }}
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                padding: 10px;
            }}
        """)
        
        help_content = """<h2 style='color: #2DD4BF;'> AI Model Selection Guide</h2>

<h3 style='color: #F97316;'> How to Check Your RAM</h3>
<p><b>Mac:</b> Click Apple menu → About This Mac → look for "Memory"</p>
<p><b>Windows:</b> Press Win+Pause/Break or Settings → System → About</p>

<h3 style='color: #2DD4BF;'> Choose Your Model</h3>
<table border='0' cellpadding='5'>
<tr style='color: #22C55E;'><td><b>8GB</b></td><td>llama3.2:1b (~1GB)</td><td>Fast, basic answers</td></tr>
<tr style='color: #22C55E;'><td><b>8GB+</b></td><td>llama3.2:3b (~2GB)</td><td>Balanced speed/quality</td></tr>
<tr style='color: #F97316;'><td><b>16GB+</b></td><td>llama3:8b (~4-5GB)</td><td>Good quality, slower</td></tr>
<tr style='color: #EF4444;'><td><b>16GB++</b></td><td>phi4 (~6GB)</td><td>Best quality, very slow on 8GB</td></tr>
</table>

<h3 style='color: #F97316;'> Recommendations</h3>
<p><b>8GB Mac/PC:</b> Use <b>1b</b> for speed or <b>3b</b> if you close other apps</p>
<p><b>16GB Mac/PC:</b> Use <b>3b</b> or <b>8b</b> for better answers</p>
<p><b>32GB+ Mac/PC:</b> Use <b>phi4</b> for professional-grade analysis</p>

<h3 style='color: #EF4444;'> Warning Signs</h3>
<p>• Rainbow wheel / spinning cursor = RAM full, switch to smaller model</p>
<p>• Long delays (>30 sec) = model too big for your system</p>
<p>• App freezes = immediately switch to 1b or use --no-ai mode</p>

<p style='color: #6B7280; font-size: 11px; margin-top: 20px;'><i>Tip: Start with 3b and only go higher if responses are fast enough.</i></p>
<p style='color: #6B7280; font-size: 11px; margin-top: 20px;'><i>Tip: If you are using a 8GB Mac/PC, use 1b for speed or 3b if you close other apps.</i></p>"""
        
        help_text.setHtml(help_content)
        layout.addWidget(help_text)
        
        close_btn = QPushButton("Got it!")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 6px;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()

    def _toggle_ai(self):
        """Toggle AI on/off."""
        if not self.dashboard:
            return
        
        if self.dashboard.ai_client:
            # Disable AI
            self.dashboard.ai_client = None
            self.ai_toggle_btn.setText("OFF")
            self.ai_toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #EF4444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-family: {THEME['font_mono']};
                    font-size: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
            """)
            # Add system message to chat
            self._add_system_message("AI disabled")
        else:
            # Enable AI
            try:
                from src.ai.ollama_client import OllamaClient
                self.dashboard.ai_client = OllamaClient()
                self.ai_toggle_btn.setText("ON")
                self.ai_toggle_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #22C55E;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-family: {THEME['font_mono']};
                        font-size: 10px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: #16A34A;
                    }}
                """)
                self._add_system_message("AI enabled - connected to Ollama")
            except Exception as e:
                self._add_system_message(f"Failed to enable AI: {str(e)}")

    def _add_system_message(self, message):
        """Add a system message to the mentor chat."""
        from PyQt6.QtWidgets import QLabel
        sys_label = QLabel(f"System: {message}")
        sys_label.setStyleSheet(f"""
            color: {THEME['text_secondary']};
            font-family: {THEME['font_mono']};
            font-size: 11px;
            font-style: italic;
            padding: 5px;
        """)
        self.mentor_chat_layout.addWidget(sys_label)
        # Scroll to bottom
        self.mentor_chat_area.verticalScrollBar().setValue(
            self.mentor_chat_area.verticalScrollBar().maximum()
        )
