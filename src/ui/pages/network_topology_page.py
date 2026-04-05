"""Network Topology page implementation."""
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QListWidget, QListWidgetItem, QTextEdit, 
    QSplitter, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from src.ui.theme import THEME
from src.ui.widgets import NetworkTopologyWidget


class NetworkTopologyPage:
    """Network Topology page for visualizing LAN devices with full device scanning."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.topology_widget = None
        self.device_list = None
        self.device_details = None
        self.scan_btn = None
        self.scan_status = None
        self.network_range_input = None
        self.total_devices_label = None
        self.pc_count_label = None
        self.iot_count_label = None
        self.unknown_count_label = None
        self.discovered_devices = {}
        
    def create(self):
        """Create and return the full network topology page widget."""
        topology_page = QWidget()
        topology_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        topology_layout = QVBoxLayout(topology_page)
        topology_layout.setContentsMargins(20, 20, 20, 20)
        topology_layout.setSpacing(20)
        
        # Header Section
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(10)
        
        topology_title = QLabel("NETWORK TOPOLOGY DISCOVERY")
        topology_title.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        topology_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topology_title.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 10px;")
        header_layout.addWidget(topology_title)
        
        topology_subtitle = QLabel("Scan your LAN to discover all connected devices and identify potential shadow IT")
        topology_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        topology_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topology_subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; margin-bottom: 20px;")
        header_layout.addWidget(topology_subtitle)
        
        # Scan Controls
        scan_controls = QHBoxLayout()
        scan_controls.setSpacing(15)
        
        self.scan_btn = QPushButton("🔍 SCAN NETWORK")
        self.scan_btn.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        self.scan_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scan_btn.setEnabled(True)
        self.scan_btn.setToolTip("Click to scan network for devices")
        self.scan_btn.setStyleSheet(f"""
            QPushButton {{
                background: {THEME['primary']};
                border: 2px solid {THEME['primary']};
                border-radius: 10px;
                color: {THEME['bg_dark']};
                padding: 15px 30px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {THEME['secondary']};
                border: 2px solid {THEME['secondary']};
            }}
            QPushButton:pressed {{
                background: #00A0B0;
                border: 2px solid #00A0B0;
            }}
            QPushButton:disabled {{
                background: #666666;
                border: 2px solid #666666;
                color: #999999;
            }}
        """)
        self.scan_btn.clicked.connect(self.scan_network_devices)
        scan_controls.addWidget(self.scan_btn)
        
        # Network Range Input
        range_layout = QHBoxLayout()
        range_label = QLabel("Network Range:")
        range_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']}; font-size: 12px;")
        self.network_range_input = QLineEdit("172.16.40.0/24")
        self.network_range_input.setStyleSheet(f"""
            QLineEdit {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
                min-width: 150px;
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
            }}
        """)
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.network_range_input)
        range_layout.addStretch()
        scan_controls.addLayout(range_layout)
        
        # Status Label
        self.scan_status = QLabel("Ready to scan")
        self.scan_status.setStyleSheet(f"color: {THEME['success']}; font-family: {THEME['font_mono']}; font-size: 12px;")
        scan_controls.addWidget(self.scan_status)
        
        scan_controls.addStretch()
        header_layout.addLayout(scan_controls)
        
        # Stats Bar
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"""
            QWidget {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(40)
        
        self.total_devices_label = QLabel("Total Devices: 0")
        self.total_devices_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']}; font-size: 14px; ")
        stats_layout.addWidget(self.total_devices_label)
        
        self.pc_count_label = QLabel("💻 PCs: 0")
        self.pc_count_label.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 14px;")
        stats_layout.addWidget(self.pc_count_label)
        
        self.iot_count_label = QLabel("📱 Mobile/IoT: 0")
        self.iot_count_label.setStyleSheet(f"color: {THEME['warning']}; font-family: {THEME['font_mono']}; font-size: 14px;")
        stats_layout.addWidget(self.iot_count_label)
        
        self.unknown_count_label = QLabel("❓ Unknown: 0")
        self.unknown_count_label.setStyleSheet(f"color: {THEME['danger']}; font-family: {THEME['font_mono']}; font-size: 14px;")
        stats_layout.addWidget(self.unknown_count_label)
        
        stats_layout.addStretch()
        header_layout.addWidget(stats_widget)
        
        topology_layout.addWidget(header_widget)
        
        # Main Content Area - Split View
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Device List
        device_list_widget = QWidget()
        device_list_layout = QVBoxLayout(device_list_widget)
        device_list_layout.setContentsMargins(0, 0, 0, 0)
        
        device_list_header = QLabel("DISCOVERED DEVICES")
        device_list_header.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 16px;  margin-bottom: 10px;")
        device_list_layout.addWidget(device_list_header)
        
        self.device_list = QListWidget()
        self.device_list.setStyleSheet(f"""
            QListWidget {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 10px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {THEME['border']};
                border-radius: 5px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QListWidget::item:hover {{
                background: rgba(0, 180, 216, 0.2);
            }}
        """)
        self.device_list.itemClicked.connect(self.show_device_details)
        device_list_layout.addWidget(self.device_list)
        
        content_splitter.addWidget(device_list_widget)
        
        # Right: Device Details & Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Network Visualization (Cisco-style radial topology)
        viz_header = QLabel("NETWORK VISUALIZATION")
        viz_header.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 16px;  margin-bottom: 10px;")
        right_layout.addWidget(viz_header)
        
        self.topology_widget = NetworkTopologyWidget()
        self.topology_widget.device_clicked.connect(self._on_topology_device_clicked)
        right_layout.addWidget(self.topology_widget)
        
        # Device Details Panel
        details_header = QLabel("DEVICE DETAILS")
        details_header.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 16px;  margin-top: 20px; margin-bottom: 10px;")
        right_layout.addWidget(details_header)
        
        self.device_details = QTextEdit()
        self.device_details.setReadOnly(True)
        self.device_details.setStyleSheet(f"""
            QTextEdit {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                line-height: 1.6;
            }}
        """)
        self.device_details.setPlaceholderText("Select a device from the list to view detailed information...")
        self.device_details.setMaximumHeight(200)
        right_layout.addWidget(self.device_details)
        
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([400, 600])
        
        topology_layout.addWidget(content_splitter, stretch=1)
        
        return topology_page
    
    def scan_network_devices(self):
        """Scan network for connected devices using ARP requests"""
        print("[DEBUG] scan_network_devices called!")
        import os
        is_windows = os.name == 'nt'
        is_root = hasattr(os, 'geteuid') and os.geteuid() == 0
        layout_only = getattr(self.dashboard, 'layout_only', False)
        
        print(f"[DEBUG] is_windows={is_windows}, is_root={is_root}, layout_only={layout_only}")
        
        # For demo mode (Windows, non-root, or layout-only), run directly on main thread
        if (is_windows or not is_root) or layout_only:
            print("[DEBUG] Demo mode - running scan directly on main thread")
            self._perform_demo_scan()
            return
        
        # For real scan, run in background thread
        print("[DEBUG] Real scan - starting background thread...")
        self.scan_btn.setEnabled(False)
        self.scan_status.setText("🔍 Scanning network...")
        self.scan_status.setStyleSheet("color: #FFD93D; font-family: 'Courier New', monospace; font-size: 12px;")
        self.device_list.clear()
        self.topology_widget.set_devices([])
        threading.Thread(target=self._perform_network_scan, daemon=True).start()
    
    def _perform_demo_scan(self):
        """Perform demo scan directly on main thread"""
        print("[DEBUG] _perform_demo_scan started")
        self.scan_btn.setEnabled(False)
        self.scan_status.setText("🔍 Scanning network...")
        self.scan_status.setStyleSheet("color: #FFD93D; font-family: 'Courier New', monospace; font-size: 12px;")
        self.device_list.clear()
        self.topology_widget.set_devices([])
        
        demo_devices = [
            {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'hostname': 'Router-Gateway', 'vendor': 'Netgear', 'type': 'pc'},
            {'ip': '192.168.1.5', 'mac': 'A4:B1:C1:22:33:44', 'hostname': 'iPhone-BPU', 'vendor': 'Apple', 'type': 'mobile'},
            {'ip': '192.168.1.10', 'mac': '64:16:66:77:88:99', 'hostname': 'Alexa-Echo', 'vendor': 'Amazon', 'type': 'iot'},
            {'ip': '192.168.1.15', 'mac': '08:00:27:AB:CD:EF', 'hostname': 'Ubuntu-VM', 'vendor': 'VirtualBox', 'type': 'vm'},
            {'ip': '192.168.1.20', 'mac': 'B8:27:EB:12:34:56', 'hostname': 'Raspberry-Pi', 'vendor': 'Raspberry Pi', 'type': 'pi'},
            {'ip': '192.168.1.100', 'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'Unknown-Device', 'vendor': 'Unknown Vendor', 'type': 'unknown'},
        ]
        
        print(f"[DEBUG] About to update device list with {len(demo_devices)} devices")
        self._update_device_list(demo_devices)
        print("[DEBUG] _update_device_list completed")
        self.scan_status.setText("⚠️ Demo mode (run with sudo for real scan)")
        self.scan_status.setStyleSheet("color: #FFD93D; font-family: 'Courier New', monospace; font-size: 12px;")
        self.scan_btn.setEnabled(True)
        print("[DEBUG] _perform_demo_scan completed")

    def _perform_network_scan(self):
        """Perform actual network scanning"""
        try:
            import scapy.all as scapy
            from scapy.layers.l2 import ARP, Ether
            
            network_range = self.network_range_input.text().strip()
            print(f"[DEBUG] Starting scan of {network_range}")
            
            # Create ARP request packet
            print(f"[DEBUG] Creating ARP packet for {network_range}")
            arp = ARP(pdst=network_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            print(f"[DEBUG] Packet created: {packet.summary()}")
            
            print(f"[DEBUG] Sending ARP requests...")
            # Send packet and capture responses
            try:
                result = scapy.srp(packet, timeout=3, verbose=0)[0]
                print(f"[DEBUG] Received {len(result)} responses")
            except Exception as scan_err:
                print(f"[DEBUG] Scapy srp error: {scan_err}")
                result = []
            
            if len(result) == 0:
                print("[DEBUG] No devices found - network may be empty or firewall blocking ARP")
            
            devices = []
            for sent, received in result:
                print(f"[DEBUG] Found device: {received.psrc} - {received.hwsrc}")
                device_info = {
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'hostname': self._get_hostname(received.psrc),
                    'vendor': self._get_vendor(received.hwsrc),
                    'type': self._categorize_device(received.hwsrc, received.psrc)
                }
                devices.append(device_info)
            
            print(f"[DEBUG] Total devices found: {len(devices)}")
            # Update UI from main thread
            self._pending_devices = devices
            QTimer.singleShot(0, self._apply_real_devices)
            
        except Exception as e:
            import traceback
            print(f"[DEBUG] Scan error: {str(e)}")
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            QTimer.singleShot(0, lambda: self._scan_error(str(e)))
    
    def _get_hostname(self, ip):
        """Try to get hostname from IP"""
        try:
            import socket
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return "Unknown"
    
    def _get_vendor(self, mac):
        """Get vendor from MAC address (simplified)"""
        mac_prefix = mac[:8].upper()
        vendors = {
            "00:50:56": "VMware",
            "08:00:27": "VirtualBox",
            "B8:27:EB": "Raspberry Pi",
            "DC:A6:32": "Raspberry Pi",
            "00:17:88": "Philips Hue",
            "18:B4:30": "Nest Labs",
            "64:16:66": "Amazon",
            "A4:77:33": "Amazon",
            "AC:63:BE": "Amazon",
            "00:04:20": "Google",
            "60:03:08": "Google",
            "D4:F5:47": "Google",
            "00:26:BB": "Apple",
            "60:33:4B": "Apple",
            "AC:DE:48": "Apple",
            "D0:23:DB": "Apple",
            "A4:B1:C1": "Apple",
            "AC:BC:32": "Apple",
            "68:D7:9A": "Samsung",
            "24:4B:03": "Samsung",
            "C0:97:27": "Samsung",
        }
        return vendors.get(mac_prefix, "Unknown Vendor")
    
    def _categorize_device(self, mac, ip):
        """Categorize device type based on MAC and hostname"""
        mac_upper = mac.upper()
        hostname_upper = self._get_hostname(ip).upper()
        
        # Mobile devices
        mobile_keywords = ["PHONE", "MOBILE", "IPHONE", "ANDROID", "IPAD", "TABLET"]
        if any(kw in hostname_upper for kw in mobile_keywords):
            return "mobile"
        
        # Check MAC prefixes for common mobile vendors
        mobile_prefixes = ["00:26:BB", "60:33:4B", "AC:DE:48", "D0:23:DB", "A4:B1:C1", "AC:BC:32", "68:D7:9A", "24:4B:03", "C0:97:27"]
        if any(mac_upper.startswith(prefix) for prefix in mobile_prefixes):
            return "mobile"
        
        # IoT devices
        iot_keywords = ["SMART", "HUE", "NEST", "RING", "ALEXA", "ECHO", "CAMERA", "IOT"]
        if any(kw in hostname_upper for kw in iot_keywords):
            return "iot"
        
        # Check MAC prefixes for common IoT vendors
        iot_prefixes = ["00:17:88", "18:B4:30", "64:16:66", "A4:77:33", "AC:63:BE"]
        if any(mac_upper.startswith(prefix) for prefix in iot_prefixes):
            return "iot"
        
        # VMs
        vm_prefixes = ["00:50:56", "08:00:27"]
        if any(mac_upper.startswith(prefix) for prefix in vm_prefixes):
            return "vm"
        
        # Raspberry Pi
        pi_prefixes = ["B8:27:EB", "DC:A6:32"]
        if any(mac_upper.startswith(prefix) for prefix in pi_prefixes):
            return "pi"
        
        return "unknown"
    
    def _apply_demo_devices(self):
        """Apply demo devices to UI from main thread"""
        print("[DEBUG] _apply_demo_devices called")
        if hasattr(self, '_pending_devices'):
            self._update_device_list(self._pending_devices)
            self.scan_status.setText("⚠️ Demo mode (run with sudo for real scan)")
            self.scan_status.setStyleSheet("color: #FFD93D; font-family: 'Courier New', monospace; font-size: 12px;")
            self.scan_btn.setEnabled(True)
            print("[DEBUG] Demo devices applied to UI")
    
    def _apply_real_devices(self):
        """Apply real scan devices to UI from main thread"""
        print("[DEBUG] _apply_real_devices called")
        if hasattr(self, '_pending_devices'):
            self._update_device_list(self._pending_devices)
            print("[DEBUG] Real devices applied to UI")
    
    def _update_device_list(self, devices):
        """Update the device list UI"""
        print(f"[DEBUG] _update_device_list called with {len(devices)} devices")
        self.discovered_devices = {}
        
        # Count devices by type
        counts = {'total': 0, 'pc': 0, 'mobile': 0, 'iot': 0, 'vm': 0, 'pi': 0, 'unknown': 0}
        
        for device in devices:
            counts['total'] += 1
            device_type = device['type']
            counts[device_type] = counts.get(device_type, 0) + 1
            
            # Create list item
            icon = self._get_device_icon(device_type)
            item_text = f"{icon} {device['ip']} - {device['hostname']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)
            self.discovered_devices[device['ip']] = device
        
        # Update stats
        self.total_devices_label.setText(f"Total Devices: {counts['total']}")
        self.pc_count_label.setText(f"💻 PCs/Servers: {counts.get('vm', 0) + counts.get('pi', 0)}")
        self.iot_count_label.setText(f"📱 Mobile/IoT: {counts.get('mobile', 0) + counts.get('iot', 0)}")
        self.unknown_count_label.setText(f"❓ Unknown: {counts['unknown']}")
        
        # Update visualization
        self.topology_widget.set_devices(devices)
        
        self.scan_btn.setEnabled(True)
        self.scan_status.setText(f"✅ Scan complete - {counts['total']} devices found")
        self.scan_status.setStyleSheet("color: #6BCF7F; font-family: 'Courier New', monospace; font-size: 12px;")
    
    def _get_device_icon(self, device_type):
        """Get icon for device type"""
        icons = {
            'pc': '💻',
            'mobile': '📱',
            'iot': '📡',
            'vm': '🖥️',
            'pi': '🥧',
            'unknown': '❓'
        }
        return icons.get(device_type, '❓')
    
    def _on_topology_device_clicked(self, device):
        """Handle device click from topology visualization"""
        # Update device details panel with selected device
        self.device_details.setHtml(self._format_device_details(device))
    
    def show_device_details(self, item):
        """Show detailed information for selected device"""
        device = item.data(Qt.ItemDataRole.UserRole)
        if not device:
            return
        
        self.device_details.setHtml(self._format_device_details(device))
    
    def _get_device_risk_assessment(self, device):
        """Get security risk assessment for device"""
        if device['vendor'] == "Unknown Vendor":
            return "⚠️ MEDIUM RISK - Unknown device vendor"
        if device['type'] == 'iot':
            return "⚠️ LOW-MEDIUM RISK - IoT device, ensure firmware is updated"
        if device['type'] == 'mobile':
            return "✅ LOW RISK - Personal mobile device"
        return "✅ LOW RISK - Known device type"
    
    def _get_device_recommendations(self, device):
        """Get security recommendations for device"""
        if device['vendor'] == "Unknown Vendor":
            return "• Investigate this device - unknown vendor could indicate rogue device\n• Consider blocking MAC if not authorized\n• Check network access logs for this IP"
        if device['type'] == 'iot':
            return "• Verify IoT device is on isolated network segment\n• Check for latest security updates\n• Review device permissions and network access"
        if device['type'] == 'mobile':
            return "• Ensure device is using WPA3 WiFi\n• Verify mobile device management (MDM) policies\n• Check for unauthorized network access"
        return "• Verify device is authorized on network\n• Ensure proper network segmentation\n• Monitor traffic patterns from this device"
    
    def _format_device_details(self, device):
        """Format device details as HTML"""
        return f"""
<b>Device Information</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>IP Address:</b>     {device['ip']}
<b>MAC Address:</b>   {device.get('mac', 'N/A')}
<b>Hostname:</b>      {device.get('hostname', 'Unknown')}
<b>Vendor:</b>         {device.get('vendor', 'Unknown')}
<b>Device Type:</b>    {device['type'].upper()}

<b>Security Analysis</b>
━━━━━━━━━━━━━━━━━━━━━━━

• Device is actively responding to ARP requests
• MAC address is {'well-known' if device.get('vendor') != 'Unknown Vendor' else 'unknown - potential shadow IT'}
• Classification: {self._get_device_risk_assessment(device)}

<b>Recommendations</b>
━━━━━━━━━━━━━━━━━━━━━━━

{self._get_device_recommendations(device)}
        """
    
    def _scan_error(self, error_msg):
        """Handle scan errors"""
        self.scan_btn.setEnabled(True)
        self.scan_status.setText(f"❌ Scan failed: {error_msg}")
        self.scan_status.setStyleSheet("color: #FF6B6B; font-family: 'Courier New', monospace; font-size: 12px;")
        
        # Show error in device list
        error_item = QListWidgetItem(f"⚠️ Error: {error_msg}")
        error_item.setForeground(QColor("red"))
        self.device_list.addItem(error_item)
