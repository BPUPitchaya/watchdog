"""
Integration Testing: ML Model with Network Monitoring
Captures packets, extracts features, predicts intrusions in real-time.
"""

import time
import joblib
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
from feature_extractor import FeatureExtractor

def packet_callback(packet):
    """Process each captured packet for feature extraction and prediction."""
    if IP in packet:
        # Extract basic packet information
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        protocol = packet[IP].proto
        length = len(packet)
        
        # Determine protocol name
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
        
        # Create packet data dict
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
        
        # Extract features
        features = extractor.extract_packet_features(packet_data)
        selected_features = extractor.get_selected_features(features)
        
        # Predict
        features_array = np.array(selected_features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        
        # Map prediction back to label (simplified)
        label_map = {0: 'normal', 1: 'attack'}  # Simplified
        predicted_label = label_map.get(prediction, 'unknown')
        
        # Print result
        if prediction != 0:  # Assuming 0 is normal
            print(f"⚠️  POTENTIAL ATTACK DETECTED: {src_ip}:{src_port} -> {dst_ip}:{dst_port} [{protocol_name}] - Predicted: {predicted_label}")
        else:
            print(f"✓ Normal traffic: {src_ip}:{src_port} -> {dst_ip}:{dst_port} [{protocol_name}]")

def main():
    """Main integration testing function."""
    global extractor, model
    
    print("Loading ML model...")
    model_path = 'models/random_forest_model.pkl'
    model = joblib.load(model_path)
    print(f"Model loaded from {model_path}")
    
    print("Initializing feature extractor...")
    extractor = FeatureExtractor()
    
    print("Starting packet capture for integration testing...")
    print("Monitoring network traffic for 30 seconds...")
    print("Press Ctrl+C to stop early")
    
    try:
        # Capture packets for 30 seconds
        sniff(
            prn=packet_callback,
            store=0,
            timeout=30,
            iface=None  # Use default interface
        )
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    print("\nIntegration testing complete!")
    print("Packets captured and analyzed with ML model.")

if __name__ == "__main__":
    main()
