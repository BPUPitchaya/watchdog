"""Threat Encyclopedia page implementation.

Educational page displaying information about various cyber threats,
attack types, and security concepts in a horizontal scrollable layout with professional styling.
Includes template-based attack simulations.
"""
import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QScrollArea, QFrame, QGraphicsDropShadowEffect, QScroller, QTextEdit
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor

from src.ui.theme import THEME


class SimulationEngine(QObject):
    """Template-based simulation engine for attack demonstrations."""
    
    # Signals to communicate with UI
    packet_injected = pyqtSignal(dict)
    sim_finished = pyqtSignal(str)
    sim_started = pyqtSignal(str, str)
    
    def __init__(self, dashboard, parent=None):
        super().__init__(parent)
        self.dashboard = dashboard
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._inject_step)
        
        # Attack Templates: Defining the "DNA" of each exploit
        self.templates = {
            "Phishing": {
                "desc": "Simulated suspicious email traffic and malicious link requests",
                "packets": [
                    {"src_ip": "192.168.1.100", "dst_ip": "10.0.0.5", "protocol": "TCP", 
                     "port": 25, "size": 2048, "flags": "PA", "threat_type": "PHISHING"},
                ] * 20,
                "interval": 200
            },
            "Malware": {
                "desc": "Simulated file system scanning and suspicious process activity",
                "packets": [
                    {"src_ip": "192.168.1.50", "dst_ip": "185.220.101.42", "protocol": "TCP",
                     "port": 443, "size": 4096, "flags": "PA", "threat_type": "MALWARE_C2"},
                ] * 50,
                "interval": 100
            },
            "DDoS": {
                "desc": "High-volume traffic flood from multiple sources",
                "packets": [
                    {"src_ip": f"10.0.{i//256}.{i%256}", "dst_ip": "192.168.1.1", "protocol": "UDP",
                     "port": 80, "size": 1400, "flags": "", "threat_type": "DDOS"}
                    for i in range(200)
                ],
                "interval": 10
            },
            "Man-in-the-Middle": {
                "desc": "ARP spoofing and traffic interception simulation",
                "packets": [
                    {"src_ip": "192.168.1.1", "dst_ip": "192.168.1.100", "protocol": "ARP",
                     "port": 0, "size": 60, "flags": "", "threat_type": "MITM"},
                ] * 30,
                "interval": 500
            },
            "SQL Injection": {
                "desc": "Malicious SQL queries targeting database ports",
                "packets": [
                    {"src_ip": "10.0.0.15", "dst_ip": "192.168.1.50", "protocol": "TCP",
                     "port": 3306, "size": 512, "flags": "PA", "threat_type": "SQL_INJECTION"},
                ] * 40,
                "interval": 150
            },
            "Cross-Site Scripting": {
                "desc": "Script injection attempts on web services",
                "packets": [
                    {"src_ip": "10.0.0.25", "dst_ip": "192.168.1.80", "protocol": "TCP",
                     "port": 80, "size": 1024, "flags": "PA", "threat_type": "XSS"},
                ] * 35,
                "interval": 180
            },
            "Zero-Day Exploit": {
                "desc": "Unknown vulnerability exploitation patterns",
                "packets": [
                    {"src_ip": "185.220.101.50", "dst_ip": "192.168.1.100", "protocol": "TCP",
                     "port": 445, "size": 2048, "flags": "S", "threat_type": "ZERO_DAY"},
                ] * 25,
                "interval": 300
            },
            "Brute Force": {
                "desc": "Sequential login attempts from single source",
                "packets": [
                    {"src_ip": "185.220.101.60", "dst_ip": "192.168.1.100", "protocol": "TCP",
                     "port": 22, "size": 128, "flags": "S", "threat_type": "BRUTE_FORCE"},
                ] * 100,
                "interval": 50
            },
            "Credential Stuffing": {
                "desc": "Automated login attempts using stolen credentials",
                "packets": [
                    {"src_ip": f"10.{i//100}.{i//10}.{i%10}", "dst_ip": "192.168.1.100", "protocol": "TCP",
                     "port": 443, "size": 256, "flags": "PA", "threat_type": "CREDENTIAL_STUFFING"}
                    for i in range(60)
                ],
                "interval": 120
            }
        }
        
        self.current_template = None
        self.current_packets = []
        self.current_index = 0
        self.active_simulation = None
    
    def start_simulation(self, threat_name):
        """Start a simulation for the given threat."""
        if threat_name in self.templates:
            template = self.templates[threat_name]
            self.current_template = template
            self.current_packets = template["packets"].copy()
            self.current_index = 0
            self.active_simulation = threat_name
            
            # Emit signal to notify UI
            self.sim_started.emit(threat_name, template["desc"])
            
            # Show immediate toast notification
            if self.dashboard and hasattr(self.dashboard, 'show_toast'):
                self.dashboard.show_toast(
                    "🧪 SIMULATION STARTED",
                    f"{threat_name} attack in progress. Click 'Stop' to end.",
                    "simulation"
                )
            
            # Start timer
            self.timer.start(template["interval"])
            return True
        return False
    
    def stop_simulation(self):
        """Stop the current simulation."""
        threat_name = self.active_simulation
        self.timer.stop()
        if threat_name:
            self.sim_finished.emit(threat_name)
            # Show completion toast
            if self.dashboard and hasattr(self.dashboard, 'show_toast'):
                self.dashboard.show_toast(
                    "✅ SIMULATION ENDED",
                    f"{threat_name} attack simulation stopped by user.",
                    "simulation"
                )
            self.active_simulation = None
    
    def is_running(self):
        """Check if a simulation is currently running."""
        return self.timer.isActive()
    
    def _inject_step(self):
        """Inject one packet step into the system."""
        if self.current_index < len(self.current_packets):
            packet = self.current_packets[self.current_index].copy()
            packet["timestamp"] = datetime.now().isoformat()
            packet["simulated"] = True
            
            # Add to dashboard's packet system
            self._inject_to_dashboard(packet)
            
            # Emit signal
            self.packet_injected.emit(packet)
            
            self.current_index += 1
        else:
            # Loop the simulation - continuous until stopped
            self.current_index = 0
    
    def _inject_to_dashboard(self, packet):
        """Inject packet into the dashboard's packet processing system."""
        # Try to access the dashboard's packet data
        if self.dashboard and hasattr(self.dashboard, 'packet_data'):
            # Add to packet list
            if 'packets' not in self.dashboard.packet_data:
                self.dashboard.packet_data['packets'] = []
            
            self.dashboard.packet_data['packets'].append(packet)
            
            # Keep only last 1000 packets
            if len(self.dashboard.packet_data['packets']) > 1000:
                self.dashboard.packet_data['packets'] = self.dashboard.packet_data['packets'][-1000:]
            
            # Update packet count
            self.dashboard.packet_data['packet_count'] = self.dashboard.packet_data.get('packet_count', 0) + 1
            
            # Update threat detection if dashboard has the method
            if hasattr(self.dashboard, '_update_threat_detection'):
                self.dashboard._update_threat_detection(packet)
            
            # Update UI if dashboard has the method
            if hasattr(self.dashboard, 'update_ui'):
                self.dashboard.update_ui()


from src.ui.theme import THEME


class SimulationController(QWidget):
    """Professional Security Sandbox - Split-pane Control Room for attack simulation."""
    
    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.setWindowTitle("Watchdog Security Sandbox")
        self.resize(1200, 1000)
        self.setMinimumSize(900, 600)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        
        # Professional Control Room Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #0F1218;
                color: #E0E0E0;
                font-family: 'Segoe UI';
            }
            QFrame#Sidebar {
                background-color: #1A1E26;
                border-right: 2px solid #343B47;
            }
            QFrame#ContentArea {
                background-color: #0F1218;
            }
            QLabel#SidebarTitle {
                color: #76D7EA;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
            QLabel#RiskLabel {
                font-size: 11px;
                font-weight: bold;
                padding: 2px 5px;
                border-radius: 3px;
            }
            QLabel#LogLabel {
                color: #9B59B6;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#AttackBtn {
                background-color: #2D323E;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
                border: 1px solid #3D4455;
                color: #E0E0E0;
                text-align: left;
            }
            QPushButton#AttackBtn:hover {
                background-color: #3D4455;
                border: 1px solid #76D7EA;
            }
            QPushButton#AttackBtn:pressed {
                background-color: #5BA4B3;
                color: #0F1218;
            }
            QTextEdit#LogDisplay {
                background-color: #05070A;
                border: 1px solid #343B47;
                color: #00FFCC;
                font-family: 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                padding: 10px;
            }
            QPushButton#StopBtn {
                background-color: #AA4444;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton#StopBtn:hover {
                background-color: #FF6B6B;
            }
            QPushButton#StopBtn:disabled {
                background-color: #4A4A4A;
                color: #8A8A8A;
            }
            QPushButton#CloseBtn {
                background-color: #343B47;
                color: #8A94A6;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QPushButton#CloseBtn:hover {
                background-color: #4A5568;
                color: #E0E0E0;
            }
        """)
        
        # Main Split-Pane Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # LEFT SIDEBAR - Attack Scenarios
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(320)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(15, 15, 15, 15)
        side_layout.setSpacing(10)
        
        # Sidebar Title
        title = QLabel("⚔️ ATTACK SCENARIOS")
        title.setObjectName("SidebarTitle")
        side_layout.addWidget(title)
        
        # Status
        self.status_label = QLabel("Status: IDLE")
        self.status_label.setStyleSheet("color: #5BA4B3; font-size: 12px; padding: 5px; background-color: #0F1218; border-radius: 4px;")
        side_layout.addWidget(self.status_label)
        
        side_layout.addSpacing(10)
        
        # Critical Risk Section
        critical_label = QLabel("🔴 CRITICAL RISK")
        critical_label.setObjectName("RiskLabel")
        critical_label.setStyleSheet("color: #FF4C4C; background-color: rgba(255,76,76,0.1);")
        side_layout.addWidget(critical_label)
        
        btn_malware = QPushButton("🦠 Malware Infection\nCommand & Control traffic")
        btn_malware.setObjectName("AttackBtn")
        btn_malware.clicked.connect(lambda: self._start_attack("Malware"))
        side_layout.addWidget(btn_malware)
        
        btn_ddos = QPushButton("🚫 DDoS Attack\nHigh-volume traffic flood")
        btn_ddos.setObjectName("AttackBtn")
        btn_ddos.clicked.connect(lambda: self._start_attack("DDoS"))
        side_layout.addWidget(btn_ddos)
        
        btn_sql = QPushButton("💉 SQL Injection\nMalicious database queries")
        btn_sql.setObjectName("AttackBtn")
        btn_sql.clicked.connect(lambda: self._start_attack("SQL Injection"))
        side_layout.addWidget(btn_sql)
        
        btn_zero = QPushButton("📦 Zero-Day Exploit\nUnknown vulnerability")
        btn_zero.setObjectName("AttackBtn")
        btn_zero.clicked.connect(lambda: self._start_attack("Zero-Day Exploit"))
        side_layout.addWidget(btn_zero)
        
        side_layout.addSpacing(5)
        
        # High Risk Section
        high_label = QLabel("🟠 HIGH RISK")
        high_label.setObjectName("RiskLabel")
        high_label.setStyleSheet("color: #FFA500; background-color: rgba(255,165,0,0.1);")
        side_layout.addWidget(high_label)
        
        btn_phishing = QPushButton("🎣 Phishing Attack\nDeceptive email/links")
        btn_phishing.setObjectName("AttackBtn")
        btn_phishing.clicked.connect(lambda: self._start_attack("Phishing"))
        side_layout.addWidget(btn_phishing)
        
        btn_xss = QPushButton("🌐 XSS Attack\nScript injection")
        btn_xss.setObjectName("AttackBtn")
        btn_xss.clicked.connect(lambda: self._start_attack("Cross-Site Scripting"))
        side_layout.addWidget(btn_xss)
        
        btn_creds = QPushButton("🔓 Credential Stuffing\nStolen credentials")
        btn_creds.setObjectName("AttackBtn")
        btn_creds.clicked.connect(lambda: self._start_attack("Credential Stuffing"))
        side_layout.addWidget(btn_creds)
        
        side_layout.addSpacing(5)
        
        # Medium Risk Section
        medium_label = QLabel("🟡 MEDIUM RISK")
        medium_label.setObjectName("RiskLabel")
        medium_label.setStyleSheet("color: #76D7EA; background-color: rgba(118,215,234,0.1);")
        side_layout.addWidget(medium_label)
        
        btn_mitm = QPushButton("👤 Man-in-the-Middle\nSession hijacking")
        btn_mitm.setObjectName("AttackBtn")
        btn_mitm.clicked.connect(lambda: self._start_attack("Man-in-the-Middle"))
        side_layout.addWidget(btn_mitm)
        
        btn_brute = QPushButton("🔗 Brute Force\nPassword guessing")
        btn_brute.setObjectName("AttackBtn")
        btn_brute.clicked.connect(lambda: self._start_attack("Brute Force"))
        side_layout.addWidget(btn_brute)
        
        side_layout.addStretch()
        
        # Close button in sidebar
        btn_close = QPushButton("✕ Close Sandbox")
        btn_close.setObjectName("CloseBtn")
        btn_close.clicked.connect(self.close)
        side_layout.addWidget(btn_close)
        
        # RIGHT PANEL - Live Injection Feed
        content_area = QFrame()
        content_area.setObjectName("ContentArea")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Log header
        log_header = QLabel("📊 LIVE INJECTION FEED")
        log_header.setObjectName("LogLabel")
        content_layout.addWidget(log_header)
        
        # Log display
        self.packet_log = QTextEdit()
        self.packet_log.setObjectName("LogDisplay")
        self.packet_log.setReadOnly(True)
        self.packet_log.setPlaceholderText("Attack packets will appear here in real-time when simulation starts...")
        content_layout.addWidget(self.packet_log)
        
        # Bottom Control Bar
        control_bar = QHBoxLayout()
        control_bar.addStretch()
        
        self.btn_stop = QPushButton("⏹️ EMERGENCY STOP")
        self.btn_stop.setObjectName("StopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_attack)
        control_bar.addWidget(self.btn_stop)
        
        content_layout.addLayout(control_bar)
        
        # Add panels to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area, 1)
        
        # Connect to engine signals
        if self.engine:
            self.engine.sim_started.connect(self._on_sim_started)
            self.engine.sim_finished.connect(self._on_sim_finished)
            self.engine.packet_injected.connect(self._on_packet_injected)
    
    def _start_attack(self, threat_name):
        """Start an attack simulation."""
        if self.engine and not self.engine.is_running():
            self.engine.start_simulation(threat_name)
    
    def _stop_attack(self):
        """Stop the current simulation."""
        if self.engine:
            self.engine.stop_simulation()
    
    def _on_sim_started(self, threat_name, desc):
        """Handle simulation started."""
        self.status_label.setText(f"Status: RUNNING: {threat_name}")
        self.status_label.setStyleSheet("color: #9B59B6; font-weight: bold; padding: 10px; background-color: #0F1218; border-radius: 5px;")
        self.btn_stop.setEnabled(True)
        self.packet_log.clear()
        self.packet_log.append(f"{'='*50}")
        self.packet_log.append(f"STARTING: {threat_name} Attack Simulation")
        self.packet_log.append(f"Description: {desc}")
        self.packet_log.append(f"{'='*50}\n")
    
    def _on_sim_finished(self, threat_name):
        """Handle simulation finished."""
        self.status_label.setText("Status: IDLE")
        self.status_label.setStyleSheet("color: #5BA4B3; font-weight: bold; padding: 10px; background-color: #0F1218; border-radius: 5px;")
        self.btn_stop.setEnabled(False)
        self.packet_log.append(f"\n{'='*50}")
        self.packet_log.append(f"SIMULATION ENDED: {threat_name}")
        self.packet_log.append(f"{'='*50}\n")
    
    def _on_packet_injected(self, packet):
        """Handle packet injection - display in log."""
        src = packet.get('src_ip', 'unknown')
        dst = packet.get('dst_ip', 'unknown')
        proto = packet.get('protocol', 'UNKNOWN')
        threat = packet.get('threat_type', 'UNKNOWN')
        port = packet.get('port', '-')
        
        log_entry = f"[{threat}] {proto}:{port} | {src} → {dst}"
        self.packet_log.append(log_entry)
        # Auto-scroll to bottom
        scrollbar = self.packet_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def closeEvent(self, event):
        """Ensure simulation stops when window closes."""
        if self.engine and self.engine.is_running():
            self.engine.stop_simulation()
        event.accept()


class SmoothScrollArea(QScrollArea):
    """Custom scroll area with smooth animated scrolling - macOS trackpad compatible."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anim = None
        self._accumulated_delta = 0
        
    def wheelEvent(self, event):
        """Override wheel event for smooth animated scrolling - works with mouse and trackpad."""
        scrollbar = self.horizontalScrollBar()
        
        # Use pixelDelta for trackpad, angleDelta for mouse wheel
        pixel_delta = event.pixelDelta()
        angle_delta = event.angleDelta()
        
        if pixel_delta.x() != 0:
            # Trackpad: smooth continuous scrolling
            # Just scroll directly without animation for trackpad native feel
            scrollbar.setValue(scrollbar.value() - pixel_delta.x())
            event.accept()
            return
        
        # Mouse wheel: use angleDelta
        delta = angle_delta.x() if angle_delta.x() != 0 else angle_delta.y()
        if delta == 0:
            event.ignore()
            return
            
        # Accumulate small deltas and scroll when threshold reached
        self._accumulated_delta += delta
        threshold = 120  # Standard wheel tick
        
        if abs(self._accumulated_delta) >= threshold:
            current = scrollbar.value()
            direction = -1 if self._accumulated_delta > 0 else 1
            target = current + (direction * 350)  # Scroll amount
            
            # Clamp to valid range
            target = max(0, min(target, scrollbar.maximum()))
            
            # Stop any running animation
            if self._anim and self._anim.state() == QPropertyAnimation.State.Running:
                self._anim.stop()
            
            # Create smooth animation
            self._anim = QPropertyAnimation(scrollbar, b"value")
            self._anim.setDuration(250)  # Slightly faster
            self._anim.setStartValue(current)
            self._anim.setEndValue(target)
            self._anim.setEasingCurve(QEasingCurve.Type.OutQuad)
            self._anim.start()
            
            self._accumulated_delta = 0
        
        event.accept()


class ThreatCard(QFrame):
    """Professional threat information card with Watchdog styling."""
    
    # Professional color palette
    BG_DEEP_DARK = "#1A1E26"
    BORDER_RIM = "#343B47"
    CYAN_SIGNATURE = "#76D7EA"
    CYAN_DIMMER = "#5BA4B3"
    TEXT_LIGHT = "#D1D8E0"
    TEXT_MUTED = "#8A94A6"
    BTN_LEARN_BG = "#265C69"
    BTN_SIM_BG = "#343B47"
    
    def __init__(self, title, subtitle, risk, how_it_works, role, page_ref=None, sim_callback=None, parent=None):
        super().__init__(parent)
        self.setFixedWidth(320)
        self.title = title
        self.page_ref = page_ref  # Reference to ThreatEncyclopediaPage
        self.sim_callback = sim_callback
        self.setObjectName("ThreatCard")
        
        # Determine risk color
        risk_color = "#FF4C4C" if "CRITICAL" in risk.upper() else (
            "#FFA500" if "HIGH" in risk.upper() else "#76D7EA"
        )
        
        # Apply Professional Card Styling
        self.setStyleSheet(f"""
            QFrame#ThreatCard {{
                background-color: {self.BG_DEEP_DARK};
                border: 1px solid {self.BORDER_RIM};
                border-radius: 20px;
            }}
            QFrame#ThreatCard:hover {{
                border: 1px solid {self.CYAN_SIGNATURE};
            }}
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 128))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(8)
        
        # Title with Segoe UI font
        self.title_label = QLabel(title)
        title_font = QFont("Segoe UI", 22)
        title_font.setWeight(QFont.Weight.DemiBold)
        self.title_label.setFont(title_font)
        self.title_label.setStyleSheet(f"color: {self.CYAN_SIGNATURE}; letter-spacing: 0.5px;")
        self.title_label.setWordWrap(True)
        
        # Subtitle
        self.sub_label = QLabel(subtitle)
        self.sub_label.setFont(QFont("Segoe UI", 15))
        self.sub_label.setStyleSheet(f"color: {self.TEXT_MUTED}; font-weight: 400;")
        
        # Risk Badge
        self.risk_badge = QLabel(risk)
        self.risk_badge.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.risk_badge.setStyleSheet(f"""
            background-color: {risk_color};
            color: #1A1E26;
            border-radius: 5px;
            padding: 4px 12px;
            font-weight: bold;
        """)
        
        # How it Works section
        how_title = QLabel("How it Works")
        how_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        how_title.setStyleSheet(f"color: {self.CYAN_DIMMER}; text-transform: uppercase; margin-top: 15px;")
        
        how_desc = QLabel(how_it_works)
        how_desc.setFont(QFont("Segoe UI", 13))
        how_desc.setStyleSheet(f"color: {self.TEXT_LIGHT}; line-height: 1.4;")
        how_desc.setWordWrap(True)
        
        # Watchdog's Role section
        role_title = QLabel("Watchdog's Role")
        role_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        role_title.setStyleSheet(f"color: {self.CYAN_DIMMER}; text-transform: uppercase;")
        
        role_desc = QLabel(role)
        role_desc.setFont(QFont("Segoe UI", 13))
        role_desc.setStyleSheet(f"color: {self.TEXT_LIGHT}; line-height: 1.4;")
        role_desc.setWordWrap(True)
        
        # Action Buttons with specific styling
        btn_layout = QHBoxLayout()
        learn_btn = QPushButton("Learn More")
        sim_btn = QPushButton("Simulator")
        
        learn_btn.setObjectName("LearnBtn")
        sim_btn.setObjectName("SimBtn")
        
        learn_btn.setStyleSheet(f"""
            QPushButton#LearnBtn {{
                background-color: {self.BTN_LEARN_BG};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
                border: none;
            }}
            QPushButton#LearnBtn:hover {{
                background-color: {self.CYAN_SIGNATURE};
                color: #1A1E26;
            }}
        """)
        
        sim_btn.setStyleSheet(f"""
            QPushButton#SimBtn {{
                background-color: {self.BTN_SIM_BG};
                color: #FFFFFF;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Segoe UI';
                font-weight: bold;
                font-size: 12px;
                border: none;
            }}
            QPushButton#SimBtn:hover {{
                background-color: {self.CYAN_SIGNATURE};
                color: #1A1E26;
            }}
        """)
        
        # Connect simulator button to open sandbox
        sim_btn.clicked.connect(self._open_sandbox)
        
        btn_layout.addWidget(learn_btn)
        btn_layout.addWidget(sim_btn)
        
        # Add all to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.sub_label)
        layout.addWidget(self.risk_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addSpacing(15)
        layout.addWidget(how_title)
        layout.addWidget(how_desc)
        layout.addWidget(role_title)
        layout.addWidget(role_desc)
        layout.addStretch()
        layout.addLayout(btn_layout)
    
    def _open_sandbox(self):
        """Open the simulation sandbox window."""
        if self.page_ref and hasattr(self.page_ref, 'show_sandbox'):
            self.page_ref.show_sandbox()


class ThreatEncyclopediaPage:
    """Educational page showing cyber threat information with horizontal scroll."""
    
    # Main background color
    MAIN_BG = "#0F1218"
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.search_input = None
        self.cards = []
        self.scroll_content = None
        self.simulation_engine = None
        self.simulation_banner = None
        self.simulation_label = None
        self.simulation_controller = None
        
    def create(self):
        """Create and return the threat encyclopedia page widget."""
        page = QWidget()
        page.setStyleSheet(f"background-color: {self.MAIN_BG};")
        
        # Main layout
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header with title and search
        header_widget = self._create_header()
        main_layout.addWidget(header_widget)
        
        # Simulation status banner (hidden by default)
        self.simulation_banner = self._create_simulation_banner()
        main_layout.addWidget(self.simulation_banner)
        
        # Horizontal scrollable content area with smooth scrolling
        scroll_area = SmoothScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background-color: {self.MAIN_BG};
            }}
            QScrollBar:horizontal {{
                background-color: {self.MAIN_BG};
                height: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: #343B47;
                border-radius: 6px;
                min-width: 30px;
            }}
        """)
        
        # Enable smooth kinetic scrolling (touch-style with momentum)
        QScroller.grabGesture(scroll_area.viewport(), QScroller.ScrollerGestureType.LeftMouseButtonGesture)
        
        # Content container with horizontal layout
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(f"background-color: {self.MAIN_BG};")
        self.cards_layout = QHBoxLayout(self.scroll_content)
        self.cards_layout.setContentsMargins(40, 40, 40, 40)
        self.cards_layout.setSpacing(30)
        
        # Add threat cards
        self._add_threat_cards()
        
        self.cards_layout.addStretch()
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)
        
        return page
    
    def _create_header(self):
        """Create page header with title and search."""
        header = QWidget()
        header.setStyleSheet(f"""
            QWidget {{
                background-color: #1A1E26;
                border-bottom: 1px solid #343B47;
            }}
        """)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Title with Segoe UI
        title = QLabel("Threat Encyclopedia")
        title_font = QFont("Segoe UI", 24)
        title_font.setWeight(QFont.Weight.DemiBold)
        title.setFont(title_font)
        title.setStyleSheet("color: #76D7EA; letter-spacing: 1px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Search container
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search threats...")
        self.search_input.setFixedWidth(250)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1A1E26;
                border: 1px solid #343B47;
                border-radius: 8px;
                padding: 10px 15px;
                color: #D1D8E0;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #76D7EA;
            }
        """)
        self.search_input.textChanged.connect(self._filter_threats)
        self.search_input.returnPressed.connect(lambda: self._filter_threats(self.search_input.text()))
        search_layout.addWidget(self.search_input)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setFixedSize(80, 38)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #265C69;
                border: none;
                border-radius: 8px;
                color: #FFFFFF;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #76D7EA;
                color: #1A1E26;
            }
        """)
        search_btn.clicked.connect(lambda: self._filter_threats(self.search_input.text()))
        search_layout.addWidget(search_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setFixedSize(60, 38)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #343B47;
                border: none;
                border-radius: 8px;
                color: #D1D8E0;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #FF4C4C;
                color: white;
            }
        """)
        clear_btn.clicked.connect(self._clear_search)
        search_layout.addWidget(clear_btn)
        
        layout.addWidget(search_container)
        
        return header
    
    def _clear_search(self):
        """Clear search input and show all cards."""
        self.search_input.clear()
        for card in self.cards:
            card.setVisible(True)
    
    def _add_threat_cards(self):
        """Add all threat information cards in a horizontal layout."""
        threats = [
            {
                "title": "🎣 Phishing",
                "subtitle": "The Impersonator",
                "risk": "HIGH RISK",
                "how_it_works": "Fake emails or websites that trick users into revealing passwords, credit cards, or personal information by pretending to be legitimate companies.",
                "role": "Detects suspicious email patterns, domain spoofing, and malicious links before they reach your inbox."
            },
            {
                "title": "🦠 Malware",
                "subtitle": "The Infector",
                "risk": "CRITICAL",
                "how_it_works": "Viruses, trojans, ransomware, and spyware that infect your device to steal data, encrypt files for ransom, or spy on activities.",
                "role": "Monitors file system changes, network connections, and process behaviors to detect and quarantine malicious software."
            },
            {
                "title": "🚫 DDoS Attack",
                "subtitle": "The Overwhelmer",
                "risk": "HIGH RISK",
                "how_it_works": "Distributed Denial of Service floods servers with massive amounts of fake traffic, causing websites and services to crash.",
                "role": "Identifies unusual traffic patterns, rate limits suspicious connections, and blocks attacking IP addresses."
            },
            {
                "title": "👤 Man-in-the-Middle",
                "subtitle": "The Eavesdropper",
                "risk": "MEDIUM RISK",
                "how_it_works": "Attackers secretly intercept and potentially alter communications between two parties without their knowledge.",
                "role": "Validates SSL/TLS certificates, detects ARP spoofing, and alerts on suspicious network routing changes."
            },
            {
                "title": "💉 SQL Injection",
                "subtitle": "The Database Hacker",
                "risk": "CRITICAL",
                "how_it_works": "Hackers insert malicious SQL code into input fields to manipulate databases, steal data, or gain unauthorized access.",
                "role": "Monitors database queries for suspicious patterns and detects abnormal data access attempts."
            },
            {
                "title": "🌐 Cross-Site Scripting",
                "subtitle": "The Script Injector",
                "risk": "HIGH RISK",
                "how_it_works": "Malicious scripts are injected into trusted websites, stealing cookies, session tokens, or redirecting users to phishing sites.",
                "role": "Scans web traffic for script injection patterns and sanitizes suspicious input data."
            },
            {
                "title": "📦 Zero-Day Exploit",
                "subtitle": "The Unknown Threat",
                "risk": "CRITICAL",
                "how_it_works": "Attacks exploiting software vulnerabilities that are unknown to vendors and have no patches available yet.",
                "role": "Uses behavioral analysis to detect unusual system activity even when the specific vulnerability is unknown."
            },
            {
                "title": "🔗 Brute Force",
                "subtitle": "The Password Cracker",
                "risk": "MEDIUM RISK",
                "how_it_works": "Automated tools try thousands of username and password combinations to gain unauthorized access to accounts.",
                "role": "Detects multiple failed login attempts, implements account lockouts, and blocks suspicious IP addresses."
            },
            {
                "title": "🔓 Credential Stuffing",
                "subtitle": "The Reuser",
                "risk": "HIGH RISK",
                "how_it_works": "Using username/password pairs stolen from previous data breaches to try accessing other accounts.",
                "role": "Monitors for login attempts from compromised credentials and alerts on suspicious account access patterns."
            },
        ]
        
        # Initialize simulation engine
        self.simulation_engine = SimulationEngine(self.dashboard)
        self.simulation_engine.sim_started.connect(self._on_simulation_started)
        self.simulation_engine.sim_finished.connect(self._on_simulation_finished)
        
        # Create simulation controller window (hidden initially)
        self.simulation_controller = SimulationController(self.simulation_engine)
        self.simulation_controller.hide()
        
        # Add cards to horizontal layout
        for threat in threats:
            card = ThreatCard(
                threat["title"],
                threat["subtitle"],
                threat["risk"],
                threat["how_it_works"],
                threat["role"],
                page_ref=self  # Pass reference to ThreatEncyclopediaPage
            )
            card.setObjectName(threat["title"].lower().split()[1])
            self.cards.append(card)
            self.cards_layout.addWidget(card)
    
    def _start_simulation(self, threat_name):
        """Start a simulation for the given threat."""
        if self.simulation_engine and not self.simulation_engine.is_running():
            # Extract threat name from title (remove emoji)
            clean_name = threat_name.split()[1] if len(threat_name.split()) > 1 else threat_name
            self.simulation_engine.start_simulation(clean_name)
    
    def _on_simulation_started(self, threat_name, description):
        """Handle simulation start - show banner."""
        if self.simulation_label:
            self.simulation_label.setText(f"🧪 SIMULATION: {threat_name} - {description}")
            self.simulation_banner.setVisible(True)
    
    def _on_simulation_finished(self, threat_name):
        """Handle simulation finish - hide banner."""
        if self.simulation_label:
            self.simulation_label.setText(f"✅ Simulation Complete: {threat_name}")
            # Hide banner after 3 seconds
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.simulation_banner.setVisible(False))
    
    def _create_simulation_banner(self):
        """Create the simulation status banner."""
        banner = QWidget()
        banner.setVisible(False)
        banner.setStyleSheet("""
            background-color: #265C69;
            border-bottom: 2px solid #76D7EA;
        """)
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(40, 10, 40, 10)
        
        self.simulation_label = QLabel("")
        self.simulation_label.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.simulation_label.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(self.simulation_label)
        
        # Stop button
        stop_btn = QPushButton("Stop Simulation")
        stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF4C4C;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-family: 'Segoe UI';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF6B6B;
            }
        """)
        stop_btn.clicked.connect(self._stop_simulation)
        layout.addWidget(stop_btn)
        
        return banner
    
    def _stop_simulation(self):
        """Stop the current simulation."""
        if self.simulation_engine:
            self.simulation_engine.stop_simulation()
    
    def show_sandbox(self):
        """Show the simulation sandbox window."""
        if not self.simulation_controller:
            self.simulation_controller = SimulationController(self.simulation_engine)
        
        # Center window on screen
        screen = self.dashboard.screen() if hasattr(self.dashboard, 'screen') else None
        if screen:
            screen_geo = screen.geometry()
            window_geo = self.simulation_controller.geometry()
            x = (screen_geo.width() - window_geo.width()) // 2
            y = (screen_geo.height() - window_geo.height()) // 2
            self.simulation_controller.move(x, y)
        
        self.simulation_controller.show()
        self.simulation_controller.raise_()
        self.simulation_controller.activateWindow()
    
    def _filter_threats(self, search_text):
        """Filter threat cards based on search text."""
        if not search_text:
            # Show all cards if search is empty
            for card in self.cards:
                card.setVisible(True)
            return
            
        search_lower = search_text.lower()
        
        for card in self.cards:
            # Check if card title or content contains search text
            found = False
            for child in card.findChildren(QLabel):
                if search_lower in child.text().lower():
                    found = True
                    break
            card.setVisible(found)
