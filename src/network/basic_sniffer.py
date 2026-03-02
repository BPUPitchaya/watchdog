"""
Basic packet sniffer using Scapy for Watchdog.
This module demonstrates basic packet capture functionality.
"""

from scapy.all import sniff, IP, TCP, UDP
import threading
import time


class BasicSniffer:
    """Basic network packet sniffer."""
    
    def __init__(self):
        self.is_running = False
        self.packet_count = 0
        self.captured_packets = []
        
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
            
            # Print packet info (for testing)
            print(f"Packet #{self.packet_count}: {src_ip} -> {dst_ip} [{protocol_name}]")
    
    def start_sniffing(self, packet_count=10, interface=None):
        """Start packet capture."""
        if self.is_running:
            print("Sniffer is already running!")
            return
            
        self.is_running = True
        self.packet_count = 0
        self.captured_packets = []
        
        print(f"Starting packet capture (capturing {packet_count} packets)...")
        
        try:
            # Start sniffing
            sniff(
                prn=self.packet_callback,
                store=0,
                count=packet_count,
                iface=interface
            )
        except KeyboardInterrupt:
            print("\nPacket capture stopped by user.")
        except Exception as e:
            print(f"Error during packet capture: {e}")
        finally:
            self.is_running = False
            print(f"Packet capture completed. Captured {self.packet_count} packets.")
    
    def stop_sniffing(self):
        """Stop packet capture."""
        self.is_running = False
        print("Stopping packet capture...")
    
    def get_captured_packets(self):
        """Return list of captured packets."""
        return self.captured_packets.copy()
    
    def get_packet_count(self):
        """Return number of captured packets."""
        return self.packet_count


def test_sniffer():
    """Test function for the basic sniffer."""
    sniffer = BasicSniffer()
    print("Testing basic packet sniffer...")
    sniffer.start_sniffing(packet_count=5)
    
    captured = sniffer.get_captured_packets()
    print(f"\nCaptured {len(captured)} packets:")
    for packet in captured:
        print(f"  {packet['count']}: {packet['src_ip']} -> {packet['dst_ip']} [{packet['protocol']}]")


if __name__ == "__main__":
    test_sniffer()
