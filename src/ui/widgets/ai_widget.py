"""AI Widget for main dashboard with model selector."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.theme import THEME


class AIWidget(QWidget):
    """AI Assistant widget with model selector for main dashboard."""
    
    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.current_model = "llama3.2:3b"  # Default model
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the AI widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header
        header = QLabel("AI Assistant")
        header.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        header.setStyleSheet(f"color: {THEME['primary']}; font-weight: bold;")
        layout.addWidget(header)
        
        # Model selector
        model_container = QWidget()
        model_layout = QHBoxLayout(model_container)
        model_layout.setContentsMargins(5, 5, 5, 5)
        
        model_label = QLabel("Model:")
        model_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px;")
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
                border-radius: 4px;
                color: {THEME['text_primary']};
                padding: 4px;
                font-size: 11px;
                min-width: 200px;
            }}
        """)
        self.model_selector.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_selector)
        
        # RAM indicator
        self.ram_label = QLabel("8GB+")
        self.ram_label.setStyleSheet(f"color: {THEME['success']}; font-size: 10px;")
        model_layout.addWidget(self.ram_label)
        
        model_layout.addStretch()
        layout.addWidget(model_container)
        
        # Status
        status_label = QLabel(f"Model: {self.current_model}")
        status_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        layout.addWidget(status_label)
        
        layout.addStretch()
        
    def _on_model_changed(self, index):
        """Handle model selection change."""
        models = ["llama3.2:1b", "llama3.2:3b", "llama3:8b", "phi4"]
        selected_model = models[index]
        self.current_model = selected_model
        
        # Update RAM indicator
        ram_labels = ["8GB", "8GB+", "16GB+", "16GB++"]
        colors = [THEME['success'], THEME['success'], THEME['warning'], THEME['danger']]
        self.ram_label.setText(ram_labels[index])
        self.ram_label.setStyleSheet(f"color: {colors[index]}; font-size: 10px;")
        
        # Update status
        status_label = QLabel(f"Model: {selected_model}")
        status_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        
        # Notify dashboard of model change
        if self.dashboard and hasattr(self.dashboard, 'update_ai_model'):
            self.dashboard.update_ai_model(selected_model)
    
    def get_current_model(self):
        """Get current selected model."""
        return self.current_model
    
    def set_model(self, model_name):
        """Set model from external source."""
        models = ["llama3.2:1b", "llama3.2:3b", "llama3:8b", "phi4"]
        try:
            index = models.index(model_name)
            self.model_selector.setCurrentIndex(index)
            self.current_model = model_name
        except ValueError:
            pass  # Model not found, ignore
