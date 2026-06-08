"""
Network sniffer service that runs independently and writes to shared data file.
This allows the UI to run without root privileges while the sniffer runs with sudo.
"""

import json
import time
import threading
import numpy as np
import joblib
from scapy.all import sniff, IP, TCP, UDP
from src.ml.feature_extractor import FeatureExtractor
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
        self.model = None
        self.extractor = None
        self.packet_buffer = []  # Buffer for batch processing
        self.batch_size = 10  # Process packets in batches of 10
        self.last_write_time = 0
        self.write_interval = 1.0  # Write to file at most every 1 second
        
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
            length = len(packet)
            
            # Determine protocol name and ports
            if protocol == 6:  # TCP
                protocol_name = "tcp"
                if TCP in packet:
                    src_port = packet[TCP].sport
                    dst_port = packet[TCP].dport
                    flags = str(packet[TCP].flags)
                else:
                    src_port = 0
                    dst_port = 0
                    flags = 'N'
            elif protocol == 17:  # UDP
                protocol_name = "udp"
                if UDP in packet:
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport
                else:
                    src_port = 0
                    dst_port = 0
                flags = 'N'
            else:
                protocol_name = f"proto_{protocol}"
                src_port = 0
                dst_port = 0
                flags = 'N'
            
            # Create packet data for feature extraction
            packet_data = {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'protocol': protocol,
                'length': length,
                'src_port': src_port,
                'dst_port': dst_port,
                'flags': flags,
                'direction': 'outbound' if src_ip.startswith('192.168.') else 'inbound'  # Simplified
            }
            
            # If ML is not available, store packet without prediction
            if self.model is None or self.extractor is None:
                packet_info = {
                    'count': self.packet_count,
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'protocol': protocol_name,
                    'timestamp': time.time(),
                    'prediction': 'unavailable',
                    'is_attack': False
                }
                self.captured_packets.append(packet_info)
                print(f"✓ Traffic (no ML): {src_ip}:{src_port} -> {dst_ip}:{dst_port} [{protocol_name}]")
            else:
                # Add to buffer for batch processing
                self.packet_buffer.append({
                    'packet_data': packet_data,
                    'src_ip': src_ip,
                    'dst_ip': dst_ip,
                    'protocol_name': protocol_name,
                    'src_port': src_port,
                    'dst_port': dst_port,
                    'count': self.packet_count,
                    'timestamp': time.time()
                })
                
                # Process batch if buffer is full
                if len(self.packet_buffer) >= self.batch_size:
                    self.process_batch()
            
            # Write to file periodically
            current_time = time.time()
            if current_time - self.last_write_time >= self.write_interval:
                self.write_data()
                self.last_write_time = current_time
    
    def process_batch(self):
        """Process buffered packets in batch for ML inference."""
        if not self.packet_buffer:
            return
        
        try:
            # Extract features for all packets in buffer
            features_list = []
            for packet in self.packet_buffer:
                features = self.extractor.extract_packet_features(packet['packet_data'])
                selected_features = self.extractor.get_selected_features(features)
                features_list.append(selected_features)
            
            # Convert to numpy array for batch prediction
            features_array = np.array(features_list)
            
            # Batch prediction
            predictions = self.model.predict(features_array)
            label_map = {0: 'normal', 1: 'attack'}
            
            # Process results and store packet info
            for i, packet in enumerate(self.packet_buffer):
                prediction = predictions[i]
                predicted_label = label_map.get(prediction, 'unknown')
                
                packet_info = {
                    'count': packet['count'],
                    'src_ip': packet['src_ip'],
                    'dst_ip': packet['dst_ip'],
                    'protocol': packet['protocol_name'],
                    'timestamp': packet['timestamp'],
                    'prediction': predicted_label,
                    'is_attack': prediction == 1
                }
                
                self.captured_packets.append(packet_info)
                
                # Print packet info and alerts
                if prediction == 1:
                    print(f"⚠️  POTENTIAL ATTACK DETECTED: {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']} [{packet['protocol_name']}] - Predicted: {predicted_label}")
                else:
                    print(f"✓ Normal traffic: {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']} [{packet['protocol_name']}]")
        
        except Exception as e:
            print(f"Error in batch prediction: {e}")
            # Fallback: process packets as normal (no prediction)
            for packet in self.packet_buffer:
                packet_info = {
                    'count': packet['count'],
                    'src_ip': packet['src_ip'],
                    'dst_ip': packet['dst_ip'],
                    'protocol': packet['protocol_name'],
                    'timestamp': packet['timestamp'],
                    'prediction': 'error',
                    'is_attack': False
                }
                self.captured_packets.append(packet_info)
        
        # Clear buffer
        self.packet_buffer = []
    
    def write_data(self):
        """Write packet data to shared file."""
        # Keep only the last 100 packets in memory to avoid memory issues
        packets_to_save = self.captured_packets[-100:] if len(self.captured_packets) > 100 else self.captured_packets
        
        data = {
            'status': 'running' if self.is_running else 'stopped',
            'packet_count': self.packet_count,
            'packets': packets_to_save,
            'alerts': [p for p in packets_to_save if p.get('is_attack', False)]
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
        
        # Load ML components if not loaded
        if self.model is None:
            try:
                self.model = joblib.load('models/random_forest_model.pkl')
                self.extractor = FeatureExtractor()
                print("ML model and feature extractor loaded successfully.")
            except FileNotFoundError:
                print("ERROR: ML model file not found. Running without threat detection.")
                print("Please ensure models/random_forest_model.pkl exists.")
                self.model = None
                self.extractor = None
            except Exception as e:
                print(f"ERROR loading ML components: {e}")
                print("Running without threat detection.")
                self.model = None
                self.extractor = None
        
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
        except PermissionError:
            print("\nERROR: Permission denied when trying to capture network traffic.")
            print("SOLUTION: Run the application with sudo/administrator privileges.")
            print("Example: sudo python src/network/sniffer_service.py")
        except OSError as e:
            if "Operation not permitted" in str(e):
                print("\nERROR: Operation not permitted - insufficient privileges for network capture.")
                print("SOLUTION: Run with sudo/administrator privileges.")
            else:
                print(f"\nERROR: Network interface error: {e}")
                print("SOLUTION: Check if the network interface exists and is accessible.")
        except Exception as e:
            print(f"\nERROR during packet capture: {e}")
            print("SOLUTION: Check network interface and permissions.")
        finally:
            self.is_running = False
            # Process any remaining packets
            if self.packet_buffer:
                print(f"Processing {len(self.packet_buffer)} remaining packets...")
                self.process_batch()
            self.write_data()
            print(f"Packet capture completed. Total packets captured: {self.packet_count}.")
    
    def stop_sniffing(self):
        """Stop packet capture."""
        self.is_running = False
        print("Stopping packet capture...")
        
        # Process any remaining packets in buffer
        if self.packet_buffer:
            print(f"Processing {len(self.packet_buffer)} remaining packets in buffer...")
            self.process_batch()
        
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
