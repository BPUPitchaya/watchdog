import sys
import os
import json
import datetime
import math
import random
import signal
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
    QScrollArea, QSplitter, QHeaderView, QTextEdit, QProgressBar,
    QStackedWidget, QDialog, QSizePolicy, QListWidget, QListWidgetItem, QMessageBox, QSlider, QFrame, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QRect, QRectF, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPointF, QByteArray
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient, QRadialGradient, QPixmap, QIcon
from PyQt6.QtSvgWidgets import QSvgWidget

import joblib
import pandas as pd
import numpy as np
import psutil

from src.ml.feature_extractor import FeatureExtractor


def get_system_ram():
    """Get total system RAM in GB."""
    try:
        ram_gb = round(psutil.virtual_memory().total / (1024**3))
        return ram_gb
    except Exception:
        return None


def get_recommended_ai_model(ram_gb):
    """Recommend AI model based on available RAM."""
    if ram_gb is None:
        return "3b", "RAM detection failed - using 3b model"
    elif ram_gb < 8:
        return "1b", f"Low RAM ({ram_gb}GB) - Use 1b model for best performance"
    elif ram_gb < 16:
        return "3b", f"Good RAM ({ram_gb}GB) - 3b model recommended"
    else:
        return "phi4", f"High RAM ({ram_gb}GB) - Can use phi4 for best quality"

from src.ai.ollama_client import OllamaClient
from src.ai.prompts import GENERAL_PROMPT, EXPLANATION_PROMPT, TECHNICAL_ANALYSIS_PROMPT
from src.ai.utils import format_packet_log
from src.ui.theme import THEME
from src.ui.widgets import (
    ThreatGauge, StatusCore, SystemHealthGauge, RiskAnalysisGauge,
    CircularGaugeWidget, LiveTrafficWidget, ToastNotification,
    NetworkTopologyWidget, ForensicAssistantPanel, HelpDialog, HelpHotspot
)
from src.ui.pages import (
    LiveSentinelPage, ForensicVaultPage, AutonomousShieldPage,
    AIMentorPage, NetworkTopologyPage, SettingsPage, PlaceholderPage,
    ThreatEncyclopediaPage
)
from src.ui.help_content import PAGE_HELP_CONTENT

def signal_handler(sig, frame):
    QApplication.quit()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class AIWorker(QThread):
    """Worker thread for non-blocking AI queries with streaming."""
    chunk = pyqtSignal(str, str)  # (chunk, full_response_so_far)
    finished = pyqtSignal(str)     # Emits final AI response
    error = pyqtSignal(str)      # Emits error message
    
    def __init__(self, ai_client, prompt):
        super().__init__()
        self.ai_client = ai_client
        self.prompt = prompt
    
    def run(self):
        try:
            # Use streaming for real-time updates
            def on_chunk(chunk, full):
                self.chunk.emit(chunk, full)
            
            response = self.ai_client.query_stream(self.prompt, on_chunk)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(f"AI Error: {str(e)}")


class WatchdogDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WATCHDOG AI Dashboard")
        self.setGeometry(100, 100, 1200, 1000)

        # Check for --layout-only and --no-ai flags
        import sys
        self.layout_only = '--layout-only' in sys.argv
        self.no_ai = '--no-ai' in sys.argv

        # Initialize attributes
        self.model = None
        self.extractor = None
        self.ai_client = None
        self.previous_packets = 0
        self.toast = None  # Toast notification instance
        
        # Shared conversation history for AI chat sync
        self.conversation_history = []  # List of (sender, message) tuples
        self.ai_mentor_page = None  # Will be set in create_pages()

        # Load ML (skip if layout-only)
        if not self.layout_only:
            try:
                self.model = joblib.load('models/random_forest_model.pkl')
                self.extractor = FeatureExtractor()
            except Exception as e:
                print(f"Failed to load ML model: {e}")
                self.model = None
                self.extractor = None

            # Initialize AI client (skip if --no-ai flag)
            if not self.no_ai:
                try:
                    self.ai_client = OllamaClient()
                except Exception as e:
                    print(f"Failed to initialize AI: {e}")
                    self.ai_client = None

        # Create UI components
        self.create_ui()

        # Timer for auto-update (skip in layout-only)
        if not self.layout_only:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_ui)
            self.timer.start(1000)  # 1 seconds

        # Initial update (skip in layout-only)
        if not self.layout_only:
            self.update_ui()

    def create_ui(self):
        # Create page container first (full-size content area)
        self.page_container = QStackedWidget()
        self.page_container.setStyleSheet("background-color: transparent;")
        self.create_pages()
        
        # Create overlay container widget (this will be the central widget)
        self.overlay_container = QWidget()
        self.overlay_container.setStyleSheet("background-color: transparent;")
        
        from PyQt6.QtGui import QFontDatabase 

        #Load custom font
        font_path = os.path.join(os.path.dirname(__file__), "assets", "Orbitron-VariableFont_wght.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path) 
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            tech_font = font_families[0] if font_families else "Courier New"
        else:
            tech_font = "Courier New" 

        #Store it for use in stylesheets
        self.tech_font = tech_font
        # Page container fills the entire overlay but with left margin for sidebar
        self.page_container.setParent(self.overlay_container)
        self.page_container.setGeometry(70, 0, self.overlay_container.width() - 70, self.overlay_container.height())
        
        # Sidebar is a child of overlay container, positioned absolutely on the left
        self.nav_sidebar = QWidget(self.overlay_container)
        self.nav_sidebar.setGeometry(0, 0, 70, self.overlay_container.height())
        self.nav_sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_header']};
            }}
        """)
        self.sidebar_expanded = False
        
        # Set the overlay container as central widget
        self.setCentralWidget(self.overlay_container)
        
        # Handle resize of overlay container
        self.overlay_container.resizeEvent = self._on_overlay_resize

        nav_layout = QVBoxLayout(self.nav_sidebar)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(30)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Logo and title header container
        self.sidebar_header = QWidget()
        self.sidebar_header.setMinimumHeight(50)
        self.sidebar_header.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(self.sidebar_header)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        self.sidebar_logo = QLabel()
        self.sidebar_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.sidebar_logo.setPixmap(scaled_logo)
        else:
            self.sidebar_logo.setText("🐺")
            self.sidebar_logo.setStyleSheet("font-size: 20px;")
        self.sidebar_logo.setFixedSize(32, 32)
        header_layout.addWidget(self.sidebar_logo)
        
        # Sidebar title (hidden when collapsed)
        self.sidebar_title = QLabel("WATCHDOG")
        self.sidebar_title.setStyleSheet(f"""
            color: {THEME['primary']};
            font-family: '{self.tech_font}', 'Orbitron', 'Rajdhani', 'Courier New', sans-serif;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 2px;
        """)
        self.sidebar_title.setVisible(False)
        header_layout.addWidget(self.sidebar_title, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        
        nav_layout.addWidget(self.sidebar_header)

        # Navigation buttons with icons (Settings at bottom)
        nav_buttons = [
            ("DASHBOARD", "Real-time visibility and high-frequency packet monitoring", "dashboard icon.png"),
            ("FORENSIC LOG VAULT", "Translating complex metadata into human-readable advice", "log vault icon.png"),
            ("SECURITY CONTROL", "Managing the host firewall and setting AI confidence thresholds", "security control icon.png"),
            ("FORENSIC AI ASSISTANT", "A dedicated chat interface for Llama 4 Scout to provide education-active security guidance", "Ai assistant icon.png"),
            ("NETWORK TOPOLOGY", "Identifying all hardware on the LAN to resolve the visibility gap", "network topology icon.png"),
            ("THREAT ENCYCLOPEDIA", "Educational resource for understanding cyber threats and attack types", "encyclopedia icon.png"),
            ("SETTINGS AND PRIVACY", "Configuring Ollama and ensuring alignment with NZ Privacy Act 2020 principles", "setting icon.png")
        ]

        self.nav_button_group = []
        self.nav_button_labels = []  # Store text labels for show/hide
        self.nav_button_icons = []  # Store icon paths
        self.nav_item_containers = []  # Store container widgets
        self.nav_item_icon_labels = []  # Store icon labels
        self.nav_item_text_labels = []  # Store text labels
        
        for i, (label, tooltip, icon_file) in enumerate(nav_buttons):
            # Create container widget for icon + text
            container = QWidget()
            container.setFixedSize(70, 60)
            container.setCursor(Qt.CursorShape.PointingHandCursor)
            container.setToolTip(tooltip)
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(5, 0, 5, 0)
            container_layout.setSpacing(5)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Icon label (always visible)
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_path = os.path.join(os.path.dirname(__file__), "assets", icon_file)
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(48, 48)
            container_layout.addWidget(icon_label)
            
            # Text label (hidden when collapsed)
            text_label = QLabel(label)
            text_label.setStyleSheet(f"""
                color: {THEME['text_secondary']};
                font-size: 12px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
            """)
            text_label.setVisible(False)
            container_layout.addWidget(text_label)
            container_layout.addStretch()
            
            # Style container like a button
            container.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border: none;
                    border-radius: 15px;
                }}
                QWidget:hover {{
                    background-color: {THEME['bg_card']};
                }}
            """)
            
            # Make clickable
            container.mousePressEvent = lambda event, idx=i: self.switch_page(idx)
            
            nav_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)
            self.nav_button_group.append(container)
            self.nav_item_containers.append(container)
            self.nav_item_icon_labels.append(icon_label)
            self.nav_item_text_labels.append(text_label)
            
            # Store the full text and icon for later
            self.nav_button_labels.append(label)
            self.nav_button_icons.append(icon_path)

        # Set first button as active
        if self.nav_button_group:
            self._set_nav_active(0)

        # Set the overlay container as central widget
        self.setCentralWidget(self.overlay_container)

        # Enable hover events for sidebar (must be after sidebar is created)
        self.nav_sidebar.setMouseTracking(True)
        self.nav_sidebar.enterEvent = self._on_sidebar_enter
        self.nav_sidebar.leaveEvent = self._on_sidebar_leave
        
        # Timer for delayed collapse
        self.sidebar_collapse_timer = QTimer()
        self.sidebar_collapse_timer.setSingleShot(True)
        self.sidebar_collapse_timer.timeout.connect(self._contract_sidebar)

    def _add_help_button(self, page_widget, page_name):
        """Add floating help button to a page widget."""
        # Create wrapper widget
        wrapper = QWidget()
        wrapper.setLayout(QVBoxLayout())
        wrapper.layout().setContentsMargins(0, 0, 0, 0)
        wrapper.layout().setSpacing(0)
        
        # Add the page widget
        wrapper.layout().addWidget(page_widget)
        
        # Create help button
        help_btn = QPushButton("?")
        help_btn.setFixedSize(36, 36)
        help_btn.setToolTip(f"Learn about {page_name}")
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 18px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
                border: 2px solid white;
            }}
        """)
        
        # Position button in top-right corner
        help_btn.setParent(wrapper)
        help_btn.move(wrapper.width() - 50, 10)
        
        # Update position on resize
        def update_position():
            help_btn.move(wrapper.width() - 50, 10)
        wrapper.resizeEvent = lambda e: update_position()
        
        # Connect click to show help
        def show_help():
            hotspots = PAGE_HELP_CONTENT.get(page_name, [])
            if hotspots:
                dialog = HelpDialog(wrapper, page_name, hotspots)
                dialog.exec()
        
        help_btn.clicked.connect(show_help)
        
        return wrapper

    def create_pages(self):
        """Create all dashboard pages with help buttons."""
        # Page 0: Live Sentinel (main dashboard)
        live_sentinel = LiveSentinelPage(self)
        sentinel_widget = self._add_help_button(live_sentinel.create(), "Live Sentinel")
        self.page_container.addWidget(sentinel_widget)
        self.table = live_sentinel.table
        
        # Page 1: Forensic Vault
        forensic_vault = ForensicVaultPage(self)
        vault_widget = self._add_help_button(forensic_vault.create(), "Forensic Vault")
        self.page_container.addWidget(vault_widget)
        self.vault_table = forensic_vault.vault_table
        self.vault_search = forensic_vault.vault_search
        
        # Page 2: Autonomous Shield
        self.shield_page = AutonomousShieldPage(self)
        shield_widget = self._add_help_button(self.shield_page.create(), "Autonomous Shield")
        self.page_container.addWidget(shield_widget)
        self.blocked_ip_table = self.shield_page.blocked_ip_table
        
        # Page 3: AI Mentor
        self.ai_mentor_page = AIMentorPage(self)
        mentor_widget = self._add_help_button(self.ai_mentor_page.create(), "AI Mentor")
        self.page_container.addWidget(mentor_widget)
        
        # Page 4: Network Topology
        self.network_topology = NetworkTopologyPage(self)
        topology_widget = self._add_help_button(self.network_topology.create(), "Network Topology")
        self.page_container.addWidget(topology_widget)
        
        # Page 5: Threat Encyclopedia
        threat_encyclopedia = ThreatEncyclopediaPage(self)
        encyclopedia_widget = self._add_help_button(threat_encyclopedia.create(), "Threat Encyclopedia")
        self.page_container.addWidget(encyclopedia_widget)
        
        # Page 6: Settings & Privacy (at bottom of sidebar)
        settings_page = SettingsPage(self)
        settings_widget = self._add_help_button(settings_page.create(), "Settings")
        self.page_container.addWidget(settings_widget)
        self.settings_nav = settings_page.settings_nav
        self.settings_content = settings_page.settings_content
    
    def _on_overlay_resize(self, event):
        """Update page container and sidebar when overlay container is resized"""
        # Update page container with left margin for sidebar
        self.page_container.setGeometry(70, 0, self.overlay_container.width() - 70, self.overlay_container.height())
        # Update sidebar height
        self.nav_sidebar.setGeometry(
            self.nav_sidebar.x(), 
            0, 
            self.nav_sidebar.width(), 
            self.overlay_container.height()
        )

    def _on_sidebar_enter(self, event):
        """Expand sidebar when mouse enters"""
        self.sidebar_collapse_timer.stop()  # Cancel any pending collapse
        if not self.sidebar_expanded:
            self._expand_sidebar()

    def _on_sidebar_leave(self, event):
        """Start timer to collapse sidebar when mouse leaves"""
        if self.sidebar_expanded:
            self.sidebar_collapse_timer.start(300)  # 300ms delay before collapsing

    def _expand_sidebar(self):
        """Expand sidebar with coordinated animation - logo moves left, titles slide in"""
        self.sidebar_expanded = True
        target_width = 280
        
        # Create parallel animation group for coordinated animation
        self.animation_group = QParallelAnimationGroup()
        
        # 1. Animate sidebar width
        sidebar_anim = QPropertyAnimation(self.nav_sidebar, b"geometry")
        sidebar_anim.setDuration(350)
        sidebar_anim.setStartValue(self.nav_sidebar.geometry())
        sidebar_anim.setEndValue(QRect(0, 0, target_width, self.overlay_container.height()))
        sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation_group.addAnimation(sidebar_anim)
        
        # 2. Show title label
        self.sidebar_title.setVisible(True)
        
        # Connect to update button text and animate text labels when animation finishes
        self.animation_group.finished.connect(self._update_sidebar_buttons)
        self.animation_group.finished.connect(self._adjust_logo_alignment)
        
        # Start animation
        self.animation_group.start()

    def _contract_sidebar(self):
        """Contract sidebar with coordinated animation"""
        self.sidebar_expanded = False
        target_width = 70
        
        # Update buttons first (remove text, show icons)
        self._update_sidebar_buttons()
        
        # Hide title
        self.sidebar_title.setVisible(False)
        
        # Create parallel animation group
        self.animation_group = QParallelAnimationGroup()
        
        # Animate sidebar width
        sidebar_anim = QPropertyAnimation(self.nav_sidebar, b"geometry")
        sidebar_anim.setDuration(350)
        sidebar_anim.setStartValue(self.nav_sidebar.geometry())
        sidebar_anim.setEndValue(QRect(0, 0, target_width, self.overlay_container.height()))
        sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation_group.addAnimation(sidebar_anim)
        
        # Connect to adjust logo alignment when done
        self.animation_group.finished.connect(self._adjust_logo_alignment)
        
        # Start animation
        self.animation_group.start()

    def toggle_sidebar(self):
        """Toggle sidebar with coordinated animation"""
        if self.sidebar_expanded:
            self._contract_sidebar()
        else:
            self._expand_sidebar()
    
    def _update_sidebar_buttons(self):
        """Update button containers based on sidebar state"""
        for i, container in enumerate(self.nav_item_containers):
            text_label = self.nav_item_text_labels[i]
            if self.sidebar_expanded:
                # Wider container, text visible
                container.setFixedSize(260, 60)
                text_label.setVisible(True)
            else:
                # Narrow container, text hidden
                container.setFixedSize(70, 60)
                text_label.setVisible(False)
    
    def _adjust_logo_alignment(self):
        """Adjust logo alignment based on sidebar state"""
        header_layout = self.sidebar_header.layout()
        if self.sidebar_expanded:
            header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def _set_nav_active(self, index):
        """Set active navigation item styling"""
        for i, container in enumerate(self.nav_item_containers):
            text_label = self.nav_item_text_labels[i]
            if i == index:
                container.setStyleSheet(f"""
                    QWidget {{
                        background-color: {THEME['bg_card']};
                        border: none;
                        border-radius: 15px;
                    }}
                """)
                text_label.setStyleSheet(f"""
                    color: {THEME['primary']};
                    font-size: 12px;
                    font-weight: bold;
                    font-family: {THEME['font_mono']};
                """)
            else:
                container.setStyleSheet(f"""
                    QWidget {{
                        background-color: transparent;
                        border: none;
                        border-radius: 15px;
                    }}
                    QWidget:hover {{
                        background-color: {THEME['bg_card']};
                        border: none;
                    }}
                """)
                text_label.setStyleSheet(f"""
                    color: {THEME['text_secondary']};
                    font-size: 12px;
                    font-weight: bold;
                    font-family: {THEME['font_mono']};
                """)
    
    def _animate_text_labels_in(self):
        """Show text labels after expansion completes"""
        for container in self.nav_item_containers:
            container.setFixedSize(260, 60)
        for text_label in self.nav_item_text_labels:
            text_label.setVisible(True)

    def toggle_ai(self, checked):
        if checked:
            # Enable AI
            if not self.ai_client:
                try:
                    self.ai_client = OllamaClient()
                    print("AI features enabled")
                except Exception as e:
                    print(f"Failed to initialize AI: {e}")
                    self.ai_toggle_btn.setChecked(False)
                    return
        else:
            # Disable AI
            self.ai_client = None
            print("AI features disabled")
        
        # Update button text and style
        self.ai_toggle_btn.setText("AI: ON" if checked else "AI: OFF")
        
        # Refresh forensic vault to update AI availability
        if hasattr(self, 'vault_table'):
            self.load_flagged_incidents()

    def switch_page(self, index):
        # Update active navigation styling
        self._set_nav_active(index)
        
        # Switch to the selected page
        self.page_container.setCurrentIndex(index)
        
        # Load page-specific data
        if index == 1:  # Forensic Vault
            self.load_flagged_incidents()

    def load_flagged_incidents(self):
        # Load flagged incidents from packet_data.json
        try:
            with open('packet_data.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"packets": []}

        packets = data.get("packets", [])
        flagged_packets = []
        
        # Filter for packets with ATTACK classification or low confidence
        for packet in packets:
            if not self.layout_only and self.model and self.extractor:
                packet_data = {
                    'src_ip': packet.get('src_ip', '192.168.1.1'),
                    'dst_ip': packet.get('dst_ip', '10.0.0.1'),
                    'protocol': 6 if packet.get('protocol', 'TCP').upper() == 'TCP' else 17,
                    'length': packet.get('length', 100),
                    'src_port': packet.get('src_port', 12345),
                    'dst_port': packet.get('dst_port', 80),
                    'flags': packet.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                probabilities = self.model.predict_proba(features_array)[0]
                confidence = max(probabilities) * 100
                
                # Flag if ATTACK prediction OR low confidence (< 60%)
                if prediction == 1 or confidence < 60.0:
                    flagged_packets.append(packet)
        
        # Always add sample flagged incidents for demonstration
        sample_packets = [
            {
                'timestamp': 1773629875.0,
                'src_ip': '192.168.1.100',
                'dst_ip': '10.0.0.1',
                'protocol': 'TCP',
                'length': 1500,
                'src_port': 4444,
                'dst_port': 80,
                'flags': 'S',
                'count': 9999
            },
            {
                'timestamp': 1773629876.0,
                'src_ip': '10.10.10.10',
                'dst_ip': '172.16.40.172',
                'protocol': 'UDP',
                'length': 512,
                'src_port': 53,
                'dst_port': 53,
                'flags': '',
                'count': 10000
            },
            {
                'timestamp': 1773629877.0,
                'src_ip': '203.0.113.1',
                'dst_ip': '172.16.40.172',
                'protocol': 'TCP',
                'length': 2000,
                'src_port': 22,
                'dst_port': 22,
                'flags': 'SA',
                'count': 10001
            },
            {
                'timestamp': 1773629880.0,
                'src_ip': '192.168.1.105',
                'dst_ip': '10.0.0.5',
                'protocol': 'TCP',
                'length': 1200,
                'src_port': 3389,
                'dst_port': 443,
                'flags': 'PA',
                'count': 10002
            },
            {
                'timestamp': 1773629885.0,
                'src_ip': '172.16.40.50',
                'dst_ip': '192.168.1.1',
                'protocol': 'ICMP',
                'length': 64,
                'src_port': 0,
                'dst_port': 0,
                'flags': '',
                'count': 10003
            },
            {
                'timestamp': 1773629890.0,
                'src_ip': '198.51.100.22',
                'dst_ip': '172.16.40.172',
                'protocol': 'TCP',
                'length': 800,
                'src_port': 443,
                'dst_port': 8080,
                'flags': 'F',
                'count': 10004
            },
            {
                'timestamp': 1773629895.0,
                'src_ip': '192.168.1.200',
                'dst_ip': '10.0.0.50',
                'protocol': 'UDP',
                'length': 256,
                'src_port': 123,
                'dst_port': 123,
                'flags': '',
                'count': 10005
            },
            {
                'timestamp': 1773629900.0,
                'src_ip': '203.0.113.50',
                'dst_ip': '192.168.1.100',
                'protocol': 'TCP',
                'length': 1800,
                'src_port': 445,
                'dst_port': 139,
                'flags': 'S',
                'count': 10006
            },
            {
                'timestamp': 1773629905.0,
                'src_ip': '10.20.30.40',
                'dst_ip': '172.16.40.172',
                'protocol': 'TCP',
                'length': 500,
                'src_port': 25,
                'dst_port': 587,
                'flags': 'R',
                'count': 10007
            },
            {
                'timestamp': 1773629910.0,
                'src_ip': '198.51.100.100',
                'dst_ip': '10.0.0.100',
                'protocol': 'UDP',
                'length': 1024,
                'src_port': 161,
                'dst_port': 162,
                'flags': '',
                'count': 10008
            }
        ]
        
        # Add all samples to ensure vault has content
        flagged_packets.extend(sample_packets[:10])

        self.vault_table.setRowCount(len(flagged_packets))
        for i, packet in enumerate(flagged_packets):
            # Convert timestamp to human-readable format
            timestamp = packet.get('timestamp', 0)
            if isinstance(timestamp, (int, float)):
                dt = datetime.datetime.fromtimestamp(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp = "Unknown"
            
            src_ip = packet.get('src_ip', '')
            dst_ip = packet.get('dst_ip', '')
            protocol = packet.get('protocol', 'Other')
            
            # Always calculate confidence for all packets
            confidence = "N/A"
            threat_level = "UNKNOWN"
            if not self.layout_only and self.model and self.extractor:
                packet_data = {
                    'src_ip': src_ip or '192.168.1.1',
                    'dst_ip': dst_ip or '10.0.0.1',
                    'protocol': 6 if protocol.upper() == 'TCP' else 17,
                    'length': packet.get('length', 100),
                    'src_port': packet.get('src_port', 12345),
                    'dst_port': packet.get('dst_port', 80),
                    'flags': packet.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                probabilities = self.model.predict_proba(features_array)[0]
                confidence = f"{max(probabilities) * 100:.1f}%"
                threat_level = "ATTACK" if prediction == 1 else "NORMAL"
            
            ai_summary = "Click to view AI analysis" if not self.layout_only else "Sample flagged packet"

            self.vault_table.setItem(i, 0, QTableWidgetItem(timestamp))
            # Make IP columns stand out with cyan color
            src_ip_item = QTableWidgetItem(src_ip)
            src_ip_item.setForeground(QColor(THEME['primary']))
            src_ip_item.setFont(QFont(THEME['font_mono'].strip("'"), 12))
            self.vault_table.setItem(i, 1, src_ip_item)
            
            dst_ip_item = QTableWidgetItem(dst_ip)
            dst_ip_item.setForeground(QColor(THEME['primary']))
            dst_ip_item.setFont(QFont(THEME['font_mono'].strip("'"), 12))
            self.vault_table.setItem(i, 2, dst_ip_item)
            self.vault_table.setItem(i, 3, QTableWidgetItem(protocol))
            self.vault_table.setItem(i, 4, QTableWidgetItem(confidence))
            self.vault_table.setItem(i, 5, QTableWidgetItem(threat_level))
            self.vault_table.setItem(i, 6, QTableWidgetItem(ai_summary))
            
            # Add Action buttons - compact tool buttons
            action_widget = QWidget()
            action_widget.setStyleSheet("background-color: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(3, 2, 3, 2)
            action_layout.setSpacing(4)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            from PyQt6.QtWidgets import QToolButton
            
            # Block Source IP button
            block_src_btn = QToolButton()
            block_src_btn.setText("SRC")
            block_src_btn.setFixedSize(55, 28)
            block_src_btn.setStyleSheet("""
                QToolButton {
                    background-color: #DC2626;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #EF4444;
                }
            """)
            block_src_btn.setToolTip(f"Block Source: {src_ip}")
            block_src_btn.clicked.connect(lambda checked, ip=src_ip: self.block_ip_from_vault(ip))
            action_layout.addWidget(block_src_btn)
            
            # Block Destination IP button
            block_dst_btn = QToolButton()
            block_dst_btn.setText("DST")
            block_dst_btn.setFixedSize(55, 28)
            block_dst_btn.setStyleSheet("""
                QToolButton {
                    background-color: #06B6D4;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #0891B2;
                }
            """)
            block_dst_btn.setToolTip(f"Block Destination: {dst_ip}")
            block_dst_btn.clicked.connect(lambda checked, ip=dst_ip: self.block_ip_from_vault(ip))
            action_layout.addWidget(block_dst_btn)
            
            self.vault_table.setCellWidget(i, 7, action_widget)

    def filter_vault_table(self, text):
        # Filter table rows based on search text
        for row in range(self.vault_table.rowCount()):
            show_row = False
            for col in range(self.vault_table.columnCount()):
                item = self.vault_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.vault_table.setRowHidden(row, not show_row)

    def block_ip_from_vault(self, ip_address):
        """Block an IP address from the vault and add it to the shield"""
        if not ip_address or ip_address in ["", "Unknown"]:
            return
            
        reply = QMessageBox.question(
            self, 
            'Block IP Address', 
            f'Are you sure you want to block {ip_address}?\n\nThis will add it to the Autonomous Shield block list.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Add to blocked IPs set
            if hasattr(self, 'blocked_ips'):
                self.blocked_ips.add(ip_address)
            
            # Increment manual block counter
            if hasattr(self, 'manual_block_count'):
                self.manual_block_count += 1
            
            # Add to shield's blocked list widget if it exists
            if hasattr(self, 'blocked_list_widget'):
                # Check if already in list
                items = []
                for i in range(self.blocked_list_widget.count()):
                    item_text = self.blocked_list_widget.item(i).text()
                    existing_ip = item_text.split(" - ")[0]
                    items.append(existing_ip)
                
                if ip_address not in items:
                    # Add with description from vault
                    description = "Blocked from Forensic Vault"
                    self.blocked_list_widget.addItem(f"{ip_address} - {description}")
            
            # Update statistics
            self.shield_page.update_shield_statistics()
            
            # Show confirmation
            QMessageBox.information(self, "IP Blocked", 
                f"Successfully blocked {ip_address}\nAdded to Autonomous Shield block list.")
            
            print(f"Blocked IP from vault: {ip_address}")

    def show_forensic_analysis(self, item):
        # Show forensic analysis dialog for clicked item
        row = item.row()
        
        # Get packet data from table
        src_ip = self.vault_table.item(row, 1).text() if self.vault_table.item(row, 1) else ""
        dst_ip = self.vault_table.item(row, 2).text() if self.vault_table.item(row, 2) else ""
        protocol = self.vault_table.item(row, 3).text() if self.vault_table.item(row, 3) else ""
        
        # Create forensic analysis dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Forensic Analysis")
        dialog.setModal(True)
        dialog.setStyleSheet("background-color: #121212; color: white;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel(f"Forensic Analysis: {src_ip} → {dst_ip}")
        title.setFont(QFont("Courier New", 16))
        title.setStyleSheet("color: #00D4FF; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Analysis content
        if not self.layout_only and self.ai_client:
            packet_info = f"Source IP: {src_ip}\nDestination IP: {dst_ip}\nProtocol: {protocol}"
            analysis_text = self.process_command(f"analyze packet: {packet_info}")
        else:
            analysis_text = f"This packet from {src_ip} to {dst_ip} using {protocol} was flagged as potentially malicious.\n\nIn a full implementation, Llama 4 Scout would provide detailed forensic analysis explaining why this packet was considered a threat, including:\n\n• Protocol analysis\n• Traffic pattern recognition\n• Known threat signature matching\n• Behavioral anomaly detection"
        
        analysis_label = QLabel(analysis_text)
        analysis_label.setWordWrap(True)
        analysis_label.setStyleSheet("background-color: rgba(30, 41, 59, 0.8); padding: 20px; border-radius: 10px; border: 1px solid #222222;")
        layout.addWidget(analysis_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #00D4FF;
                color: #121212;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                
            }
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.resize(600, 400)
        dialog.exec()

    def update_ui(self):
        current_packets = 0
        try:
            with open('packet_data.json', 'r') as f:
                data = json.load(f)
            current_packets = data.get('packet_count', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"packets": []}

        packets = data.get("packets", [])
        if packets:
            # Update table
            self.table.setRowCount(min(10, len(packets)))
            for i, packet in enumerate(packets[-10:]):
                self.table.setItem(i, 0, QTableWidgetItem(packet.get('src_ip', '')))
                self.table.setItem(i, 1, QTableWidgetItem(packet.get('dst_ip', '')))
                proto = packet.get('protocol', 'Other')
                self.table.setItem(i, 2, QTableWidgetItem(proto))
                self.table.setItem(i, 3, QTableWidgetItem(str(packet.get('length', 0))))
                
                # ML predictions for Confidence Score and Action (skip in layout-only)
                if not self.layout_only and self.model and self.extractor:
                    packet_data = {
                        'src_ip': packet.get('src_ip', '192.168.1.1'),
                        'dst_ip': packet.get('dst_ip', '10.0.0.1'),
                        'protocol': 6 if packet.get('protocol', 'TCP').upper() == 'TCP' else 17,
                        'length': packet.get('length', 100),
                        'src_port': packet.get('src_port', 12345),
                        'dst_port': packet.get('dst_port', 80),
                        'flags': packet.get('flags', 'S'),
                        'direction': 'inbound'
                    }
                    features = self.extractor.extract_packet_features(packet_data)
                    selected_features = self.extractor.get_selected_features(features)
                    features_array = np.array(selected_features).reshape(1, -1)
                    prediction = self.model.predict(features_array)[0]
                    probabilities = self.model.predict_proba(features_array)[0]
                    confidence = max(probabilities) * 100
                    action = "NORMAL" if prediction == 0 else "ATTACK"
                    if action == "ATTACK" and confidence > 70:
                        src_ip = packet.get('src_ip', 'unknown')
                        dst_ip = packet.get('dst_ip', 'unknown')
                        
                        # Check if this is a simulated attack
                        is_simulation = packet.get('simulated', False)
                        toast_type = "simulation" if is_simulation else "block"
                        title = "🧪 SIMULATED THREAT" if is_simulation else "🚨 THREAT DETECTED"
                        
                        self.show_toast(
                            title,
                            f"Attack from {src_ip} to {dst_ip}\nConfidence: {confidence:.1f}%",
                            toast_type
                        )
                    self.table.setItem(i, 4, QTableWidgetItem(f"{confidence:.1f}%"))
                    self.table.setItem(i, 5, QTableWidgetItem(action))
                else:
                    self.table.setItem(i, 4, QTableWidgetItem("N/A"))
                    self.table.setItem(i, 5, QTableWidgetItem("UNKNOWN"))

        # Update pps and gauge (skip in layout-only)
        if not self.layout_only:
            pps = max(0, current_packets - self.previous_packets)
            self.previous_packets = current_packets
            risk = min(100, (pps / 50) * 100)  # 50 pps = 100% risk
            if hasattr(self, 'right_gauge') and self.right_gauge:
                self.right_gauge.set_risk(risk)

    def send_message(self, msg):
        """Send message programmatically (used by forensic panel)."""
        if not msg:
            return
        # Add user message and queue AI response
        self.add_chat_message("user", msg)
        QTimer.singleShot(1000, lambda: self.process_response(msg))

    def process_response(self, msg):
        """Process AI response and add to shared conversation."""
        response = self.process_command(msg)
        self.add_chat_message("ai", response)

    def add_chat_message(self, sender, message):
        """Add a message to shared conversation history and sync both chats."""
        # Add to shared history
        self.conversation_history.append((sender, message))
        
        # Update dashboard forensic panel chat (QTextEdit uses HTML)
        if hasattr(self, 'forensic_panel') and self.forensic_panel:
            if sender == "user":
                self.forensic_panel.chat_area.append(f"<b>You:</b> {message}")
            else:  # ai
                self.forensic_panel.chat_area.append(f"<b><span style='color: #2DD4BF'>AI:</span></b> {message}")
        
        # Sync with AI Mentor page if available
        if self.ai_mentor_page:
            self.ai_mentor_page.sync_message(sender, message)

    def process_command(self, msg):
        """Process user commands and return appropriate responses."""
        msg_lower = msg.lower()
        
        # Keyword-based responses (work without AI)
        import re
        greeting_pattern = r'\b(hi|hello|hey|greetings)\b'
        if re.search(greeting_pattern, msg_lower):
            return "Hello! I'm the AI assistant for WATCHDOG. Type 'help' to see what I can do."
        
        elif msg_lower.strip() in ["help", "?", "help me", "commands"] or msg_lower.startswith("help "):
            return """Available Commands (AI-free mode):

Basic:
• hi/hello - Greeting
• help - Show this message
• time - Current time

Security Status:
• threat level - Current risk with live data
• status - Full system health
• dangerous/risk/warning - Quick safety check

Information:
• packets/traffic - Network activity summary
• logs/history - Activity log overview
• monitor - Monitoring capabilities
• firewall - Firewall status
• attack types - Common threats detected

Advice (No AI needed):
• prevent threats - Security best practices
• tips/advice - Security recommendations
• improve security - Quick wins for protection
• secure my network - Actionable steps

Analysis:
• predict: src_ip=X dst_ip=Y protocol=tcp length=100 - ML packet analysis
• what can you do - List capabilities

Enable AI with Ollama on port 11434 for detailed analysis."""
        
        elif "what can you do" in msg_lower or "capabilities" in msg_lower:
            offline_features = [
                "Real-time threat monitoring (Live Sentinel)",
                "ML-based packet analysis",
                "Security best practices and tips",
                "Network traffic insights",
                "System health reports",
                "Attack type explanations"
            ]
            ai_features = "Detailed log analysis and natural language security explanations (with AI enabled)"
            return f"Offline Features (no AI required):\n• " + "\n• ".join(offline_features) + f"\n\n{ai_features}\n\nType 'help' for all available commands."
        
        elif "thank" in msg_lower:
            return "You're welcome! Let me know if you need anything else."
        
        elif "threat" in msg_lower and "level" in msg_lower:
            context = self._get_system_context()
            return f"Current threat level: {context['threat_level']} ({context['risk_score']:.1f}% risk)\n{context['system_health']}\nTotal packets monitored: {context['total_packets']:,}\n{context['recent_alerts']}"
        
        elif "status" in msg_lower:
            context = self._get_system_context()
            return f"System Status: {context['system_health']}\nThreat Level: {context['threat_level']}\nPackets Monitored: {context['total_packets']:,}\nAI Assistant: {'Online (with real-time context)' if self.ai_client else 'Offline'}"
        
        elif "firewall" in msg_lower:
            return "Firewall Status: ACTIVE - Blocking unauthorized connections. Last updated: just now."
        
        elif "packet" in msg_lower or "traffic" in msg_lower:
            return "Recent activity: Monitoring 47 packets/sec. No anomalies detected in current traffic flow."
        
        elif "who are you" in msg_lower or "your name" in msg_lower:
            return "I'm WATCHDOG's AI Security Assistant. I help monitor network traffic, detect threats, and provide forensic analysis."
        
        elif "time" in msg_lower:
            from datetime import datetime
            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Comprehensive security advice responses (work without AI)
        elif "prevent" in msg_lower and any(w in msg_lower for w in ["threat", "attack", "security", "protect"]):
            context = self._get_system_context()
            return f"""Security Best Practices:

Current Status: {context['system_health']}

Prevention Tips:
1. Keep firewall ACTIVE (currently enabled)
2. Monitor unusual traffic patterns ({context['recent_alerts']})
3. Regular security audits ({context['total_packets']:,} packets analyzed)
4. Block suspicious IPs (ML model: {'Active' if self.model else 'Offline'})

Risk Level: {context['threat_level']} ({context['risk_score']:.1f}%)

For detailed analysis, enable AI with Ollama running on port 11434."""
        
        elif any(w in msg_lower for w in ["tip", "advice", "recommend", "improve", "secure"]):
            return """Network Security Recommendations:

Quick Wins:
• Use strong, unique passwords for all network devices
• Enable WPA3 encryption on WiFi
• Disable unused ports and services
• Keep firmware/software updated
• Enable automatic security patches

Monitoring:
• Review firewall logs weekly
• Set up alerts for suspicious traffic
• Check for unauthorized devices
• Audit user access permissions

Currently: ML threat detection {'active' if self.model else 'offline'}, monitoring enabled."""
        
        elif "dangerous" in msg_lower or "risk" in msg_lower or "warning" in msg_lower:
            context = self._get_system_context()
            if context['threat_level'] in ['HIGH', 'ELEVATED']:
                return f"⚠️ ALERT: {context['recent_alerts']}\n\nRisk Score: {context['risk_score']:.1f}%\nStatus: {context['system_health']}\n\nRecommend immediate review of recent traffic. Check Settings > Flagged Incidents for details."
            else:
                return f"✅ System is currently safe. Risk Level: {context['threat_level']} ({context['risk_score']:.1f}%)\n\n{context['system_health']}\n\nContinue monitoring - no immediate threats detected."
        
        elif "attack" in msg_lower and "type" in msg_lower:
            return """Common Attack Types Detected by WATCHDOG:

1. Port Scanning - Systematic scanning of ports for vulnerabilities
2. DDoS - Distributed Denial of Service traffic floods
3. Malware C2 - Command & control communication attempts
4. Brute Force - Repeated login/password attempts
5. Suspicious Payloads - Unusual packet sizes or content
6. IP Spoofing - Fake source addresses

Current Detection: ML model {'active' if self.model else 'offline'}
Check Live Sentinel > Flagged Incidents for detected threats."""
        
        elif "log" in msg_lower or "history" in msg_lower or "record" in msg_lower:
            context = self._get_system_context()
            return f"""Network Activity Log Summary:

• Total Packets Monitored: {context['total_packets']:,}
• Recent Alerts: {context['recent_alerts']}
• Current Threat Level: {context['threat_level']}
• System Status: {context['system_health']}

View detailed logs:
- Live Sentinel page: Real-time packet table
- Forensic Vault: Flagged incidents and analysis
- Settings: Export packet data

For AI-powered log analysis, enable Ollama integration."""
        
        elif "monitor" in msg_lower or "watch" in msg_lower:
            return """WATCHDOG Monitoring Capabilities:

Active Monitoring:
✓ Real-time packet capture and analysis
✓ ML-based threat detection ({'enabled' if self.model else 'disabled'})
✓ Risk score calculation (0-100%)
✓ Automated toast alerts for threats
✓ Network traffic visualization

Dashboard Views:
- Live Sentinel: Current traffic + threat gauge
- Forensic Vault: Historical incidents
- Network Topology: Device monitoring

Auto-refresh: Every 2 seconds"""
        
        elif msg_lower.startswith("predict"):
            if not self.model or not self.extractor:
                return "ML model not available. Please ensure models/random_forest_model.pkl exists. Try 'help' for other commands."
            try:
                params_str = msg.split(":", 1)[1].strip()
                params = {}
                for pair in params_str.split():
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key.strip()] = value.strip()
                packet_data = {
                    'src_ip': params.get('src_ip', '192.168.1.1'),
                    'dst_ip': params.get('dst_ip', '10.0.0.1'),
                    'protocol': 6 if params.get('protocol', 'tcp').lower() == 'tcp' else 17,
                    'length': int(params.get('length', '100')),
                    'src_port': int(params.get('src_port', '12345')),
                    'dst_port': int(params.get('dst_port', '80')),
                    'flags': params.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                label_map = {0: 'NORMAL', 1: 'ATTACK'}
                return f"Prediction: {label_map.get(prediction, 'UNKNOWN')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        # AI-dependent responses (require ai_client)
        if not self.ai_client:
            return f"I'm not connected to the AI backend right now. Try 'help' to see available offline commands, or enable AI with Ollama running on port 11434."
        
        # Check if there's already an AI query running
        if hasattr(self, '_ai_worker') and self._ai_worker and self._ai_worker.isRunning():
            return "⏳ I'm still processing your previous question. Please wait..."
        
        if msg_lower.startswith("explain log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                self._start_ai_query(EXPLANATION_PROMPT.format(log=formatted))
                return "__AI_PROCESSING__"  # Signal that we're handling this async
            except Exception as e:
                return f"Error processing log: {str(e)}"
        
        elif msg_lower.startswith("analyze log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                self._start_ai_query(TECHNICAL_ANALYSIS_PROMPT.format(log=formatted))
                return "__AI_PROCESSING__"
            except Exception as e:
                return f"Error processing log: {str(e)}"
        
        else:
            # Gather real-time system context for AI
            context = self._get_system_context()
            prompt = GENERAL_PROMPT.format(
                query=msg,
                threat_level=context['threat_level'],
                risk_score=context['risk_score'],
                total_packets=context['total_packets'],
                recent_alerts=context['recent_alerts'],
                system_health=context['system_health']
            )
            self._start_ai_query(prompt)
            return "__AI_PROCESSING__"
    
    def _get_system_context(self):
        """Gather current system state for AI context (fast, no ML predictions)."""
        context = {
            'threat_level': 'LOW',
            'risk_score': 0,
            'total_packets': 0,
            'recent_alerts': 'None',
            'system_health': 'Operational'
        }
        
        # Get packet count from file (fast)
        try:
            with open('packet_data.json', 'r') as f:
                data = json.load(f)
            context['total_packets'] = data.get('packet_count', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Count attacks from table widget (fast, already calculated)
        attack_count = 0
        if hasattr(self, 'table'):
            row_count = min(self.table.rowCount(), 20)  # Check last 20 visible rows
            for i in range(row_count):
                action_item = self.table.item(i, 5)  # Action column
                if action_item and action_item.text() == "ATTACK":
                    attack_count += 1
        
        if attack_count > 0:
            context['threat_level'] = 'ELEVATED' if attack_count < 3 else 'HIGH'
            context['recent_alerts'] = f"{attack_count} threats in recent traffic"
        
        # Get risk score from gauge (fast)
        if hasattr(self, 'right_gauge') and hasattr(self.right_gauge, 'current_value'):
            context['risk_score'] = round(self.right_gauge.current_value, 1)
        
        # Determine system health
        if context['risk_score'] > 70:
            context['system_health'] = 'CRITICAL - Immediate attention required'
        elif context['risk_score'] > 40:
            context['system_health'] = 'WARNING - Elevated risk detected'
        elif context['risk_score'] > 0:
            context['system_health'] = 'CAUTION - Minor anomalies'
        else:
            context['system_health'] = 'NOMINAL - All systems operational'
        
        return context

    def _start_ai_query(self, prompt):
        """Start async AI query with streaming."""
        # Initialize streaming state
        self._streaming_buffer = ""
        self._streaming_anchor_pos = None  # Integer position anchor
        
        # Add placeholder message and store position
        if hasattr(self, 'forensic_panel') and self.forensic_panel:
            chat = self.forensic_panel.chat_area
            chat.append("<b><span style='color: #2DD4BF'>AI:</span></b> ")
            # Store the text length as anchor position
            self._streaming_anchor_pos = len(chat.toPlainText())
        
        # Setup timer for batched UI updates (every 150ms)
        self._stream_timer = QTimer(self)
        self._stream_timer.timeout.connect(self._flush_stream_buffer)
        self._stream_timer.start(150)
        
        # Create and start worker thread
        self._ai_worker = AIWorker(self.ai_client, prompt)
        self._ai_worker.chunk.connect(self._on_ai_chunk_buffered)
        self._ai_worker.finished.connect(self._on_ai_finished)
        self._ai_worker.error.connect(self._on_ai_error)
        self._ai_worker.start()
    
    def _on_ai_chunk_buffered(self, chunk, full_response):
        """Buffer chunks - actual UI update happens in timer."""
        self._streaming_buffer = full_response
    
    def _flush_stream_buffer(self):
        """Batch update UI with accumulated chunks."""
        if not self._streaming_buffer or self._streaming_anchor_pos is None:
            return
        
        chat = self.forensic_panel.chat_area
        cursor = chat.textCursor()
        
        # Select from anchor position to end
        cursor.beginEditBlock()
        cursor.setPosition(self._streaming_anchor_pos)
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self._streaming_buffer)
        cursor.endEditBlock()
        
        # Auto-scroll
        scrollbar = chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _on_ai_finished(self, response):
        """Handle AI response when streaming finishes."""
        # Stop the batch timer
        if hasattr(self, '_stream_timer') and self._stream_timer:
            self._stream_timer.stop()
        
        # Final flush to ensure all text is shown
        self._flush_stream_buffer()
        self._streaming_buffer = ""
        self._streaming_anchor_pos = None
        
        # Sync to AI Mentor page
        if self.ai_mentor_page:
            self.ai_mentor_page.sync_message("ai", response)
    
    def _on_ai_error(self, error_msg):
        """Handle AI query error."""
        if hasattr(self, '_stream_timer') and self._stream_timer:
            self._stream_timer.stop()
        self.add_chat_message("ai", f"❌ {error_msg}")

    def update_ai_model(self, model_name):
        """Update the AI model used by OllamaClient."""
        if self.ai_client:
            self.ai_client.model = model_name
            print(f"AI model updated to: {model_name}")
        else:
            print("AI client not initialized - model switch will apply on next AI query")

    def closeEvent(self, event):
        # Stop all timers
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'right_gauge') and hasattr(self.right_gauge, 'smooth_timer'):
            self.right_gauge.smooth_timer.stop()
        if hasattr(self, 'live_traffic') and hasattr(self.live_traffic, 'timer'):
            self.live_traffic.timer.stop()
        if hasattr(self, '_stream_timer') and self._stream_timer:
            self._stream_timer.stop()
        # Stop AI worker if running
        if hasattr(self, '_ai_worker') and self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.terminate()
            self._ai_worker.wait(1000)
        # Quit the application
        QApplication.quit()
        event.accept()

    def create_settings_page(self):
        """Create Settings & Privacy page with toast notification testing"""
        settings_page = QWidget()
        settings_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        main_layout = QVBoxLayout(settings_page)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header
        header = QLabel("SETTINGS & PRIVACY")
        header.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        main_layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Configure Ollama and ensure alignment with NZ Privacy Act 2020 principles")
        subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; margin-bottom: 30px;")
        main_layout.addWidget(subtitle)
        
        # Toast Notification Testing Section
        toast_section = QWidget()
        toast_section.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        toast_layout = QVBoxLayout(toast_section)
        
        toast_title = QLabel("🍞 Toast Notification Testing")
        toast_title.setFont(QFont(THEME['font_mono'].strip("'"), 18))
        toast_title.setStyleSheet(f"color: {THEME['text_primary']}; margin-bottom: 15px;")
        toast_layout.addWidget(toast_title)
        
        toast_desc = QLabel("Test the toast notification system with different message types:")
        toast_desc.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px; margin-bottom: 15px;")
        toast_layout.addWidget(toast_desc)
        
        # Test buttons
        btn_layout = QHBoxLayout()
        
        # Info toast button (Electric Blue)
        info_btn = QPushButton("Test Info Toast")
        info_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['primary']};
                border: 2px solid {THEME['primary']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 180, 216, 0.2);
            }}
        """)
        info_btn.clicked.connect(lambda: self.show_toast("System Update", "Dashboard refreshed successfully", "info"))
        btn_layout.addWidget(info_btn)
        
        # Block toast button (Red)
        block_btn = QPushButton("Test Block Toast")
        block_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['danger']};
                border: 2px solid {THEME['danger']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 107, 107, 0.2);
            }}
        """)
        block_btn.clicked.connect(lambda: self.show_toast("IP Blocked", "192.168.1.100 has been added to block list", "block"))
        btn_layout.addWidget(block_btn)
        
        # Multiple toasts button
        multi_btn = QPushButton("Test Multiple Toasts")
        multi_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['warning']};
                border: 2px solid {THEME['warning']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 159, 67, 0.2);
            }}
        """)
        multi_btn.clicked.connect(self.test_multiple_toasts)
        btn_layout.addWidget(multi_btn)
        
        toast_layout.addLayout(btn_layout)
        main_layout.addWidget(toast_section)
        
        # Add some spacing
        main_layout.addStretch()
        
        self.page_container.addWidget(settings_page)

    def show_toast(self, title, message, type='info'):
        """Show a toast notification"""
        if not self.toast:
            self.toast = ToastNotification(self)
        self.toast.show_message(title, message, type)

    def test_multiple_toasts(self):
        """Test showing multiple toast notifications"""
        self.show_toast("First Notification", "This is the first toast message", "info")
        QTimer.singleShot(500, lambda: self.show_toast("Second Notification", "This is the second toast message", "block"))
        QTimer.singleShot(1000, lambda: self.show_toast("Third Notification", "This is the third toast message", "info"))

    def apply_theme(self):
        """Re-apply current theme to all UI components."""
        from src.ui.theme import THEME
        
        # Update main window background
        self.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Update sidebar header
        if hasattr(self, 'sidebar_header'):
            self.sidebar_header.setStyleSheet(f"""
                background-color: {THEME['bg_header']};
            """)
        
        # Update nav_sidebar
        if hasattr(self, 'nav_sidebar'):
            self.nav_sidebar.setStyleSheet(f"""
                QWidget {{
                    background-color: {THEME['bg_header']};
                }}
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {THEME['text_secondary']};
                    font-family: {THEME['font_mono']};
                    font-size: 12px;
                    padding: 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {THEME['bg_card']};
                    color: {THEME['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: {THEME['primary']};
                    color: {THEME['bg_dark']};
                }}
            """)
        
        # Update sidebar title
        if hasattr(self, 'sidebar_title'):
            self.sidebar_title.setStyleSheet(f"""
                color: {THEME['primary']};
                font-family: '{self.tech_font}', 'Orbitron', 'Rajdhani', 'Courier New', sans-serif;
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
            """)
        
        # Re-create all pages with new theme
        old_index = self.page_container.currentIndex()
        
        # Remove old widgets
        while self.page_container.count() > 0:
            widget = self.page_container.widget(0)
            self.page_container.removeWidget(widget)
            widget.deleteLater()
        
        # Update page container background
        self.page_container.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Re-create pages
        self.create_pages()
        
        # Restore current page
        self.page_container.setCurrentIndex(min(old_index, self.page_container.count() - 1))
        
        # Update status bar if exists
        if hasattr(self, 'status_bar'):
            self.status_bar.setStyleSheet(f"""
                background-color: {THEME['bg_header']};
                border-top: 2px solid {THEME['border']};
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 11px;
                padding: 5px 15px;
            """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatchdogDashboard()
    window.show()
    sys.exit(app.exec())
