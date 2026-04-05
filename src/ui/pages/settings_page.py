"""Settings & Privacy page implementation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QStackedWidget, QLineEdit, QComboBox, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.theme import THEME


class SettingsPage:
    """Settings & Privacy page with tabbed navigation."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.settings_nav = None
        self.settings_content = None
        
    def create(self):
        """Create and return the settings page widget."""
        settings_page = QWidget()
        settings_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Main horizontal layout
        main_layout = QHBoxLayout(settings_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # LEFT: Navigation List
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_header']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(10)
        
        # Settings title
        settings_title = QLabel("SETTINGS")
        settings_title.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        settings_title.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(settings_title)
        
        # Navigation list
        self.settings_nav = QListWidget()
        self.settings_nav.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 13px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px 15px;
                border-radius: 8px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QListWidget::item:hover {{
                background-color: {THEME['bg_card']};
            }}
        """)
        self.settings_nav.addItem("Network")
        self.settings_nav.addItem("AI Brain")
        self.settings_nav.addItem("Security")
        self.settings_nav.addItem("Privacy")
        nav_layout.addWidget(self.settings_nav)
        nav_layout.addStretch()
        
        main_layout.addWidget(nav_widget)
        
        # RIGHT: Content Stack
        self.settings_content = QStackedWidget()
        self.settings_content.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        
        # Add settings tabs
        self.settings_content.addWidget(self._create_network_tab())
        self.settings_content.addWidget(self._create_ai_tab())
        self.settings_content.addWidget(self._create_security_tab())
        self.settings_content.addWidget(self._create_privacy_tab())
        
        # Connect navigation to content
        self.settings_nav.currentRowChanged.connect(self.settings_content.setCurrentIndex)
        
        main_layout.addWidget(self.settings_content, stretch=1)
        
        return settings_page
        
    def _create_network_tab(self):
        """Create the Network settings tab."""
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)
        network_layout.setContentsMargins(30, 30, 30, 30)
        network_layout.setSpacing(20)
        
        network_header = QLabel("Network Settings")
        network_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        network_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        network_layout.addWidget(network_header)
        
        # Active Interface dropdown
        interface_container = QWidget()
        interface_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        interface_layout = QVBoxLayout(interface_container)
        
        interface_label = QLabel("Active Interface")
        interface_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        interface_label.setStyleSheet(f"color: {THEME['text_primary']};")
        interface_layout.addWidget(interface_label)
        
        interface_combo = QComboBox()
        interface_combo.addItems(["eth0", "wlan0", "lo", "en0", "Wi-Fi", "Ethernet"])
        interface_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
                min-width: 200px;
            }}
        """)
        interface_layout.addWidget(interface_combo)
        network_layout.addWidget(interface_container)
        
        # Network range input
        range_container = QWidget()
        range_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        range_layout = QVBoxLayout(range_container)
        
        range_label = QLabel("Network Range")
        range_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        range_label.setStyleSheet(f"color: {THEME['text_primary']};")
        range_layout.addWidget(range_label)
        
        range_input = QLineEdit("172.16.40.0/24")
        range_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
            }}
        """)
        range_layout.addWidget(range_input)
        network_layout.addWidget(range_container)
        network_layout.addStretch()
        
        return network_tab
        
    def _create_ai_tab(self):
        """Create the AI Brain settings tab."""
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        ai_layout.setContentsMargins(30, 30, 30, 30)
        ai_layout.setSpacing(20)
        
        ai_header = QLabel("AI Brain Settings")
        ai_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        ai_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        ai_layout.addWidget(ai_header)
        
        # Explanation Detail slider
        explanation_container = QWidget()
        explanation_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        explanation_layout = QVBoxLayout(explanation_container)
        
        explanation_label = QLabel("Explanation Detail")
        explanation_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        explanation_label.setStyleSheet(f"color: {THEME['text_primary']};")
        explanation_layout.addWidget(explanation_label)
        
        explanation_slider = QSlider(Qt.Orientation.Horizontal)
        explanation_slider.setRange(1, 5)
        explanation_slider.setValue(3)
        explanation_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {THEME['border']};
                height: 8px;
                background: {THEME['bg_card']};
                border-radius: 4px;
            }}
            QSlider::sub-page:horizontal {{
                background: {THEME['primary']};
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {THEME['primary']};
                width: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }}
        """)
        explanation_layout.addWidget(explanation_slider)
        ai_layout.addWidget(explanation_container)
        
        # Local Model toggle
        local_model_container = QWidget()
        local_model_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        local_model_layout = QHBoxLayout(local_model_container)
        
        local_model_label = QLabel("Use Local Model")
        local_model_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        local_model_label.setStyleSheet(f"color: {THEME['text_primary']};")
        local_model_layout.addWidget(local_model_label)
        local_model_layout.addStretch()
        
        local_model_toggle = QCheckBox()
        local_model_toggle.setChecked(True)
        local_model_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        local_model_layout.addWidget(local_model_toggle)
        ai_layout.addWidget(local_model_container)
        ai_layout.addStretch()
        
        return ai_tab
        
    def _create_security_tab(self):
        """Create the Security settings tab."""
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setContentsMargins(30, 30, 30, 30)
        security_layout.setSpacing(20)
        
        security_header = QLabel("Security Settings")
        security_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        security_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        security_layout.addWidget(security_header)
        
        # Sensitivity slider
        sensitivity_container = QWidget()
        sensitivity_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        sensitivity_layout = QVBoxLayout(sensitivity_container)
        
        sensitivity_label = QLabel("Detection Sensitivity")
        sensitivity_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        sensitivity_label.setStyleSheet(f"color: {THEME['text_primary']};")
        sensitivity_layout.addWidget(sensitivity_label)
        
        sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        sensitivity_slider.setRange(0, 100)
        sensitivity_slider.setValue(75)
        sensitivity_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {THEME['border']};
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {THEME['danger']}, stop:0.5 {THEME['warning']}, stop:1 {THEME['success']});
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {THEME['primary']};
                width: 18px;
                border-radius: 9px;
                margin: -5px 0;
            }}
        """)
        sensitivity_layout.addWidget(sensitivity_slider)
        security_layout.addWidget(sensitivity_container)
        
        # Auto-block toggle
        autoblock_container = QWidget()
        autoblock_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        autoblock_layout = QHBoxLayout(autoblock_container)
        
        autoblock_label = QLabel("Auto-Block Threats")
        autoblock_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        autoblock_label.setStyleSheet(f"color: {THEME['text_primary']};")
        autoblock_layout.addWidget(autoblock_label)
        autoblock_layout.addStretch()
        
        autoblock_toggle = QCheckBox()
        autoblock_toggle.setChecked(True)
        autoblock_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        autoblock_layout.addWidget(autoblock_toggle)
        security_layout.addWidget(autoblock_container)
        security_layout.addStretch()
        
        return security_tab
        
    def _create_privacy_tab(self):
        """Create the Privacy settings tab."""
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout(privacy_tab)
        privacy_layout.setContentsMargins(30, 30, 30, 30)
        privacy_layout.setSpacing(20)
        
        privacy_header = QLabel("Privacy Settings")
        privacy_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        privacy_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        privacy_layout.addWidget(privacy_header)
        
        privacy_info = QLabel("NZ Privacy Act 2020 Compliance\n\nYour data is processed locally.\nNo data is sent to external servers.")
        privacy_info.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        privacy_info.setStyleSheet(f"color: {THEME['text_secondary']};")
        privacy_info.setWordWrap(True)
        privacy_layout.addWidget(privacy_info)
        privacy_layout.addStretch()
        
        return privacy_tab
