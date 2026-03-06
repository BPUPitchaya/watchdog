"""
Integrated Watchdog - Runs both UI and sniffer service in one terminal.
Uses subprocess to manage the sniffer service with proper permissions.
"""

import flet as ft
import threading
import time
import json
import os
import subprocess
import sys
import signal


class IntegratedWatchdog:
    """Integrated Watchdog application with built-in sniffer management."""
    
    def __init__(self):
        self.data_file = "packet_data.json"
        self.stop_signal_file = "stop_signal.txt"
        self.is_sniffing = False
        self.sniffer_process = None
        self.last_packet_count = 0
        self.alerts_list = ft.ListView(expand=1, spacing=5, padding=10, auto_scroll=True)
        
    def main(self, page: ft.Page):
        """Main application entry point."""
        # Page setup
        page.title = "Watchdog - Network Security Monitor"
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        page.bgcolor = ft.Colors.BLUE_GREY_50
        page.window_width = 800
        page.window_height = 600
        
        # UI Components
        self.status_text = ft.Text(
            "Status: Ready",
            size=20,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_600
        )
        
        self.packet_count_text = ft.Text(
            "Packets Captured: 0",
            size=16,
            color=ft.Colors.BLUE_GREY_700
        )
        
        self.start_button = ft.Button(
            "Start Sniffing",
            on_click=self.start_sniffing_handler,
            bgcolor=ft.Colors.GREEN_500,
            color=ft.Colors.WHITE
        )
        
        self.stop_button = ft.Button(
            "Stop Sniffing",
            on_click=self.stop_sniffing_handler,
            bgcolor=ft.Colors.RED_500,
            color=ft.Colors.WHITE,
            disabled=True
        )
        
        # Packet display area
        self.packet_list = ft.ListView(
            expand=1,
            spacing=5,
            padding=10,
            auto_scroll=True
        )
        
        # Main layout
        header = ft.Column(
            [
                ft.Text(
                    "Watchdog Network Monitor",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_800
                ),
                ft.Text(
                    "Real-time Network Packet Analysis",
                    size=16,
                    color=ft.Colors.BLUE_GREY_600
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5
        )
        
        status_section = ft.Row(
            [
                self.status_text,
                self.packet_count_text
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND
        )
        
        controls = ft.Row(
            [
                self.start_button,
                self.stop_button
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        
        # Packet display container
        packet_display = ft.Container(
            content=self.packet_list,
            border=ft.Border.all(2, ft.Colors.BLUE_GREY_300),
            border_radius=10,
            bgcolor=ft.Colors.WHITE,
            padding=10,
            height=300
        )
        
        # Main content column
        content = ft.Column(
            [
                header,
                ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                status_section,
                controls,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text(
                    "Captured Packets:",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_GREY_700
                ),
                packet_display,
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Text(
                    "Attack Alerts:",
                    size=18,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_700
                ),
                ft.Container(
                    content=self.alerts_list,
                    border=ft.Border.all(2, ft.Colors.RED_300),
                    border_radius=10,
                    bgcolor=ft.Colors.WHITE,
                    padding=10,
                    height=200
                )
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        
        # Add content to page
        page.add(content)
        
        # Store page reference for updates
        self.page = page
        
        # Start monitoring thread
        monitor_thread = threading.Thread(
            target=self.monitor_sniffer,
            daemon=True
        )
        monitor_thread.start()
    
    def start_sniffing_handler(self, e):
        """Handle start sniffing button click."""
        if self.is_sniffing:
            return
            
        self.is_sniffing = True
        self.status_text.value = "Status: Starting sniffer..."
        self.status_text.color = ft.Colors.ORANGE_600
        self.start_button.disabled = True
        self.stop_button.disabled = False
        
        # Clear previous packets
        self.packet_list.controls.clear()
        
        self.page.update()
        
        # Start sniffer process with sudo
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()
            # Use sudo for the sniffer service only
            self.sniffer_process = subprocess.Popen(
                ["sudo", sys.executable, "-m", "src.network.sniffer_service", "start"],
                cwd=os.getcwd(),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Start monitoring the output
            output_thread = threading.Thread(
                target=self.monitor_sniffer_output,
                daemon=True
            )
            output_thread.start()
            
        except Exception as e:
            self.show_error(f"Failed to start sniffer: {str(e)}")
    
    def stop_sniffing_handler(self, e):
        """Handle stop sniffing button click."""
        if not self.is_sniffing:
            return
            
        self.is_sniffing = False
        
        # Create stop signal file
        try:
            with open(self.stop_signal_file, 'w') as f:
                f.write("stop")
        except Exception as e:
            print(f"Error creating stop signal: {e}")
        
        # Stop the sniffer process
        if self.sniffer_process:
            try:
                self.sniffer_process.terminate()
                self.sniffer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.sniffer_process.kill()
            except:
                pass
        
        self.status_text.value = "Status: Stopped"
        self.status_text.color = ft.Colors.RED_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        self.page.update()
    
    def monitor_sniffer_output(self):
        """Monitor sniffer process output."""
        if self.sniffer_process:
            for line in iter(self.sniffer_process.stdout.readline, ''):
                if line:
                    print(f"Sniffer: {line.strip()}")
    
    def monitor_sniffer(self):
        """Monitor the shared packet data file."""
        while True:
            try:
                if os.path.exists(self.data_file):
                    with open(self.data_file, 'r') as f:
                        data = json.load(f)
                    
                    # Update UI with new data
                    self.page.run_thread(lambda: self.update_ui_from_data(data))
                        
            except Exception as e:
                pass  # Ignore file reading errors
            
            time.sleep(1)  # Check every second
    
    def update_ui_from_data(self, data):
        """Update UI from shared data."""
        # Always update status based on data
        status = data.get('status', 'stopped')
        if status == 'running':
            self.status_text.value = "Status: Sniffing..."
            self.status_text.color = ft.Colors.ORANGE_600
        elif status == 'stopped':
            if self.is_sniffing:  # Only update if we were sniffing
                self.status_text.value = "Status: Stopped"
                self.status_text.color = ft.Colors.RED_600
                self.start_button.disabled = False
                self.stop_button.disabled = True
                self.is_sniffing = False
        
        # Update packet count
        count = data.get('packet_count', 0)
        self.packet_count_text.value = f"Packets Captured: {count}"
        
        # Get current packets from data
        packets = data.get('packets', [])
        
        # Only update packet display if we're actively sniffing or have packets to show
        if self.is_sniffing or packets:
            # Clear the display and show all current packets
            self.packet_list.controls.clear()
            
            # Display all packets from the data file (these are already the latest 100)
            for packet in packets[self.last_packet_count:]:
                color = ft.Colors.RED_600 if packet.get('is_attack') else ft.Colors.BLUE_GREY_800
                prediction = packet.get('prediction', 'unknown')
                packet_text = ft.Text(
                    f"#{packet['count']}: {packet['src_ip']} -> {packet['dst_ip']} [{packet['protocol']}] - {prediction}",
                    size=12,
                    color=color
                )
                self.packet_list.controls.append(packet_text)
        
            self.last_packet_count = len(packets)
        
            # Update alerts
            alerts = data.get('alerts', [])
            self.alerts_list.controls.clear()
            for alert in alerts[-10:]:
                alert_text = ft.Text(
                    f"#{alert['count']}: {alert['src_ip']} -> {alert['dst_ip']} [{alert['protocol']}] - {alert['prediction']}",
                    size=12,
                    color=ft.Colors.RED_600
                )
                self.alerts_list.controls.append(alert_text)
        
            self.page.update()
        
        # Update our counter
        self.last_packet_count = len(packets)
    
    def show_error(self, message):
        """Show error message in UI."""
        self.status_text.value = f"Error: {message}"
        self.status_text.color = ft.Colors.RED_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        self.is_sniffing = False
        self.page.update()
    
    def cleanup(self):
        """Clean up resources on exit."""
        if self.sniffer_process:
            try:
                self.sniffer_process.terminate()
            except:
                pass
        
        # Clean up signal files
        for file in [self.stop_signal_file, self.data_file]:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    print("\nShutting down...")
    if 'app' in globals():
        app.cleanup()
    sys.exit(0)


def main():
    """Main entry point for the integrated application."""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    app = IntegratedWatchdog()
    
    try:
        ft.run(app.main)
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
