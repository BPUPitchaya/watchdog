"""Settings & Privacy page implementation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QStackedWidget, QLineEdit, QComboBox, QSlider, QCheckBox,
    QPushButton, QMessageBox, QScrollArea, QListWidgetItem
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
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # LEFT: Navigation List
        nav_widget = QWidget()
        nav_widget.setFixedWidth(180)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 8px;
            }}
        """)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(10)
        
        # Settings title
        settings_title = QLabel("Settings")
        settings_title.setFont(QFont(THEME['font_mono'].strip("'"), 13))
        settings_title.setStyleSheet(f"color: {THEME['text_secondary']}; font-weight: 600; margin-bottom: 8px;")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        nav_layout.addWidget(settings_title)
        
        # Navigation list
        self.settings_nav = QListWidget()
        self.settings_nav.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-left: 2px solid transparent;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{
                background-color: {THEME['bg_dark']};
                border-left: 2px solid {THEME['primary']};
                color: {THEME['primary']};
            }}
            QListWidget::item:hover:!selected {{
                background-color: {THEME['bg_dark']};
                color: {THEME['text_primary']};
            }}
        """)
        self.settings_nav.addItem("Network")
        self.settings_nav.addItem("AI Brain")
        self.settings_nav.addItem("Notifications")
        self.settings_nav.addItem("System")
        self.settings_nav.addItem("Security")
        self.settings_nav.addItem("Privacy")
        self.settings_nav.addItem("Keyboard Shortcuts")
        nav_layout.addWidget(self.settings_nav)
        nav_layout.addStretch()
        
        main_layout.addWidget(nav_widget)
        
        # RIGHT: Content Stack
        self.settings_content = QStackedWidget()
        self.settings_content.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 8px;
            }}
        """)
        
        # Add settings tabs
        self.settings_content.addWidget(self._create_network_tab())
        self.settings_content.addWidget(self._create_ai_tab())
        self.settings_content.addWidget(self._create_alerts_tab())
        self.settings_content.addWidget(self._create_system_tab())
        self.settings_content.addWidget(self._create_security_tab())
        self.settings_content.addWidget(self._create_privacy_tab())
        self.settings_content.addWidget(self._create_keyboard_shortcuts_tab())
        
        # Connect navigation to content
        self.settings_nav.currentRowChanged.connect(self.settings_content.setCurrentIndex)
        
        main_layout.addWidget(self.settings_content, stretch=1)
        
        return settings_page
        
    def _create_network_tab(self):
        """Create the Network settings tab."""
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)
        network_layout.setContentsMargins(20, 20, 20, 20)
        network_layout.setSpacing(12)
        
        network_header = QLabel("Network")
        network_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        network_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        network_layout.addWidget(network_header)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Active Interface dropdown
        interface_container = QWidget()
        interface_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        interface_layout = QVBoxLayout(interface_container)
        interface_layout.setSpacing(8)
        
        interface_label = QLabel("Active Interface (Eyes of the Watchdog)")
        interface_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        interface_label.setStyleSheet(f"color: {THEME['text_primary']};")
        interface_layout.addWidget(interface_label)
        
        interface_combo = QComboBox()
        interface_combo.addItems(["eth0", "wlan0", "lo", "en0", "Wi-Fi", "Ethernet"])
        interface_combo.setMinimumHeight(35)
        interface_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 6px;
                font-family: {THEME['font_mono']};
                font-size: 11px;
                min-width: 200px;
            }}
        """)
        interface_layout.addWidget(interface_combo)
        scroll_layout.addWidget(interface_container)
        
        # Promiscuous Mode toggle
        promiscuous_container = QWidget()
        promiscuous_container.setMaximumHeight(50)
        promiscuous_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        promiscuous_layout = QHBoxLayout(promiscuous_container)
        promiscuous_layout.setSpacing(8)
        
        promiscuous_label = QLabel("Promiscuous Mode")
        promiscuous_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        promiscuous_label.setStyleSheet(f"color: {THEME['text_primary']};")
        promiscuous_layout.addWidget(promiscuous_label)
        promiscuous_layout.addStretch()
        
        promiscuous_toggle = QCheckBox()
        promiscuous_toggle.setChecked(False)
        promiscuous_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 35px;
                height: 18px;
                border-radius: 9px;
                background: {THEME['bg_card']};
                border: none;
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        promiscuous_layout.addWidget(promiscuous_toggle)
        scroll_layout.addWidget(promiscuous_container)
        
        # Ignore List (Whitelisting)
        ignore_container = QWidget()
        ignore_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        ignore_layout = QVBoxLayout(ignore_container)
        ignore_layout.setSpacing(8)
        
        ignore_label = QLabel("Ignore List (Whitelisting - Trusted IPs)")
        ignore_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        ignore_label.setStyleSheet(f"color: {THEME['text_primary']};")
        ignore_layout.addWidget(ignore_label)
        
        # IP List widget
        self.ignore_list = QListWidget()
        self.ignore_list.setMinimumHeight(100)
        self.ignore_list.setMaximumHeight(150)
        self.ignore_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 4px;
                font-family: {THEME['font_mono']};
                font-size: 10px;
            }}
            QListWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {THEME['border']};
            }}
            QListWidget::item:selected {{
                background-color: {THEME['primary']};
                color: white;
            }}
        """)
        # Add some sample IPs
        sample_ips = ["192.168.1.100", "10.0.0.50", "192.168.1.1"]
        for ip in sample_ips:
            item = QListWidgetItem(ip)
            self.ignore_list.addItem(item)
        ignore_layout.addWidget(self.ignore_list)
        
        # Add/Remove buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        add_ip_input = QLineEdit()
        add_ip_input.setPlaceholderText("Add IP address...")
        add_ip_input.setMinimumHeight(30)
        add_ip_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 4px;
                font-family: {THEME['font_mono']};
                font-size: 10px;
            }}
        """)
        button_layout.addWidget(add_ip_input, stretch=1)
        
        add_btn = QPushButton("Add")
        add_btn.setMinimumHeight(30)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 6px;
                color: white;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        button_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove")
        remove_btn.setMinimumHeight(30)
        remove_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 4px 12px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {THEME['bg_card']};
            }}
        """)
        button_layout.addWidget(remove_btn)
        
        ignore_layout.addLayout(button_layout)
        scroll_layout.addWidget(ignore_container)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        network_layout.addWidget(scroll_area, stretch=1)
        
        return network_tab
        
    def _create_ai_tab(self):
        """Create the AI Brain settings tab."""
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        ai_layout.setContentsMargins(20, 20, 20, 20)
        ai_layout.setSpacing(12)
        
        ai_header = QLabel("AI Brain")
        ai_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        ai_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        ai_layout.addWidget(ai_header)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Model Selection dropdown
        model_container = QWidget()
        model_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        model_layout = QVBoxLayout(model_container)
        model_layout.setSpacing(8)
        
        model_label = QLabel("AI Model Selection")
        model_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        model_label.setStyleSheet(f"color: {THEME['text_primary']};")
        model_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["Llama 3.2 (1B)", "Llama 3.2 (3B)", "Llama 3 (8B)", "Phi-4"])
        self.model_combo.setCurrentIndex(1)  # Default to 3B
        self.model_combo.setMinimumHeight(35)
        self.model_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 6px;
                font-family: {THEME['font_mono']};
                font-size: 11px;
                min-width: 200px;
            }}
        """)
        model_layout.addWidget(self.model_combo)
        
        # Apply button for model
        apply_model_btn = QPushButton("Apply Model")
        apply_model_btn.setMinimumHeight(35)
        apply_model_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 6px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        apply_model_btn.clicked.connect(self._on_model_changed)
        model_layout.addWidget(apply_model_btn)
        scroll_layout.addWidget(model_container)
        
        # Keep-Alive Timer slider
        keepalive_container = QWidget()
        keepalive_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        keepalive_layout = QVBoxLayout(keepalive_container)
        keepalive_layout.setSpacing(8)
        
        keepalive_label = QLabel("Keep-Alive Timer (minutes)")
        keepalive_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        keepalive_label.setStyleSheet(f"color: {THEME['text_primary']};")
        keepalive_layout.addWidget(keepalive_label)
        
        self.keepalive_slider = QSlider(Qt.Orientation.Horizontal)
        self.keepalive_slider.setRange(5, 60)
        self.keepalive_slider.setValue(30)
        self.keepalive_slider.setMinimumHeight(25)
        self.keepalive_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {THEME['bg_card']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {THEME['primary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {THEME['primary']};
                width: 14px;
                border-radius: 7px;
                margin: -4px 0;
            }}
        """)
        keepalive_layout.addWidget(self.keepalive_slider)
        
        self.keepalive_value_label = QLabel("30 minutes")
        self.keepalive_value_label.setFont(QFont(THEME['font_mono'].strip("'"), 9))
        self.keepalive_value_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        self.keepalive_slider.valueChanged.connect(self._on_keepalive_changed)
        keepalive_layout.addWidget(self.keepalive_value_label)
        scroll_layout.addWidget(keepalive_container)
        
        # Context Window slider
        context_container = QWidget()
        context_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        context_layout = QVBoxLayout(context_container)
        context_layout.setSpacing(8)
        
        context_label = QLabel("Context Window (tokens)")
        context_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        context_label.setStyleSheet(f"color: {THEME['text_primary']};")
        context_layout.addWidget(context_label)
        
        self.context_slider = QSlider(Qt.Orientation.Horizontal)
        self.context_slider.setRange(512, 4096)
        self.context_slider.setValue(1024)
        self.context_slider.setMinimumHeight(25)
        self.context_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {THEME['bg_card']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {THEME['primary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {THEME['primary']};
                width: 14px;
                border-radius: 7px;
                margin: -4px 0;
            }}
        """)
        context_layout.addWidget(self.context_slider)
        
        self.context_value_label = QLabel("1024 tokens")
        self.context_value_label.setFont(QFont(THEME['font_mono'].strip("'"), 9))
        self.context_value_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        self.context_slider.valueChanged.connect(self._on_context_changed)
        context_layout.addWidget(self.context_value_label)
        scroll_layout.addWidget(context_container)
        
        # Explanation Detail slider (existing)
        explanation_container = QWidget()
        explanation_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        explanation_layout = QVBoxLayout(explanation_container)
        explanation_layout.setSpacing(8)
        
        explanation_label = QLabel("Explanation Detail")
        explanation_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        explanation_label.setStyleSheet(f"color: {THEME['text_primary']};")
        explanation_layout.addWidget(explanation_label)
        
        explanation_slider = QSlider(Qt.Orientation.Horizontal)
        explanation_slider.setRange(1, 5)
        explanation_slider.setValue(3)
        explanation_slider.setMinimumHeight(25)
        explanation_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {THEME['bg_card']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {THEME['primary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {THEME['primary']};
                width: 14px;
                border-radius: 7px;
                margin: -4px 0;
            }}
        """)
        explanation_layout.addWidget(explanation_slider)
        scroll_layout.addWidget(explanation_container)
        
        # Local Model toggle (existing)
        local_model_container = QWidget()
        local_model_container.setMaximumHeight(50)
        local_model_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        local_model_layout = QHBoxLayout(local_model_container)
        local_model_layout.setSpacing(8)
        
        local_model_label = QLabel("Use Local Model")
        local_model_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        local_model_label.setStyleSheet(f"color: {THEME['text_primary']};")
        local_model_layout.addWidget(local_model_label)
        local_model_layout.addStretch()
        
        local_model_toggle = QCheckBox()
        local_model_toggle.setChecked(True)
        local_model_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 35px;
                height: 18px;
                border-radius: 9px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        local_model_layout.addWidget(local_model_toggle)
        scroll_layout.addWidget(local_model_container)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        ai_layout.addWidget(scroll_area, stretch=1)
        
        return ai_tab
        
    def _create_alerts_tab(self):
        """Create the Alerts & Notifications settings tab."""
        alerts_tab = QWidget()
        alerts_layout = QVBoxLayout(alerts_tab)
        alerts_layout.setContentsMargins(20, 20, 20, 20)
        alerts_layout.setSpacing(12)
        
        alerts_header = QLabel("Notifications")
        alerts_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        alerts_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        alerts_layout.addWidget(alerts_header)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Risk Threshold slider
        risk_container = QWidget()
        risk_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        risk_layout = QVBoxLayout(risk_container)
        risk_layout.setSpacing(8)
        
        risk_label = QLabel("Risk Threshold (Desktop Notification Trigger)")
        risk_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        risk_label.setStyleSheet(f"color: {THEME['text_primary']};")
        risk_layout.addWidget(risk_label)
        
        self.risk_slider = QSlider(Qt.Orientation.Horizontal)
        self.risk_slider.setRange(1, 5)
        self.risk_slider.setValue(3)
        self.risk_slider.setMinimumHeight(25)
        self.risk_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: none;
                height: 6px;
                background: {THEME['bg_card']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background: {THEME['primary']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 2px solid {THEME['primary']};
                width: 14px;
                border-radius: 7px;
                margin: -4px 0;
            }}
        """)
        risk_layout.addWidget(self.risk_slider)
        
        self.risk_value_label = QLabel("Medium (Level 3)")
        self.risk_value_label.setFont(QFont(THEME['font_mono'].strip("'"), 9))
        self.risk_value_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        self.risk_slider.valueChanged.connect(self._on_risk_changed)
        risk_layout.addWidget(self.risk_value_label)
        scroll_layout.addWidget(risk_container)
        
        # Sound Alerts toggle
        sound_container = QWidget()
        sound_container.setMaximumHeight(50)
        sound_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        sound_layout = QHBoxLayout(sound_container)
        sound_layout.setSpacing(8)
        
        sound_label = QLabel("Sound Alerts (Cyber Alert Sound)")
        sound_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        sound_label.setStyleSheet(f"color: {THEME['text_primary']};")
        sound_layout.addWidget(sound_label)
        sound_layout.addStretch()
        
        sound_toggle = QCheckBox()
        sound_toggle.setChecked(True)
        sound_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 35px;
                height: 18px;
                border-radius: 9px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        sound_layout.addWidget(sound_toggle)
        scroll_layout.addWidget(sound_container)
        
        # Log Retention setting
        retention_container = QWidget()
        retention_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        retention_layout = QVBoxLayout(retention_container)
        retention_layout.setSpacing(8)
        
        retention_label = QLabel("Log Retention (Days to Keep Forensic Data)")
        retention_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        retention_label.setStyleSheet(f"color: {THEME['text_primary']};")
        retention_layout.addWidget(retention_label)
        
        retention_input = QLineEdit()
        retention_input.setText("30")
        retention_input.setMinimumHeight(35)
        retention_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 6px;
                font-family: {THEME['font_mono']};
                font-size: 11px;
            }}
        """)
        retention_layout.addWidget(retention_input)
        
        retention_hint = QLabel("Old packets will be automatically deleted after this period")
        retention_hint.setFont(QFont(THEME['font_mono'].strip("'"), 9))
        retention_hint.setStyleSheet(f"color: {THEME['text_secondary']};")
        retention_layout.addWidget(retention_hint)
        scroll_layout.addWidget(retention_container)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        alerts_layout.addWidget(scroll_area, stretch=1)
        
        return alerts_tab
        
    def _create_system_tab(self):
        """Create the System settings tab."""
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        system_layout.setContentsMargins(20, 20, 20, 20)
        system_layout.setSpacing(12)
        
        system_header = QLabel("System")
        system_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        system_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        system_layout.addWidget(system_header)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Hardware Acceleration toggle
        gpu_container = QWidget()
        gpu_container.setMaximumHeight(50)
        gpu_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        gpu_layout = QHBoxLayout(gpu_container)
        gpu_layout.setSpacing(8)
        
        gpu_label = QLabel("Hardware Acceleration (GPU)")
        gpu_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        gpu_label.setStyleSheet(f"color: {THEME['text_primary']};")
        gpu_layout.addWidget(gpu_label)
        gpu_layout.addStretch()
        
        gpu_toggle = QCheckBox()
        gpu_toggle.setChecked(False)
        gpu_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 35px;
                height: 18px;
                border-radius: 9px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        gpu_layout.addWidget(gpu_toggle)
        scroll_layout.addWidget(gpu_container)
        
        # Theme Toggle
        theme_container = QWidget()
        theme_container.setMaximumHeight(50)
        theme_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
            }}
        """)
        theme_layout = QHBoxLayout(theme_container)
        theme_layout.setSpacing(8)
        
        theme_label = QLabel("Theme (Midnight / High Contrast)")
        theme_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        theme_label.setStyleSheet(f"color: {THEME['text_primary']};")
        theme_layout.addWidget(theme_label)
        theme_layout.addStretch()
        
        theme_toggle = QCheckBox()
        theme_toggle.setChecked(False)
        theme_toggle.setStyleSheet(f"""
            QCheckBox::indicator {{
                width: 35px;
                height: 18px;
                border-radius: 9px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
            }}
        """)
        theme_layout.addWidget(theme_toggle)
        scroll_layout.addWidget(theme_container)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        system_layout.addWidget(scroll_area, stretch=1)
        
        return system_tab
        
    def _create_security_tab(self):
        """Create the Security settings tab."""
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setContentsMargins(20, 20, 20, 20)
        security_layout.setSpacing(12)
        
        security_header = QLabel("Security")
        security_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        security_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        security_layout.addWidget(security_header)
        
        # Sensitivity slider
        sensitivity_container = QWidget()
        sensitivity_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 12px;
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
                border: none;
                border-radius: 8px;
                padding: 12px;
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
        privacy_layout.setContentsMargins(20, 20, 20, 20)
        privacy_layout.setSpacing(12)
        
        privacy_header = QLabel("Privacy")
        privacy_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        privacy_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        privacy_layout.addWidget(privacy_header)
        
        privacy_info = QLabel("NZ Privacy Act 2020 Compliance\n\nYour data is processed locally.\nNo data is sent to external servers.")
        privacy_info.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        privacy_info.setStyleSheet(f"color: {THEME['text_secondary']};")
        privacy_info.setWordWrap(True)
        privacy_layout.addWidget(privacy_info)
        privacy_layout.addStretch()
        
        return privacy_tab

    def _create_appearance_tab(self):
        """Create the Appearance settings tab."""
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        appearance_layout.setContentsMargins(20, 20, 20, 20)
        appearance_layout.setSpacing(12)
        
        appearance_header = QLabel("Appearance")
        appearance_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        appearance_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        appearance_layout.addWidget(appearance_header)
        
        # Font size slider
        font_container = QWidget()
        font_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        font_layout = QVBoxLayout(font_container)
        
        font_label = QLabel("Interface Scale")
        font_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        font_label.setStyleSheet(f"color: {THEME['text_primary']};")
        font_layout.addWidget(font_label)
        
        font_slider = QSlider(Qt.Orientation.Horizontal)
        font_slider.setRange(80, 150)
        font_slider.setValue(100)
        font_slider.setStyleSheet(f"""
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
        font_layout.addWidget(font_slider)
        appearance_layout.addWidget(font_container)
        
        # Animations toggle
        anim_container = QWidget()
        anim_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        anim_layout = QHBoxLayout(anim_container)
        
        anim_label = QLabel("Enable Animations")
        anim_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        anim_label.setStyleSheet(f"color: {THEME['text_primary']};")
        anim_layout.addWidget(anim_label)
        anim_layout.addStretch()
        
        anim_toggle = QCheckBox()
        anim_toggle.setChecked(True)
        anim_toggle.setStyleSheet(f"""
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
        anim_layout.addWidget(anim_toggle)
        appearance_layout.addWidget(anim_container)
        
        appearance_layout.addStretch()
        
        return appearance_tab

    def _create_keyboard_shortcuts_tab(self):
        """Create the Keyboard Shortcuts settings tab."""
        shortcuts_tab = QWidget()
        shortcuts_layout = QVBoxLayout(shortcuts_tab)
        shortcuts_layout.setContentsMargins(20, 20, 20, 20)
        shortcuts_layout.setSpacing(12)
        
        shortcuts_header = QLabel("Keyboard Shortcuts")
        shortcuts_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        shortcuts_header.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600; margin-bottom: 8px;")
        shortcuts_layout.addWidget(shortcuts_header)
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # Keyboard shortcuts info
        info_label = QLabel("Learn the keyboard shortcuts to navigate Watchdog quickly and efficiently.")
        info_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        info_label.setStyleSheet(f"color: {THEME['text_secondary']}; margin-bottom: 10px;")
        info_label.setWordWrap(True)
        scroll_layout.addWidget(info_label)
        
        # Shortcuts table
        shortcuts_container = QWidget()
        shortcuts_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        shortcuts_table_layout = QVBoxLayout(shortcuts_container)
        
        # Shortcut items
        shortcuts = [
            ("Ctrl+Q", "Quit application", "Close Watchdog and exit"),
            ("Ctrl+S", "Navigate to Settings", "Jump directly to the Settings page"),
            ("F11", "Toggle Fullscreen", "Switch between windowed and fullscreen mode"),
        ]
        
        for key, action, description in shortcuts:
            shortcut_item = QWidget()
            shortcut_item.setStyleSheet(f"""
                QWidget {{
                    background-color: {THEME['bg_card']};
                    border: 1px solid {THEME['border']};
                    border-radius: 6px;
                    padding: 12px;
                }}
            """)
            shortcut_layout = QHBoxLayout(shortcut_item)
            shortcut_layout.setSpacing(15)
            
            # Key badge
            key_label = QLabel(key)
            key_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
            key_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {THEME['primary']};
                    color: white;
                    padding: 6px 12px;
                    border-radius: 4px;
                    font-weight: 600;
                }}
            """)
            key_label.setFixedWidth(80)
            shortcut_layout.addWidget(key_label)
            
            # Action and description
            action_desc_layout = QVBoxLayout()
            action_label = QLabel(action)
            action_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
            action_label.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600;")
            action_desc_layout.addWidget(action_label)
            
            desc_label = QLabel(description)
            desc_label.setFont(QFont(THEME['font_mono'].strip("'"), 10))
            desc_label.setStyleSheet(f"color: {THEME['text_secondary']};")
            desc_label.setWordWrap(True)
            action_desc_layout.addWidget(desc_label)
            
            shortcut_layout.addLayout(action_desc_layout)
            shortcut_layout.addStretch()
            
            shortcuts_table_layout.addWidget(shortcut_item)
        
        scroll_layout.addWidget(shortcuts_container)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        shortcuts_layout.addWidget(scroll_area)
        
        return shortcuts_tab

    def _on_model_changed(self, index=None):
        """Handle AI model selection change."""
        try:
            # Map display names to model identifiers
            model_map = {
                'Llama 3.2 (1B)': 'llama3.2:1b',
                'Llama 3.2 (3B)': 'llama3.2:3b',
                'Llama 3 (8B)': 'llama3:8b',
                'Phi-4': 'phi4'
            }
            
            # Get current text from combo box
            current_text = self.model_combo.currentText()
            selected = model_map.get(current_text)
            selected_name = current_text
            
            if not selected:
                print(f"ERROR: Unknown model name: {current_text}")
                return
            
            # Show confirmation dialog
            confirm = QMessageBox(self.dashboard)
            confirm.setWindowTitle("Confirm Model Change")
            confirm.setText(f"Switch to '{selected_name}'?")
            confirm.setInformativeText("The AI client will be reinitialized with the new model.")
            confirm.setIcon(QMessageBox.Icon.Question)
            confirm.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirm.setDefaultButton(QMessageBox.StandardButton.Yes)
            confirm.setStyleSheet(f"""
                QMessageBox {{
                    background-color: {THEME['bg_dark']};
                }}
                QLabel {{
                    color: {THEME['text_primary']};
                    font-size: 13px;
                }}
                QPushButton {{
                    background-color: {THEME['primary']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {THEME['secondary']};
                }}
            """)
            
            reply = confirm.exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                # Update AI client with new model using dashboard method to sync with AI widget
                if hasattr(self.dashboard, 'update_ai_model'):
                    self.dashboard.update_ai_model(selected)
                    print(f"AI model changed to: {selected}")
                else:
                    # Fallback: directly update AI client
                    if hasattr(self.dashboard, 'ai_client') and self.dashboard.ai_client:
                        self.dashboard.ai_client.set_model(selected)
                        print(f"AI model changed to: {selected}")
                    else:
                        # Reinitialize AI client with new model
                        from src.ai.ollama_client import OllamaClient
                        self.dashboard.ai_client = OllamaClient(model=selected)
                        print(f"AI client reinitialized with model: {selected}")
        except Exception as e:
            print(f"Error changing AI model: {e}")

    def _on_keepalive_changed(self, value):
        """Handle Keep-Alive Timer slider change."""
        self.keepalive_value_label.setText(f"{value} minutes")
        if hasattr(self.dashboard, 'ai_client') and self.dashboard.ai_client:
            self.dashboard.ai_client.set_keep_alive(value)

    def _on_context_changed(self, value):
        """Handle Context Window slider change."""
        self.context_value_label.setText(f"{value} tokens")
        if hasattr(self.dashboard, 'ai_client') and self.dashboard.ai_client:
            self.dashboard.ai_client.set_context_window(value)

    def set_model(self, model_name):
        """Set model from external source (e.g., AI widget)."""
        models = ['llama3.2:1b', 'llama3.2:3b', 'llama3:8b', 'phi4']
        try:
            index = models.index(model_name)
            # Block signals to prevent loop
            self.model_combo.blockSignals(True)
            self.model_combo.setCurrentIndex(index)
            self.model_combo.blockSignals(False)
        except ValueError:
            print(f"Model {model_name} not found in settings page")

    def _on_risk_changed(self, value):
        """Handle Risk Threshold slider change."""
        risk_levels = ["Low (Level 1)", "Low-Medium (Level 2)", "Medium (Level 3)", "Medium-High (Level 4)", "High (Level 5)"]
        self.risk_value_label.setText(risk_levels[value - 1])

    def apply_theme(self):
        """Re-apply current theme to settings page components."""
        from src.ui.theme import THEME
        from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QSlider, QCheckBox, QPushButton, QLineEdit, QListWidget
        
        # Update settings navigation
        if hasattr(self, 'settings_nav'):
            self.settings_nav.setStyleSheet(f"""
                QListWidget {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 8px;
                    padding: 8px;
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
        
        # Update settings content container
        if hasattr(self, 'settings_content'):
            self.settings_content.setStyleSheet(f"""
                QStackedWidget {{
                    background-color: {THEME['bg_card']};
                    border: 1px solid {THEME['border']};
                    border-radius: 12px;
                }}
            """)
        
        # Recursively update all widgets in the settings content
        if hasattr(self, 'settings_content'):
            self._update_widget_theme(self.settings_content)
    
    def _update_widget_theme(self, widget):
        """Recursively update theme for all child widgets."""
        from src.ui.theme import THEME
        from PyQt6.QtWidgets import QWidget, QLabel, QComboBox, QSlider, QCheckBox, QPushButton, QLineEdit, QListWidget
        
        # Update the widget itself if it has a specific type
        if isinstance(widget, QLabel):
            widget.setStyleSheet(f"color: {THEME['text_primary']};")
        elif isinstance(widget, QComboBox):
            widget.setStyleSheet(f"""
                QComboBox {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 6px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
            """)
        elif isinstance(widget, QSlider):
            widget.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 6px;
                    background: {THEME['bg_card']};
                    border-radius: 3px;
                }}
                QSlider::sub-page:horizontal {{
                    background: {THEME['primary']};
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background: white;
                    border: 2px solid {THEME['primary']};
                    width: 14px;
                    border-radius: 7px;
                    margin: -4px 0;
                }}
            """)
        elif isinstance(widget, QCheckBox):
            widget.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 35px;
                    height: 18px;
                    border-radius: 9px;
                    background: {THEME['bg_card']};
                    border: none;
                }}
                QCheckBox::indicator:checked {{
                    background: {THEME['primary']};
                }}
            """)
        elif isinstance(widget, QPushButton):
            if widget.text() in ["Add", "Remove", "Apply"]:
                widget.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {THEME['primary']};
                        border: none;
                        border-radius: 6px;
                        color: white;
                        padding: 4px 12px;
                        font-weight: bold;
                        font-size: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {THEME['secondary']};
                    }}
                """)
            else:
                widget.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        border: none;
                        border-radius: 6px;
                        color: {THEME['text_primary']};
                        padding: 4px 12px;
                        font-weight: bold;
                        font-size: 10px;
                    }}
                    QPushButton:hover {{
                        background-color: {THEME['bg_card']};
                    }}
                """)
        elif isinstance(widget, QLineEdit):
            widget.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 6px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
            """)
        elif isinstance(widget, QListWidget):
            widget.setStyleSheet(f"""
                QListWidget {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 4px;
                    font-family: {THEME['font_mono']};
                    font-size: 10px;
                }}
                QListWidget::item {{
                    padding: 4px;
                    border-bottom: 1px solid {THEME['border']};
                }}
                QListWidget::item:selected {{
                    background-color: {THEME['primary']};
                    color: white;
                }}
            """)
        elif isinstance(widget, QWidget):
            # Check if it's a container with the dark background style
            current_style = widget.styleSheet()
            if 'background-color: {THEME' in current_style or 'background-color: #0' in current_style or 'background-color: #F' in current_style:
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {THEME['bg_dark']};
                        border: 1px solid {THEME['border']};
                        border-radius: 10px;
                        padding: 12px;
                    }}
                """)
        
        # Recursively update children
        if hasattr(widget, 'children'):
            for child in widget.children():
                if isinstance(child, QWidget):
                    self._update_widget_theme(child)       