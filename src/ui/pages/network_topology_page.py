"""Network Topology page implementation."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.theme import THEME
from src.ui.widgets import NetworkTopologyWidget


class NetworkTopologyPage:
    """Network Topology page for visualizing LAN devices."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.topology_widget = None
        
    def create(self):
        """Create and return the network topology page widget."""
        topology_page = QWidget()
        topology_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        main_layout = QVBoxLayout(topology_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header = QLabel("NETWORK TOPOLOGY")
        header.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {THEME['primary']};")
        main_layout.addWidget(header)
        
        # Subtitle
        subtitle = QLabel("Visualizing all hardware on your LAN")
        subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {THEME['text_secondary']};")
        main_layout.addWidget(subtitle)
        
        # Topology visualization widget
        self.topology_widget = NetworkTopologyWidget()
        main_layout.addWidget(self.topology_widget, stretch=1)
        
        # Scan button
        scan_btn = QPushButton("Scan Network")
        scan_btn.setFixedHeight(40)
        scan_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                font-family: {THEME['font_mono']};
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        scan_btn.clicked.connect(self._scan_network)
        main_layout.addWidget(scan_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return topology_page
        
    def _scan_network(self):
        """Simulate network scan and update topology."""
        # Sample devices for demonstration
        sample_devices = [
            {'ip': '192.168.1.1', 'type': 'pc', 'hostname': 'Gateway'},
            {'ip': '192.168.1.100', 'type': 'pc', 'hostname': 'Desktop-PC'},
            {'ip': '192.168.1.101', 'type': 'mobile', 'hostname': 'iPhone'},
            {'ip': '192.168.1.102', 'type': 'iot', 'hostname': 'SmartTV'},
            {'ip': '192.168.1.103', 'type': 'vm', 'hostname': 'Ubuntu-VM'},
        ]
        self.topology_widget.set_devices(sample_devices)
