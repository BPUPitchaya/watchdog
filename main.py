"""
Main application for Watchdog - Network Security Monitoring System.
This integrates Flet UI with Scapy packet capture functionality.
"""

import flet as ft
import threading
import time
from src.network.basic_sniffer import BasicSniffer


class WatchdogApp:
    """Main Watchdog application class."""
    
    def __init__(self):
        self.sniffer = BasicSniffer()
        self.is_sniffing = False
        
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
        
        self.start_button = ft.ElevatedButton(
            "Start Sniffing",
            on_click=self.start_sniffing_handler,
            icon=ft.icons.PLAY_ARROW,
            bgcolor=ft.Colors.GREEN_500,
            color=ft.Colors.WHITE
        )
        
        self.stop_button = ft.ElevatedButton(
            "Stop Sniffing",
            on_click=self.stop_sniffing_handler,
            icon=ft.icons.STOP,
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
            border=ft.border.all(2, ft.Colors.BLUE_GREY_300),
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
                packet_display
            ],
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
        
        # Add content to page
        page.add(content)
        
        # Store page reference for updates
        self.page = page
    
    def start_sniffing_handler(self, e):
        """Handle start sniffing button click."""
        if self.is_sniffing:
            return
            
        self.is_sniffing = True
        self.status_text.value = "Status: Sniffing..."
        self.status_text.color = ft.Colors.ORANGE_600
        self.start_button.disabled = True
        self.stop_button.disabled = False
        
        # Clear previous packets
        self.packet_list.controls.clear()
        self.sniffer.captured_packets.clear()
        
        self.page.update()
        
        # Start sniffing in background thread
        sniff_thread = threading.Thread(
            target=self.sniffing_worker,
            daemon=True
        )
        sniff_thread.start()
    
    def stop_sniffing_handler(self, e):
        """Handle stop sniffing button click."""
        if not self.is_sniffing:
            return
            
        self.is_sniffing = False
        self.sniffer.stop_sniffing()
        
        self.status_text.value = "Status: Stopped"
        self.status_text.color = ft.Colors.RED_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        self.page.update()
    
    def sniffing_worker(self):
        """Background worker for packet sniffing."""
        try:
            # Start continuous sniffing
            self.sniffer.start_sniffing(packet_count=50)  # Capture 50 packets then stop
            
        except Exception as e:
            print(f"Sniffing error: {e}")
        
        # Update UI when done
        self.page.run_thread(self.update_ui_after_sniffing)
    
    def update_ui_after_sniffing(self):
        """Update UI after sniffing completes."""
        self.is_sniffing = False
        self.status_text.value = "Status: Ready"
        self.status_text.color = ft.Colors.GREEN_600
        self.start_button.disabled = False
        self.stop_button.disabled = True
        
        # Update packet count
        count = self.sniffer.get_packet_count()
        self.packet_count_text.value = f"Packets Captured: {count}"
        
        # Display captured packets
        packets = self.sniffer.get_captured_packets()
        for packet in packets:
            packet_text = ft.Text(
                f"#{packet['count']}: {packet['src_ip']} -> {packet['dst_ip']} [{packet['protocol']}]",
                size=12,
                color=ft.Colors.BLUE_GREY_800
            )
            self.packet_list.controls.append(packet_text)
        
        self.page.update()


def main():
    """Main entry point for the application."""
    app = WatchdogApp()
    ft.run(target=app.main)


if __name__ == "__main__":
    main()
