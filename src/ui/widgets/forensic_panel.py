from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.ui.theme import THEME
from src.ui.widgets.loading_spinner import LoadingOverlay


class ForensicAssistantPanel(QWidget):
    """AI chat panel for forensic analysis"""

    def __init__(self, dashboard=None, parent=None):
        super().__init__(parent)
        self.dashboard = dashboard
        self.loading_overlay = None
        self.setMinimumSize(300, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header with AI toggle
        header_widget = QWidget()
        header_widget.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(10)

        # Title
        header_title = QLabel("Forensic Assistant")
        header_title.setStyleSheet("""
            color: #D4D8E0;
            font-family: {THEME['font_mono']};
            font-size: 12px;
            font-weight: 600;
            background-color: transparent;
        """.replace("{THEME['font_mono']}", THEME["font_mono"]))
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        # AI Toggle Button
        self.ai_toggle_btn = QPushButton(
            "ON" if self.dashboard and self.dashboard.ai_client else "OFF"
        )
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
        header_layout.addWidget(self.ai_toggle_btn)

        layout.addWidget(header_widget)

        # AI Model Selector
        settings_widget = QWidget()
        settings_layout = QHBoxLayout(settings_widget)
        settings_layout.setContentsMargins(10, 8, 10, 8)
        settings_layout.setSpacing(10)
        settings_widget.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
        """)

        model_label = QLabel("AI Model:")
        model_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        settings_layout.addWidget(model_label)

        self.model_selector = QComboBox()
        self.model_selector.addItems(
            [
                "llama3.2:1b (~1GB RAM)",
                "llama3.2:3b (~2GB RAM)",
                "llama3:8b (~4-5GB RAM)",
                "phi4 (~6GB RAM - Best Quality)",
            ]
        )
        self.model_selector.setCurrentIndex(0)  # Default to 1b for stability
        self.model_selector.setStyleSheet(f"""
            QComboBox {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 4px;
                color: {THEME['text_primary']};
                padding: 4px;
                font-size: 11px;
            }}
        """)
        self.model_selector.currentIndexChanged.connect(self._on_model_changed)
        settings_layout.addWidget(self.model_selector)

        # RAM indicator
        self.ram_label = QLabel("8GB+")
        self.ram_label.setStyleSheet(f"color: {THEME['success']}; font-size: 10px;")
        settings_layout.addWidget(self.ram_label)

        # Help link
        help_btn = QPushButton("?")
        help_btn.setFixedSize(20, 20)
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        help_btn.setToolTip("How to find the best AI model")
        help_btn.clicked.connect(self._show_model_help)
        settings_layout.addWidget(help_btn)

        settings_layout.addStretch()
        layout.addWidget(settings_widget)

        # Chat area container (for overlay)
        chat_container = QWidget()
        chat_container_layout = QVBoxLayout(chat_container)
        chat_container_layout.setContentsMargins(0, 0, 0, 0)
        chat_container_layout.setSpacing(0)

        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_card']};
                border: none;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                padding: 8px;
            }}
        """)
        chat_container_layout.addWidget(self.chat_area)

        # Loading overlay (hidden by default)
        self.loading_overlay = LoadingOverlay("AI Processing...", self.chat_area)
        self.loading_overlay.setGeometry(0, 0, self.chat_area.width(), self.chat_area.height())
        self.loading_overlay.hide()

        layout.addWidget(chat_container)

        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(8)
        input_widget.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
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
                padding: 6px 10px;
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
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
        if not text:
            return
        self.input_field.clear()

        # Use shared conversation if dashboard available
        if self.dashboard:
            self.dashboard.add_chat_message("user", text)
            # Show loading overlay
            if self.loading_overlay:
                self.loading_overlay.setGeometry(
                    0, 0, self.chat_area.width(), self.chat_area.height()
                )
                self.loading_overlay.show()
                self.loading_overlay.raise_()
            # Simulate AI response with delay for loading effect
            QTimer.singleShot(100, lambda: self._send_ai_response(text))
        else:
            # Fallback: just update local chat
            self.chat_area.append(f"<b>You:</b> {text}")
            self.chat_area.append(
                f"<b><span style='color: {THEME['primary']}'>AI:</span></b> I'm analyzing the packet data..."
            )

    def _send_ai_response(self, user_text):
        """Send AI response through shared conversation using process_command."""
        if self.dashboard:
            # Use process_command to get proper response based on keywords
            response = self.dashboard.process_command(user_text)
            # Hide loading overlay
            if self.loading_overlay:
                self.loading_overlay.hide()
            # Skip adding message if async AI is processing (handler will add it)
            if response != "__AI_PROCESSING__":
                self.dashboard.add_chat_message("ai", response)

    def _on_model_changed(self, index):
        """Handle AI model selection change."""
        models = ["llama3.2:1b", "llama3.2:3b", "llama3:8b", "phi4"]
        selected_model = models[index]

        # Update RAM indicator
        ram_labels = ["⚡ 8GB", "⚡ 8GB+", "⚡ 16GB+", "⚡ 16GB++"]
        colors = [THEME["success"], THEME["success"], THEME["warning"], THEME["danger"]]
        self.ram_label.setText(ram_labels[index])
        self.ram_label.setStyleSheet(f"color: {colors[index]}; font-size: 10px;")

        # Notify dashboard to update model and sync other pages
        if self.dashboard and hasattr(self.dashboard, "update_ai_model"):
            self.dashboard.update_ai_model(selected_model)
            self.chat_area.append(
                f"<b><span style='color: {THEME['primary']}'>System:</span></b> AI model switched to {selected_model}"
            )
            # Sync AI Mentor page if available
            if hasattr(self.dashboard, "ai_mentor_page") and self.dashboard.ai_mentor_page:
                self.dashboard.ai_mentor_page.set_model(index)

    def set_model(self, index):
        """Set model from external source (sync from AI Mentor page)."""
        # Block signals to prevent loop and duplicate messages
        self.model_selector.blockSignals(True)
        self.model_selector.setCurrentIndex(index)
        self.model_selector.blockSignals(False)

    def apply_theme(self):
        """Re-apply current theme to forensic panel components."""
        from src.ui.theme import THEME

        # Update model selector
        if hasattr(self, "model_selector"):
            self.model_selector.setStyleSheet(f"""
                QComboBox {{
                    background-color: {THEME['bg_card']};
                    border: 1px solid {THEME['border']};
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 8px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
            """)

        # Update RAM indicator
        if hasattr(self, "ram_label"):
            self.ram_label.setStyleSheet(f"color: {THEME['success']}; font-size: 10px;")

        # Update chat area
        if hasattr(self, "chat_area"):
            self.chat_area.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {THEME['bg_dark']};
                    border: 1px solid {THEME['border']};
                    border-radius: 8px;
                    color: {THEME['text_primary']};
                    padding: 10px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
            """)

    def _show_model_help(self):
        """Show help dialog for selecting the best AI model based on RAM."""
        from PyQt6.QtWidgets import QDialog, QTextEdit, QVBoxLayout

        dialog = QDialog(self)
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

        help_content = """<h2 style='color: #2DD4BF;'>AI Model Selection Guide</h2>

<h3 style='color: #F97316;'>How to Check Your RAM</h3>
<p><b>Mac:</b> Click Apple menu → About This Mac → look for "Memory"</p>
<p><b>Windows:</b> Press Win+Pause/Break or Settings → System → About</p>

<h3 style='color: #2DD4BF;'>Choose Your Model</h3>
<table border='0' cellpadding='5'>
<tr style='color: #22C55E;'><td><b>⚡ 8GB</b></td><td>llama3.2:1b (~1GB)</td><td>Fast, basic answers</td></tr>
<tr style='color: #22C55E;'><td><b>⚡ 8GB+</b></td><td>llama3.2:3b (~2GB)</td><td>Balanced speed/quality</td></tr>
<tr style='color: #F97316;'><td><b>⚡ 16GB+</b></td><td>llama3:8b (~4-5GB)</td><td>Good quality, slower</td></tr>
<tr style='color: #EF4444;'><td><b>⚡ 16GB++</b></td><td>phi4 (~6GB)</td><td>Best quality, very slow on 8GB</td></tr>
</table>

<h3 style='color: #F97316;'>Recommendations</h3>
<p><b>8GB Mac/PC:</b> Use <b>1b</b> for speed or <b>3b</b> if you close other apps</p>
<p><b>16GB Mac/PC:</b> Use <b>3b</b> or <b>8b</b> for better answers</p>
<p><b>32GB+ Mac/PC:</b> Use <b>phi4</b> for professional-grade analysis</p>

<h3 style='color: #EF4444;'>Warning Signs</h3>
<p>• Rainbow wheel / spinning cursor = RAM full, switch to smaller model</p>
<p>• Long delays (>30 sec) = model too big for your system</p>
<p>• App freezes = immediately switch to 1b or use --no-ai mode</p>

<p style='color: #6B7280; font-size: 11px; margin-top: 20px;'><i>Tip: Start with 3b and only go higher if responses are fast enough.</i></p>"""

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
            self.chat_area.append("<b><span style='color: #EF4444'>System:</span></b> AI disabled")
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
                self.chat_area.append(
                    "<b><span style='color: #22C55E'>System:</span></b> AI enabled - connected to Ollama"
                )
            except Exception as e:
                self.chat_area.append(
                    f"<b><span style='color: #EF4444'>System:</span></b> Failed to enable AI: {str(e)}"
                )
