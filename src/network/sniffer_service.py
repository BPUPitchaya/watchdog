"""
Network sniffer service that runs independently and writes to shared data file.
This allows the UI to run without root privileges while the sniffer runs with sudo.
"""

import json
import time
import threading
from scapy.all import sniff, IP, TCP, UDP
import os


class SnifferService:
    """Independent network sniffer service."""
    
    def __init__(self, data_file="packet_data.json"):
        self.data_file = data_file
        self.stop_signal_file = "stop_signal.txt"
        self.is_running = False
        self.keep_running = True
        self.packet_count = 0
        self.captured_packets = []
        
        # Load existing packet count if file exists
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.packet_count = data.get('packet_count', 0)
        except:
            pass
        
    def packet_callback(self, packet):
        """Callback function for each captured packet."""
        if IP in packet:
            self.packet_count += 1
            
            # Extract basic packet information
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = packet[IP].proto
            
            # Determine protocol name
            if protocol == 6:  # TCP
                protocol_name = "TCP"
            elif protocol == 17:  # UDP
                protocol_name = "UDP"
            else:
                protocol_name = f"PROTO-{protocol}"
            
            # Store packet info
            packet_info = {
                'count': self.packet_count,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'protocol': protocol_name,
                'timestamp': time.time()
            }
            
            self.captured_packets.append(packet_info)
            
            # Write to shared file
            self.write_data()
            
            # Print packet info (for testing)
            print(f"Packet #{self.packet_count}: {src_ip} -> {dst_ip} [{protocol_name}]")
    
    def write_data(self):
        """Write packet data to shared file."""
        # Keep only the last 100 packets in memory to avoid memory issues
        packets_to_save = self.captured_packets[-100:] if len(self.captured_packets) > 100 else self.captured_packets
        
        data = {
            'status': 'running' if self.is_running else 'stopped',
            'packet_count': self.packet_count,
            'packets': packets_to_save
        }
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing data: {e}")
    
    def monitor_stop_signal(self):
        """Monitor for stop signal file and stop sniffing when detected."""
        while True:
            if os.path.exists(self.stop_signal_file):
                print("Stop signal received. Stopping sniffer service...")
                os.remove(self.stop_signal_file)
                self.keep_running = False
                self.stop_sniffing()
                break
            time.sleep(0.1)
    
    def start_sniffing(self, packet_count=50, interface=None):
        """Start packet capture."""
        if self.is_running:
            print("Sniffer is already running!")
            return
            
        self.is_running = True
        # Don't reset packet_count - keep it continuous
        # self.packet_count = 0  # Removed this line
        # self.captured_packets = []  # Don't clear all packets, just manage size
        
        print(f"Starting packet capture (capturing {packet_count} packets, total count: {self.packet_count})...")
        self.write_data()
        
        try:
            # Start sniffing
            sniff(
                prn=self.packet_callback,
                store=0,
                count=packet_count,
                iface=interface,
                stop_filter=lambda x: not self.is_running  # Check for stop signal
            )
        except KeyboardInterrupt:
            print("\nPacket capture stopped by user.")
        except Exception as e:
            print(f"Error during packet capture: {e}")
        finally:
            self.is_running = False
            self.write_data()
            print(f"Packet capture completed. Total packets captured: {self.packet_count}.")
    
    def stop_sniffing(self):
        """Stop packet capture."""
        self.is_running = False
        print("Stopping packet capture...")
        # Write stopped status to file
        self.write_data()
        print("Status updated to 'stopped'")


def main():
    """Main entry point for the sniffer service."""
    import sys
    
    # Check if running with root privileges
    if os.geteuid() != 0:
        print("Error: Root privileges required. Run with: sudo python sniffer_service.py")
        sys.exit(1)
    
    service = SnifferService()
    
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        # Start stop signal monitor thread
        stop_monitor_thread = threading.Thread(target=service.monitor_stop_signal, daemon=True)
        stop_monitor_thread.start()
        try:
            while service.keep_running:
                if not service.is_running:
                    service.start_sniffing(packet_count=50)
                
                time.sleep(0.5)  # Brief pause between captures
                
        except KeyboardInterrupt:
            print("\nStopping sniffer service...")
            service.stop_sniffing()
    else:
        # Run single capture
        service.start_sniffing(packet_count=50)


if __name__ == "__main__":
    main()
