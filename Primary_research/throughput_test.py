import sys
import os
import time
import joblib
import pandas as pd

# Add watchdog root directory to system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ml.feature_extractor import FeatureExtractor
from src.firewall_manager import FirewallManager

def run_throughput_benchmark():
    print("Initializing System Throughput Test...")
    model = joblib.load('models/random_forest_model.pkl')
    extractor = FeatureExtractor()
    firewall = FirewallManager()

    SELECTED_FEATURES = [
        'src_bytes', 'same_srv_rate', 'flag', 'dst_host_serror_rate', 
        'serror_rate', 'diff_srv_rate', 'dst_host_same_srv_rate', 
        'srv_serror_rate', 'dst_host_srv_serror_rate', 'dst_host_same_src_port_rate',
        'dst_host_diff_srv_rate', 'count', 'dst_bytes', 'dst_host_srv_diff_host_rate',
        'protocol_type', 'srv_count', 'dst_host_srv_count', 'service', 
        'dst_host_rerror_rate', 'dst_host_count'
    ]
    
    mock_packet = {'src_ip': '203.0.113.50', 'dst_ip': '192.168.1.1', 'protocol': 'TCP', 'length': 64}
    
    print("Simulating high-frequency packet ingestion stream...")
    start_test = time.perf_counter()
    packet_count = 0
    mitigation_latencies = []
    
    # Run a high-speed loop for 5 seconds to simulate an attack flood
    while time.perf_counter() - start_test < 5.0:
        packet_count += 1
        
        # Ingestion and extraction
        features = extractor.extract_packet_features(mock_packet)
        df = pd.DataFrame([features])[SELECTED_FEATURES]
        
        # Simulate a malicious packet hit every 500th packet to test mitigation speed
        if packet_count % 500 == 0:
            start_mitigation = time.perf_counter()
            
            # 1. Classify Threat
            prediction = model.predict(df.values)
            
            # 2. Trigger System Rule (pfctl or iptables)
            firewall.block_ip('203.0.113.50')
            
            end_mitigation = time.perf_counter()
            mitigation_latencies.append(end_mitigation - start_mitigation)
            
    end_test = time.perf_counter()
    total_time = end_test - start_test
    pps = packet_count / total_time
    
    print("\n=== SYSTEM THROUGHPUT RESULTS ===")
    print(f"Total Packets Ingested: {packet_count}")
    print(f"Sustained Throughput Rate: {pps:.2f} Packets Per Second (PPS)")
    print(f"Average Mitigation Block Latency: {sum(mitigation_latencies)/len(mitigation_latencies)*1000:.2f} ms")

if __name__ == "__main__":
    run_throughput_benchmark()