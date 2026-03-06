
# Modern Dashboard for WATCHDOG AI
# High-fidelity UI with dark mode, glassmorphism, and cybersecurity components.

import flet as ft
import json
import joblib
import numpy as np
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ml.feature_extractor import FeatureExtractor

from src.ai.ollama_client import OllamaClient
from src.ai.prompts import GENERAL_PROMPT, EXPLANATION_PROMPT, TECHNICAL_ANALYSIS_PROMPT
from src.ai.utils import format_packet_log

class ModernDashboard:
    "Modern dashboard with dark theme and advanced UI components."
    
    def __init__(self):
        self.data_file = "packet_data.json"
        
        # Load ML model and feature extractor
        try:
            self.model = joblib.load('models/random_forest_model.pkl')
            self.extractor = FeatureExtractor()
            print("ML model loaded successfully")
        except Exception as e:
            print(f"Failed to load ML model: {e}")
            self.model = None
            self.extractor = None
        
        self.ai_client = OllamaClient()
        
        # Initialize components
        self.sidebar = self.create_sidebar()
        self.header = self.create_header()
        self.status_gauge = self.create_status_gauge()
        
        # Initialize traffic display (text since LineChart not available)
        self.last_packet_count = 0
        self.current_packets = ft.Text("Packets: 0", color="#B0B0B0", size=12)
        self.monitoring_status = ft.Text("Status: Waiting for data", color="#B0B0B0", size=10)
        
        self.traffic_graph = self.create_traffic_graph()
        self.threat_gauge = self.create_threat_gauge()
        self.monitoring_table = self.create_monitoring_table()
        self.firewall = None  # Placeholder for future integration
        self.chat_log = ft.Column(scroll=ft.ScrollMode.AUTO, height=250)
        self.chat_log.controls.append(ft.Text("Welcome! Type 'threat level' or 'predict: src_ip=X dst_ip=Y protocol=tcp' to interact with ML.", color="#B0B0B0", size=10))
        self.chatbot = self.create_chatbot()
        
        # Data tracking
        self.threat_level = 0.2  # 0-1 scale
    
    def create_sidebar(self):
        "Create left sidebar navigation."
        return ft.Container(
            width=80,
            bgcolor="#1A1A1A",
            content=ft.Column([
                ft.Container(height=20),
                ft.Icon(ft.Icons.DASHBOARD, color="#00FFCC", size=30),
                ft.Container(height=20),
                ft.Icon(ft.Icons.SHIELD, color="#00FFCC", size=30),
                ft.Container(height=20),
                ft.Icon(ft.Icons.ANALYTICS, color="#00FFCC", size=30),
                ft.Container(height=20),
                ft.Icon(ft.Icons.SETTINGS, color="#00FFCC", size=30),
                ft.Container(height=40),
                ft.Button("Start", on_click=self.start_sniffer, bgcolor="#00FFCC", color="#12181B", width=60, height=40)
            ], alignment=ft.MainAxisAlignment.START)
        )
    
    def create_header(self):
        "Create top header bar."
        return ft.Container(
            height=60,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=10,
            padding=ft.Padding.symmetric(horizontal=20),
            content=ft.Row([
                ft.Text(
                    "WATCHDOG AI",
                    size=24,
                    color="#00FFCC",
                    weight=ft.FontWeight.BOLD
                ),
                ft.Container(expand=True),  # Spacer
                ft.Text("Auckland, NZ", color="#B0B0B0"),
                ft.Text("Last Alert: 2 min ago", color="#FFA500"),
                ft.Button("Refresh", on_click=self.update_ui, bgcolor="#00FFCC", color="#12181B")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        )
    
    def create_status_gauge(self):
        "Create central system status circular gauge with concentric rings."
        return ft.Container(
            height=200,
            width=200,
            content=ft.Stack([
                # Outer ring (background)
                ft.Container(
                    padding=ft.Padding.all(0),
                    content=ft.Container(
                        width=200,
                        height=200,
                        border=ft.Border.all(10, "#333333"),
                        border_radius=100,
                    )
                ),
                # Inner ring (status)
                ft.Container(
                    padding=ft.Padding.only(left=10, top=10),
                    content=ft.Container(
                        width=180,
                        height=180,
                        border=ft.Border.all(10, "#00FFCC"),
                        border_radius=90,
                    )
                ),
                # Center text
                ft.Container(
                    padding=ft.Padding.only(left=40, top=40),
                    content=ft.Container(
                        width=120,
                        height=120,
                        content=ft.Column([
                            ft.Text("SYSTEM", size=12, color="#00FFCC", text_align=ft.TextAlign.CENTER),
                            ft.Text("STATUS", size=12, color="#00FFCC", text_align=ft.TextAlign.CENTER),
                            ft.Text("SAFE", size=16, color="#00FFCC", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
                    )
                )
            ])
        )
    
    def create_traffic_graph(self):
        "Create network traffic display (text-based since charts not available)."
        return ft.Container(
            height=250,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=15,
            padding=15,
            content=ft.Column([
                ft.Text("NETWORK TRAFFIC", size=14, color="#00FFCC", weight=ft.FontWeight.BOLD),
                ft.Container(height=20),  # Spacer
                self.current_packets,
                ft.Container(height=10),  # Spacer
                self.monitoring_status,
                ft.Container(height=20),  # Spacer
                ft.Text("Real-time packet count display", color="#B0B0B0", size=10)
            ])
        )
    
    def create_threat_gauge(self):
        "Create threat level semi-circular gauge."
        # Use ProgressRing for circular gauge
        threat_level = 0.2  # Local for demo
        threat_color = "#00FF00" if threat_level < 0.3 else "#FFA500" if threat_level < 0.7 else "#FF0000"
        threat_text = "LOW" if threat_level < 0.3 else "MEDIUM" if threat_level < 0.7 else "HIGH"
        
        return ft.Container(
            height=150,
            width=200,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=10,
            padding=10,
            content=ft.Column([
                ft.Text("THREAT LEVEL", size=12, color="#FFA500"),
                ft.Container(
                    height=80,
                    alignment=ft.MainAxisAlignment.CENTER,
                    content=ft.ProgressRing(
                        value=threat_level,
                        bgcolor="#333333",
                        color=threat_color,
                        stroke_width=8,
                    )
                ),
                ft.Text(threat_text, size=16, color=threat_color, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.CENTER)
        )
    
    def create_monitoring_table(self):
        "Create active monitoring data table."
        columns = [
            ft.DataColumn(ft.Text("Time", color="#00FFCC")),
            ft.DataColumn(ft.Text("Source IP", color="#00FFCC")),
            ft.DataColumn(ft.Text("Classification", color="#00FFCC")),
            ft.DataColumn(ft.Text("Action", color="#00FFCC")),
        ]
        
        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("12:34:56", color="#B0B0B0")),
                ft.DataCell(ft.Text("192.168.1.100", color="#B0B0B0")),
                ft.DataCell(ft.Text("Normal", color="#00FF00")),
                ft.DataCell(ft.Text("Allow", color="#00FF00")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("12:35:12", color="#B0B0B0")),
                ft.DataCell(ft.Text("10.0.0.5", color="#B0B0B0")),
                ft.DataCell(ft.Text("Normal", color="#00FF00")),
                ft.DataCell(ft.Text("Allow", color="#00FF00")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("12:35:45", color="#B0B0B0")),
                ft.DataCell(ft.Text("172.16.0.10", color="#B0B0B0")),
                ft.DataCell(ft.Text("Suspicious", color="#FFA500")),
                ft.DataCell(ft.Text("Monitor", color="#FFA500")),
            ]),
        ]
        
        table = ft.DataTable(
            columns=columns,
            rows=rows,
            border=ft.Border.all(1, "#333333"),
            horizontal_lines=ft.Border.all(1, "#333333"),
            vertical_lines=ft.Border.all(1, "#333333"),
        )
        
        return ft.Container(
            height=300,
            width=400,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=10,
            padding=10,
            content=ft.Column([
                ft.Text("ACTIVE MONITORING", size=12, color="#00FFCC"),
                ft.Container(
                    expand=True,
                    content=table
                )
            ])
        )
    
    def create_chatbot(self):
        "Create chatbot sidebar."
        return ft.Container(
            width=250,
            height=330,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            border_radius=10,
            padding=10,
            content=ft.Column([
                ft.Text("AI ASSISTANT", size=12, color="#00FFCC"),
                self.chat_log,
                ft.TextField(
                    label="Ask me...",
                    on_submit=self.handle_chat,
                    border_color="#00FFCC",
                    focused_border_color="#00FFCC"
                )
            ], spacing=10)
        )
    
    def handle_chat(self, e):
        "Handle chat input submission."
        user_msg = e.control.value.strip()
        if user_msg:
            self.chat_log.controls.append(ft.Text(f"You: {user_msg}", color="#00FFCC"))
            response = self.process_command(user_msg)
            self.chat_log.controls.append(ft.Text(f"AI: {response}", color="#B0B0B0"))
            e.control.value = ""
            self.chat_log.update()
            e.control.update()
            self.page.update()
    
    def start_sniffer(self, e):
        "Launch the sniffer service."
        import subprocess
        self.sniffer_process = subprocess.Popen(['sudo', 'python3', '-m', 'src.network.sniffer_service'], cwd='/Users/bpu/Documents/Uni/Watchdog')
    
    def process_command(self, msg):
        "Process user commands, including ML-powered analysis."
        msg_lower = msg.lower()
        
        # Check if ML model is available
        if not self.model or not self.extractor:
            return "ML model not available. Please ensure models/random_forest_model.pkl exists."
        
        if msg_lower == "status":
            return "System status: SAFE - All systems operational."
        elif msg_lower in ["alerts", "alert"]:
            return "Recent alerts: Suspicious packet from 172.16.0.10."
        elif msg_lower.startswith("block "):
            ip = msg.split()[1]
            return f"Mock blocked IP: {ip} (firewall integration pending)."
        elif msg_lower.startswith("unblock "):
            ip = msg.split()[1]
            return f"Mock unblocked IP: {ip} (firewall integration pending)."
        elif msg_lower in ["hi", "hello", "hey", "greetings"]:
            return "Hello! I'm the AI assistant for WATCHDOG. I can help with threat analysis, packet predictions, and system status. Try commands like 'threat level' or 'predict: src_ip=192.168.1.1 dst_ip=10.0.0.1 protocol=tcp'."
        elif msg_lower in ["threat level", "current threat", "threat"]:
            threat_text = "LOW" if self.threat_level < 0.3 else "MEDIUM" if self.threat_level < 0.7 else "HIGH"
            return f"Current threat level: {threat_text} ({self.threat_level:.2f})"
        elif msg_lower.startswith("predict"):
            # Parse packet data from message, e.g., "predict: src_ip=192.168.1.1 dst_ip=10.0.0.1 protocol=tcp src_port=80 dst_port=443"
            try:
                # Extract parameters after "predict:"
                params_str = msg.split(":", 1)[1].strip() if ":" in msg else ""
                if not params_str:
                    return "Usage: predict: src_ip=X dst_ip=Y protocol=Z src_port=A dst_port=B"
                
                # Parse parameters
                params = {}
                for pair in params_str.split():
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key.strip()] = value.strip()
                
                # Create packet data dict
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
                
                # Extract features
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                
                # Predict
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                
                # Map prediction
                label_map = {0: 'normal', 1: 'attack'}
                predicted_label = label_map.get(prediction, 'unknown')
                
                return f"ML Prediction for packet {packet_data['src_ip']}:{packet_data['src_port']} -> {packet_data['dst_ip']}:{packet_data['dst_port']}: {predicted_label.upper()}"
                
            except Exception as e:
                return f"Error processing prediction: {str(e)}. Usage: predict: src_ip=X dst_ip=Y protocol=Z src_port=A dst_port=B"
        
        elif msg_lower.startswith("explain log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                return self.ai_client.query(EXPLANATION_PROMPT.format(log=formatted))
            except Exception as e:
                return f"Error processing log: {str(e)}"
        
        elif msg_lower.startswith("analyze log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                return self.ai_client.query(TECHNICAL_ANALYSIS_PROMPT.format(log=formatted))
            except Exception as e:
                return f"Error processing log: {str(e)}"
        
        else:
            return self.ai_client.query(GENERAL_PROMPT.format(query=msg))
    
    def update_ui(self, e):
        "Update UI components with real-time data."
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {"packets": [], "alerts": []}
        
        # Update monitoring table with last 5 packets
        packets = data.get("packets", [])[-5:]
        rows = []
        for pkt in packets:
            time_str = pkt.get("time", "")
            src_ip = pkt.get("src_ip", "")
            classification = pkt.get("classification", "Normal")
            action = pkt.get("action", "Allow")
            color = "#FFA500" if classification.lower() == "suspicious" else "#00FF00"
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(time_str, color="#B0B0B0")),
                ft.DataCell(ft.Text(src_ip, color="#B0B0B0")),
                ft.DataCell(ft.Text(classification, color=color)),
                ft.DataCell(ft.Text(action, color=color)),
            ]))
        self.monitoring_table.content.controls[1].content.rows = rows
        
        # Update traffic display with packet count
        packet_count = len(packets)
        self.current_packets.value = f"Packets: {packet_count}"
        self.current_packets.update()
        
        # Update monitoring status
        self.monitoring_status.value = "Status: Monitoring active" if packet_count > 0 else "Status: Waiting for data"
        self.monitoring_status.update()
        
        self.last_packet_count = packet_count
        
        self.page.update()
    
    def main(self, page: ft.Page):
        "Main application entry point."
        self.page = page  # Add this line to fix chat functionality
        page.title = "WATCHDOG AI - Modern Dashboard"
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#12181B"
        page.window_width = 1400
        page.window_height = 900
        
        # Layout structure
        main_content = ft.Column([
            self.header,
            ft.Container(height=20),  # Spacer
            ft.ResponsiveRow([
                ft.Container(col=4, content=self.status_gauge),
                ft.Container(col=4, content=self.traffic_graph),
                ft.Container(col=4, content=self.threat_gauge),
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),  # Spacer
            ft.Row([
                ft.Container(expand=True, content=self.monitoring_table),
                ft.Container(width=250, content=self.chatbot),
            ], alignment=ft.MainAxisAlignment.START),
        ], spacing=0)
        
        layout = ft.Row([
            self.sidebar,
            ft.Container(
                content=main_content,
                expand=True,
                padding=20
            )
        ])
        
        page.add(layout)
        
        # Manual refresh available via button
    
    # def start_monitoring(self, page):
    #     "Start monitoring data file for updates."
    #     # Will implement real-time updates
    #     pass

def run_app(page):
    "Main entry point for Flet app."
    dashboard = ModernDashboard()
    dashboard.main(page)

if __name__ == "__main__":
    ft.app(target=run_app)
