"""
Main application for Watchdog - Network Security Monitoring System.
This integrates Flet UI with Scapy packet capture functionality.
"""

import flet as ft
import threading
import time
import json
import os

# Import your T&C view!
from src.ui.tnc import tnc_view


class WatchdogApp:
    """Main Watchdog application class."""
    
    def __init__(self):
        self.data_file = "packet_data.json"
        self.stop_signal_file = "stop_signal.txt"
        self.is_sniffing = False
        self.last_packet_count = 0
        self.page = None
        
        # Initialize UI Components here so background threads can update them safely
        self.status_text = ft.Text("Status: Ready", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
        self.packet_count_text = ft.Text("Packets Captured: 0", size=16, color=ft.Colors.BLUE_GREY_700)
        
        self.start_button = ft.ElevatedButton("Start Sniffing", on_click=self.start_sniffing_handler, bgcolor=ft.Colors.GREEN_500, color=ft.Colors.WHITE)
        self.stop_button = ft.ElevatedButton("Stop Sniffing", on_click=self.stop_sniffing_handler, bgcolor=ft.Colors.RED_500, color=ft.Colors.WHITE, disabled=True)
        
        self.packet_list = ft.ListView(expand=1, spacing=5, padding=10, auto_scroll=True)

    def get_dashboard_view(self):
        """Assembles and returns the Dashboard UI view."""
        header = ft.Column(
            [
                ft.Text("Watchdog Network Monitor", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_800),
                ft.Text("Real-time Network Packet Analysis", size=16, color=ft.Colors.BLUE_GREY_600),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )
        
        status_section = ft.Row([self.status_text, self.packet_count_text], alignment=ft.MainAxisAlignment.SPACE_AROUND)
        controls = ft.Row([self.start_button, self.stop_button], alignment=ft.MainAxisAlignment.CENTER)
        
        packet_display = ft.Container(
            content=self.packet_list,
            border=ft.border.all(2, ft.Colors.BLUE_GREY_300),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            padding=10,
            height=300
        )
        
        content = ft.Column(
            [
                header,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                status_section,
                controls,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text("Captured Packets:", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_GREY_700),
                packet_display
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )

        return ft.View(
            route="/dashboard",
            controls=[content],
            bgcolor=ft.Colors.BLUE_GREY_50,
            padding=30
        )
        
    def main(self, page: ft.Page):
        """Main application entry point."""
        self.page = page
        
        # General Page setup
        page.title = "Watchdog - Network Security Monitor"
        page.window_width = 800
        page.window_height = 600

        # Router function to handle switching screens
        def route_change(route):
            page.views.clear()
            
            # 1. Load the T&C page
            if page.route == "/tnc" or page.route == "/":
                page.views.append(tnc_view(page))
                
            # 2. Load the Dashboard page
            elif page.route == "/dashboard":
                page.views.append(self.get_dashboard_view())
                
            page.update()

        # Listen for route changes
        page.on_route_change = route_change
        
        # Start the application by going to the T&C page
        page.go("/tnc")
    
    # ----------------------------------------------------
    # Background Logic & Handlers (Unchanged)
    # ----------------------------------------------------
    def start_sniffing_handler(self, e):
        if self.is_sniffing: return
        self.is_sniffing = True
        self.status_text.value = "Status: Waiting for sniffer service..."
        self.status_text.color = ft.Colors.ORANGE_600
        self.start_button.disabled = True
        self.stop_button.disabled = False
        self.packet_list.controls.clear()
        self.page.update()
        threading.Thread(target=self.monitor_sniffer, daemon=True).start()
    
    def stop_sniffing_handler(self, e):
        if not self.is_sniffing: return
        self.is_sniffing = False
        try:
            with open(self.stop_signal_file, 'w') as f: f.write("stop")
        except Exception as e:
            print(f"Error creating stop signal: {e}")
        self.status_text.value = "Status: Stopped"
        self.status_text.color = ft.Colors.RED_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.page.update()
    
    def monitor_sniffer(self):
        while self.is_sniffing:
            try:
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r') as f: data = json.load(f)
                    self.page.run_thread(lambda: self.update_ui_from_data(data))
                    if data.get('status') == 'stopped': break
            except Exception as e:
                print(f"Error reading data: {e}")
            time.sleep(1)
        self.page.run_thread(self.update_ui_after_sniffing)
    
    def update_ui_from_data(self, data):
        if not self.is_sniffing: return
        if data.get('status') == 'running':
            self.status_text.value = "Status: Sniffing..."
            self.status_text.color = ft.Colors.ORANGE_600
        
        count = data.get('packet_count', 0)
        self.packet_count_text.value = f"Packets Captured: {count}"
        
        packets = data.get('packets', [])
        for packet in packets[self.last_packet_count:]:
            packet_text = ft.Text(
                f"#{packet['count']}: {packet['src_ip']} -> {packet['dst_ip']} [{packet['protocol']}]",
                size=12, color=ft.Colors.BLUE_GREY_800
            )
            self.packet_list.controls.append(packet_text)
        
        self.last_packet_count = len(packets)
        self.page.update()
    
    def show_error(self, message):
        self.status_text.value = f"Error: {message}"
        self.status_text.color = ft.Colors.RED_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.is_sniffing = False
        self.page.update()
    
    def update_ui_after_sniffing(self):
        self.is_sniffing = False
        self.status_text.value = "Status: Stopped"
        self.status_text.color = ft.Colors.RED_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f: data = json.load(f)
                count = data.get('packet_count', 0)
                self.packet_count_text.value = f"Packets Captured: {count}"
        except:
            pass
        self.page.update()


def main():
    """Main entry point for the application."""
    app = WatchdogApp()
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        ft.run(app.main, view=ft.AppView.WEB_BROWSER)
    else:
        ft.run(app.main)

if __name__ == "__main__":
    main()