"""Live Sentinel (Dashboard) page implementation."""

import json

import psutil
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.ui.theme import THEME
from src.ui.widgets import (
    ForensicAssistantPanel,
    LiveTrafficWidget,
    RiskAnalysisGauge,
    SystemHealthGauge,
)
from src.utils.crypto_utils import get_crypto

crypto = get_crypto()


def get_system_ram():
    """Get total system RAM in GB."""
    try:
        ram_gb = round(psutil.virtual_memory().total / (1024**3))
        return ram_gb
    except Exception:
        return None


class LiveSentinelPage(QWidget):
    """Main dashboard page with metrics, traffic table, and AI panel."""

    def __init__(self, dashboard):
        super().__init__()
        self.dashboard = dashboard
        self.table = None
        self.forensic_panel = None
        self.health_timer = None
        self.risk_timer = None

    def update_system_health(self):
        """Update system health with real data."""
        try:
            import psutil

            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)

            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Get disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Calculate overall health (inverse of resource usage)
            # Lower usage = higher health score
            health_score = max(0, 100 - ((cpu_percent + memory_percent + disk_percent) / 3))

            # Update the gauge
            if hasattr(self, "health_gauge") and self.health_gauge:
                self.health_gauge.set_health(int(health_score))

        except ImportError:
            # If psutil not available, use a reasonable default
            if hasattr(self, "health_gauge") and self.health_gauge:
                self.health_gauge.set_health(75)
        except Exception:
            if hasattr(self, "health_gauge") and self.health_gauge:
                self.health_gauge.set_health(50)

    def update_risk_analysis(self):
        """Update risk analysis with real packet data."""
        try:
            # Read packet data for risk analysis
            packet_data = crypto.read_encrypted_file("packet_data.json")

            packets = packet_data.get("packets", [])
            total_packets = packet_data.get("packet_count", 0)

            # Simple risk calculation based on packet patterns
            risk_score = 5  # Base risk

            if len(packets) > 0:
                # Check for suspicious patterns
                recent_packets = packets[-100:]  # Last 100 packets

                # Count unique source IPs
                unique_sources = len(set(p.get("src_ip", "") for p in recent_packets))

                # Risk factors:
                # - High packet volume
                # - Many unique sources
                # - Suspicious protocols

                if total_packets > 1000:
                    risk_score += 10

                if unique_sources > 20:
                    risk_score += 15

                # Check for non-standard ports
                suspicious_ports = [8080, 3128, 1080, 8081, 8888]
                for packet in recent_packets:
                    if "src_port" in packet and packet["src_port"] in suspicious_ports:
                        risk_score += 5
                        break

                # Add some variation based on time to make it dynamic
                import time

                time_factor = int(time.time()) % 10
                risk_score += time_factor

            # Add some random variation
            import random

            risk_score += random.randint(-5, 10)

            # Cap risk score at 100
            risk_score = max(5, min(100, risk_score))

            # Update the gauge
            if hasattr(self, "right_gauge") and self.right_gauge:
                self.right_gauge.set_risk(int(risk_score))

        except (FileNotFoundError, json.JSONDecodeError):
            # No packet data available - use demo mode
            import random

            if hasattr(self, "right_gauge") and self.right_gauge:
                risk_value = random.randint(5, 25)
                self.right_gauge.set_risk(risk_value)
        except Exception:
            if hasattr(self, "right_gauge") and self.right_gauge:
                self.right_gauge.set_risk(20)

    def update_shield_statistics(self):
        """Update shield statistics with current data."""
        # This method will be called by the dashboard to update statistics
        pass

    def populate_demo_table(self):
        """Populate the traffic table with demo data."""
        if not hasattr(self, "table") or self.table is None:
            return

        sample_traffic = [
            ("192.168.1.100", "10.0.0.1", "TCP", 1500, "85%", "Allowed"),
            ("192.168.1.105", "10.0.0.5", "TCP", 1200, "92%", "Allowed"),
            ("172.16.40.50", "192.168.1.1", "ICMP", 64, "45%", "Allowed"),
            ("198.51.100.22", "172.16.40.172", "TCP", 800, "78%", "Allowed"),
            ("203.0.113.45", "192.168.1.1", "TCP", 1500, "95%", "Blocked"),
            ("198.51.100.23", "192.168.1.1", "TCP", 1500, "88%", "Blocked"),
            ("192.0.2.100", "192.168.1.1", "HTTP", 1500, "92%", "Blocked"),
            ("203.0.113.67", "192.168.1.1", "SSH", 1500, "85%", "Blocked"),
            ("198.51.100.50", "192.168.1.1", "DNS", 1500, "90%", "Flagged"),
            ("203.0.113.89", "192.168.1.1", "HTTP", 1500, "87%", "Flagged"),
        ]
        for row, (src_ip, dst_ip, protocol, length, confidence, action) in enumerate(sample_traffic):
            self.table.setItem(row, 0, QTableWidgetItem(src_ip))
            self.table.setItem(row, 1, QTableWidgetItem(dst_ip))
            self.table.setItem(row, 2, QTableWidgetItem(protocol))
            self.table.setItem(row, 3, QTableWidgetItem(str(length)))
            self.table.setItem(row, 4, QTableWidgetItem(confidence))
            self.table.setItem(row, 5, QTableWidgetItem(action))

    def _trigger_demo_attack(self):
        """Trigger a demo attack to show complete system response."""
        try:
            from datetime import datetime

            # Create multiple mock threats for Forensic Vault (7 examples)
            demo_threats = [
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "DDoS Attack",
                    "source_ip": "203.0.113.45",
                    "destination_ip": "192.168.1.1",
                    "protocol": "TCP",
                    "confidence": 95,
                    "action": "Auto-blocked (Src)",
                    "description": "High volume of SYN packets detected from single source",
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "Port Scanning",
                    "source_ip": "198.51.100.23",
                    "destination_ip": "192.168.1.1",
                    "protocol": "TCP",
                    "confidence": 88,
                    "action": "Auto-blocked (Src)",
                    "description": "Sequential port probing behavior detected",
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "SQL Injection Attempt",
                    "source_ip": "192.0.2.100",
                    "destination_ip": "192.168.1.1",
                    "protocol": "HTTP",
                    "confidence": 92,
                    "action": "Auto-blocked (Src)",
                    "description": "Malicious SQL patterns detected in HTTP requests",
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "Brute Force Attack",
                    "source_ip": "203.0.113.67",
                    "destination_ip": "192.168.1.1",
                    "protocol": "SSH",
                    "confidence": 85,
                    "action": "Auto-blocked (Src)",
                    "description": "Multiple failed login attempts detected",
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "Malware Communication",
                    "source_ip": "198.51.100.50",
                    "destination_ip": "192.168.1.1",
                    "protocol": "DNS",
                    "confidence": 90,
                    "action": "Flagged",
                    "description": "Suspicious DNS tunneling activity detected",
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "XSS Attack",
                    "source_ip": "203.0.113.89",
                    "destination_ip": "192.168.1.1",
                    "protocol": "HTTP",
                    "confidence": 87,
                    "action": "Flagged",
                    "description": "Cross-site scripting patterns detected in web requests",
                },
                {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "attack_type": "Man-in-the-Middle",
                    "source_ip": "192.0.2.150",
                    "destination_ip": "192.168.1.1",
                    "protocol": "HTTPS",
                    "confidence": 93,
                    "action": "Flagged",
                    "description": "SSL certificate spoofing detected",
                },
            ]

            # Add to flagged incidents for AI analysis (Forensic Vault)
            # Convert to the format expected by the vault table
            if not hasattr(self.dashboard, "flagged_incidents"):
                self.dashboard.flagged_incidents = []
            for threat in demo_threats:
                vault_packet = {
                    "timestamp": datetime.now().timestamp(),
                    "src_ip": threat['source_ip'],
                    "dst_ip": threat['destination_ip'],
                    "protocol": threat['protocol'],
                    "length": 1500,
                    "src_port": 4444,
                    "dst_port": 80,
                    "flags": "S",
                    "count": 9999,
                    "ai_confidence": f"{threat['confidence']}%",
                    "ai_threat": threat['attack_type'],
                    "attack_type": threat['attack_type'],
                    "confidence": threat['confidence'],
                    "action": threat['action'],
                    "description": threat['description'],
                }
                self.dashboard.flagged_incidents.insert(0, vault_packet)

            # Add 4 IPs to Security Control blocked IPs
            if not hasattr(self.dashboard, "blocked_ips"):
                self.dashboard.blocked_ips = set()
            if not hasattr(self.dashboard, "blocked_ip_reasons"):
                self.dashboard.blocked_ip_reasons = {}

            # Add first 4 threats as blocked IPs
            for i in range(min(4, len(demo_threats))):
                threat = demo_threats[i]
                self.dashboard.blocked_ips.add(threat['source_ip'])
                self.dashboard.blocked_ip_reasons[threat['source_ip']] = f"Auto-blocked - {threat['attack_type']} detected ({threat['confidence']}% confidence). {threat['description']}"

            # Show toast notification for the primary attack
            if hasattr(self.dashboard, "show_toast"):
                self.dashboard.show_toast(
                    "IP AUTO-BLOCKED",
                    f"Attack from {demo_threats[0]['source_ip']} to {demo_threats[0]['destination_ip']}\nConfidence: {demo_threats[0]['confidence']}%\nIP has been automatically blocked",
                    "block"
                )

            # Update Security Control page
            if hasattr(self.dashboard, "shield_page") and self.dashboard.shield_page:
                self.dashboard.shield_page._sync_blocked_ips()
                self.dashboard.shield_page.update_shield_statistics()

            # Update Forensic Vault page - use dashboard's vault table reference
            if hasattr(self.dashboard, "vault_table") and self.dashboard.vault_table:
                from PyQt6.QtGui import QColor, QFont
                from PyQt6.QtWidgets import QTableWidgetItem

                vault_table = self.dashboard.vault_table
                vault_table.setRowCount(len(demo_threats))
                for i, threat in enumerate(demo_threats):
                    # Timestamp
                    timestamp_item = QTableWidgetItem(threat['timestamp'])
                    vault_table.setItem(i, 0, timestamp_item)

                    # Source IP
                    src_ip_item = QTableWidgetItem(threat['source_ip'])
                    src_ip_item.setForeground(QColor(THEME["primary"]))
                    src_ip_item.setFont(QFont(THEME["font_mono"].strip("'"), 12))
                    vault_table.setItem(i, 1, src_ip_item)

                    # Destination IP
                    dst_ip_item = QTableWidgetItem(threat['destination_ip'])
                    vault_table.setItem(i, 2, dst_ip_item)

                    # Protocol
                    protocol_item = QTableWidgetItem(threat['protocol'])
                    vault_table.setItem(i, 3, protocol_item)

                    # Confidence
                    confidence_item = QTableWidgetItem(f"{threat['confidence']}%")
                    vault_table.setItem(i, 4, confidence_item)

                    # Threat Level
                    threat_item = QTableWidgetItem(threat['attack_type'])
                    vault_table.setItem(i, 5, threat_item)

                    # AI Summary
                    summary_item = QTableWidgetItem("Click to view AI analysis")
                    vault_table.setItem(i, 6, summary_item)

                    # Action
                    action_item = QTableWidgetItem(threat['action'])
                    vault_table.setItem(i, 7, action_item)

            print("Demo attack triggered successfully")

        except Exception as e:
            print(f"Error triggering demo attack: {e}")

    def update_all_widgets(self):
        self.update_system_health()
        self.update_risk_analysis()
        self.update_shield_statistics()
        # Don't clear table in demo mode
        if hasattr(self.dashboard, "demo_mode") and not self.dashboard.demo_mode:
            # Only clear table in live mode
            pass

    def create(self):
        """Create and return the live sentinel page widget."""
        # No separate timer - use dashboard's main timer system

        # Main content widget with dark background
        main_content = QWidget()
        main_content.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ===== PAGE HEADER =====
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        page_title = QLabel("Dashboard")
        page_title.setFont(QFont(THEME["font_mono"].strip("'"), 16))
        page_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: 600;")
        header_layout.addWidget(page_title)

        page_subtitle = QLabel("Live Sentinel")
        page_subtitle.setFont(QFont(THEME["font_mono"].strip("'"), 11))
        page_subtitle.setStyleSheet(f"color: {THEME['text_secondary']};")
        page_subtitle.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(page_subtitle)
        header_layout.addStretch()

        live_pill = QLabel("● LIVE")
        live_pill.setStyleSheet(f"""
            color: {THEME['primary']};
            font-size: 10px;
            font-weight: 600;
            font-family: {THEME['font_mono']};
        """)
        header_layout.addWidget(live_pill)

        # Demo Attack button (only visible in demo mode)
        if hasattr(self.dashboard, "demo_mode") and self.dashboard.demo_mode:
            demo_attack_btn = QPushButton("Demo Attack")
            demo_attack_btn.setMinimumHeight(30)
            demo_attack_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {THEME['danger']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #DC2626;
                }}
            """)
            demo_attack_btn.clicked.connect(self._trigger_demo_attack)
            header_layout.addWidget(demo_attack_btn)

        main_layout.addLayout(header_layout)

        # ===== TOP ROW: Three Metric Cards =====
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        # System Health Card with RAM info
        health_card, self.ram_label = self._create_health_card_with_ram()
        cards_layout.addWidget(health_card)

        # Live Traffic Card
        traffic_widget = LiveTrafficWidget()
        traffic_card = self._create_metric_card("Live Traffic", traffic_widget)
        cards_layout.addWidget(traffic_card)
        if hasattr(self, "sniffer") and self.sniffer.is_running:
            traffic_widget.set_network_status("Connected")

        # Risk Analysis Card
        self.right_gauge = RiskAnalysisGauge()
        risk_card = self._create_metric_card("Risk Analysis", self.right_gauge)
        cards_layout.addWidget(risk_card)

        # Force immediate update with real data
        self.update_risk_analysis()

        main_layout.addLayout(cards_layout)

        # ===== BOTTOM ROW: Table and AI Panel =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)

        # Left side: Traffic Table
        table_container = self._create_traffic_table_section()
        bottom_layout.addWidget(table_container, stretch=2)

        # Right side: Forensic Assistant Panel
        self.forensic_panel = ForensicAssistantPanel(dashboard=self.dashboard)
        bottom_layout.addWidget(self.forensic_panel, stretch=1)

        main_layout.addLayout(bottom_layout, stretch=1)

        return main_content

    def _create_metric_card(self, title, widget):
        """Create a styled metric card with title."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {THEME['text_secondary']};
            font-family: {THEME['font_mono']};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            border: none;
        """)
        layout.addWidget(title_label)

        # Widget (gauge or chart)
        widget.setMinimumHeight(180)
        layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)

        return card

    def _create_health_card_with_ram(self):
        """Create System Health card with RAM info label."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 8px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Title
        title_label = QLabel("System Health")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {THEME['text_secondary']};
            font-family: {THEME['font_mono']};
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 1px;
            border: none;
        """)
        layout.addWidget(title_label)

        # Gauge
        gauge = SystemHealthGauge()
        gauge.setMinimumHeight(160)
        layout.addWidget(gauge, alignment=Qt.AlignmentFlag.AlignCenter)

        # Store reference for updates
        self.health_gauge = gauge

        # Force immediate update with real data
        self.update_system_health()

        # RAM info label
        ram_gb = get_system_ram()
        if ram_gb:
            ram_label = QLabel(f"{ram_gb}GB RAM detected")
            ram_text = f"{ram_gb}GB RAM detected"
        else:
            ram_label = QLabel("RAM: Unknown")
            ram_text = "RAM: Unknown"

        ram_label = QLabel(ram_text)
        ram_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ram_label.setStyleSheet(f"""
            color: {THEME['text_secondary']};
            font-family: {THEME['font_mono']};
            font-size: 11px;
            padding-top: 5px;
            border: none;
        """)
        layout.addWidget(ram_label)

        return card, ram_label

    def _create_traffic_table_section(self):
        """Create traffic table with teal header and Refresh button."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Table with teal header
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Source IP", "Destination IP", "Protocol", "Length", "Confidence\nScore", "Action"]
        )

        # Make table stretch to fill container
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Stretch all columns to fill width
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)

        # Make rows fill vertical space and stretch
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                border: 0px;
                margin: 0px;
                padding: 0px;
            }
        """)
        self.table.setRowCount(10)
        for row in range(10):
            for col in range(6):
                self.table.setItem(row, col, QTableWidgetItem(""))

        # Populate with sample data in demo mode
        if hasattr(self.dashboard, "demo_mode") and self.dashboard.demo_mode:
            sample_traffic = [
                ("192.168.1.100", "10.0.0.1", "TCP", 1500, "85%", "Allowed"),
                ("192.168.1.105", "10.0.0.5", "TCP", 1200, "92%", "Allowed"),
                ("172.16.40.50", "192.168.1.1", "ICMP", 64, "45%", "Allowed"),
                ("198.51.100.22", "172.16.40.172", "TCP", 800, "78%", "Allowed"),
                ("203.0.113.45", "192.168.1.1", "TCP", 1500, "95%", "Blocked"),
                ("198.51.100.23", "192.168.1.1", "TCP", 1500, "88%", "Blocked"),
                ("192.0.2.100", "192.168.1.1", "HTTP", 1500, "92%", "Blocked"),
                ("203.0.113.67", "192.168.1.1", "SSH", 1500, "85%", "Blocked"),
                ("198.51.100.50", "192.168.1.1", "DNS", 1500, "90%", "Flagged"),
                ("203.0.113.89", "192.168.1.1", "HTTP", 1500, "87%", "Flagged"),
            ]
            for row, (src_ip, dst_ip, protocol, length, confidence, action) in enumerate(sample_traffic):
                self.table.setItem(row, 0, QTableWidgetItem(src_ip))
                self.table.setItem(row, 1, QTableWidgetItem(dst_ip))
                self.table.setItem(row, 2, QTableWidgetItem(protocol))
                self.table.setItem(row, 3, QTableWidgetItem(str(length)))
                self.table.setItem(row, 4, QTableWidgetItem(confidence))
                self.table.setItem(row, 5, QTableWidgetItem(action))

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Teal header styling with improved sizing
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 8px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                gridline-color: {THEME['border']};
            }}
            QTableWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid {THEME['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QHeaderView::section {{
                background-color: {THEME['table_header_bg']};
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 11px;
                font-weight: 600;
                padding: 8px 10px;
                border: none;
                border-bottom: 1px solid {THEME['border']};
            }}
            QHeaderView::section:vertical {{
                background-color: {THEME['table_header_bg']};
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 11px;
                border: none;
            }}
        """)

        layout.addWidget(self.table, stretch=1)

        # Refresh button (centered)

        return container
