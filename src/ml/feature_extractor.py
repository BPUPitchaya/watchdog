"""
Real-time Feature Extractor for NSL-KDD
Extracts selected features from captured packets in real-time.
Maintains connection state for accurate feature computation.
"""

import time
from collections import defaultdict, deque
import numpy as np

class FeatureExtractor:
    """Extracts NSL-KDD features from packets in real-time."""
    
    def __init__(self, window_size=100, time_window=2.0):
        """
        Initialize the feature extractor.
        
        Args:
            window_size: Maximum number of recent connections to track
            time_window: Time window in seconds for rate calculations
        """
        self.window_size = window_size
        self.time_window = time_window
        
        # Connection tracking: key = (src_ip, dst_ip, protocol)
        self.connections = {}
        
        # Global packet history for host-based features
        self.global_packets = deque(maxlen=1000)  # Keep last 1000 packets
        
        # Service mapping (simplified)
        self.service_map = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
            80: 'http', 110: 'pop3', 143: 'imap', 443: 'https', 993: 'imaps'
        }
        
        # Flag mapping
        self.flag_map = {
            'F': 1, 'S': 2, 'R': 3, 'P': 4, 'A': 5, 'U': 6, 'C': 7, 'E': 8, 'N': 9, 'O': 10
        }
    
    def extract_packet_features(self, packet_data):
        """
        Extract features from a single packet.
        
        Args:
            packet_data: Dict with packet information (src_ip, dst_ip, protocol, etc.)
        
        Returns:
            dict: Extracted features for the packet's connection
        """
        # Update global packet history
        packet_data['timestamp'] = time.time()
        self.global_packets.append(packet_data)
        
        # Get connection key
        src_ip = packet_data.get('src_ip')
        dst_ip = packet_data.get('dst_ip')
        protocol = packet_data.get('protocol', 6)  # Default TCP
        
        conn_key = (src_ip, dst_ip, protocol)
        
        # Initialize connection if new
        if conn_key not in self.connections:
            self.connections[conn_key] = {
                'start_time': time.time(),
                'packets': [],
                'src_bytes': 0,
                'dst_bytes': 0,
                'count': 0,
                'srv_count': 0,
                'serror_count': 0,
                'rerror_count': 0,
                'same_srv_count': 0,
                'diff_srv_count': 0
            }
        
        conn = self.connections[conn_key]
        
        # Update connection stats
        conn['packets'].append(packet_data)
        conn['count'] += 1
        
        # Determine direction and update bytes
        if packet_data.get('direction') == 'outbound':
            conn['src_bytes'] += packet_data.get('length', 0)
        else:
            conn['dst_bytes'] += packet_data.get('length', 0)
        
        # Update error counts (simplified)
        if packet_data.get('flags', '').find('R') >= 0:
            conn['rerror_count'] += 1
        elif packet_data.get('flags', '').find('S') >= 0:
            conn['serror_count'] += 1
        
        # Service detection
        dst_port = packet_data.get('dst_port', 0)
        service = self.service_map.get(dst_port, 'other')
        
        # Flag encoding
        flags = packet_data.get('flags', 'N')
        flag_encoded = self.flag_map.get(flags[0] if flags else 'N', 9)
        
        # Protocol encoding
        protocol_encoded = 1 if protocol == 6 else (2 if protocol == 17 else 0)
        
        # Compute features
        features = {}
        
        # Basic features
        features['src_bytes'] = conn['src_bytes']
        features['dst_bytes'] = conn['dst_bytes']
        features['count'] = conn['count']
        features['protocol_type'] = protocol_encoded
        features['service'] = hash(service) % 70  # Simplified encoding
        features['flag'] = flag_encoded
        
        # Rate features (simplified)
        current_time = time.time()
        time_diff = current_time - conn['start_time']
        
        if time_diff > 0:
            features['serror_rate'] = conn['serror_count'] / time_diff
            features['srv_serror_rate'] = conn['serror_count'] / time_diff  # Simplified
            features['rerror_rate'] = conn['rerror_count'] / time_diff
            features['same_srv_rate'] = conn['same_srv_count'] / conn['count'] if conn['count'] > 0 else 0
            features['diff_srv_rate'] = conn['diff_srv_count'] / conn['count'] if conn['count'] > 0 else 0
            features['srv_count'] = conn['count']  # Simplified
        else:
            features['serror_rate'] = 0
            features['srv_serror_rate'] = 0
            features['rerror_rate'] = 0
            features['same_srv_rate'] = 0
            features['diff_srv_rate'] = 0
            features['srv_count'] = 0
        
        # Host-based features (simplified)
        # Count connections to same destination
        dst_host_count = sum(1 for p in self.global_packets 
                           if p.get('dst_ip') == dst_ip and 
                           current_time - p.get('timestamp', 0) < self.time_window)
        features['dst_host_count'] = min(dst_host_count, 255)
        
        # Other host features (simplified approximations)
        features['dst_host_srv_count'] = features['dst_host_count']  # Simplified
        features['dst_host_same_srv_rate'] = 1.0 if features['dst_host_count'] > 0 else 0
        features['dst_host_diff_srv_rate'] = 0.0
        features['dst_host_same_src_port_rate'] = 0.0
        features['dst_host_srv_diff_host_rate'] = 0.0
        features['dst_host_serror_rate'] = features['serror_rate']
        features['dst_host_srv_serror_rate'] = features['srv_serror_rate']
        features['dst_host_rerror_rate'] = features['rerror_rate']
        
        # Clean up old connections
        self._cleanup_old_connections()
        
        return features
    
    def _cleanup_old_connections(self):
        """Remove old connections to prevent memory issues."""
        current_time = time.time()
        to_remove = []
        
        for conn_key, conn in self.connections.items():
            if current_time - conn['start_time'] > self.time_window * 10:  # Keep for 10 windows
                to_remove.append(conn_key)
        
        for key in to_remove:
            del self.connections[key]
        
        # Keep only recent global packets
        cutoff_time = current_time - self.time_window * 2
        while self.global_packets and self.global_packets[0]['timestamp'] < cutoff_time:
            self.global_packets.popleft()
    
    def get_selected_features(self, features_dict):
        """Extract only the selected features for model input."""
        selected = [
            'src_bytes', 'same_srv_rate', 'flag', 'dst_host_serror_rate', 
            'serror_rate', 'diff_srv_rate', 'dst_host_same_srv_rate', 
            'srv_serror_rate', 'dst_host_srv_serror_rate', 'dst_host_same_src_port_rate',
            'dst_host_diff_srv_rate', 'count', 'dst_bytes', 'dst_host_srv_diff_host_rate',
            'protocol_type', 'srv_count', 'dst_host_srv_count', 'service', 
            'dst_host_rerror_rate', 'dst_host_count'
        ]
        
        return [features_dict.get(feat, 0) for feat in selected], selected


# Example usage
if __name__ == "__main__":
    extractor = FeatureExtractor()
    
    # Example packet
    packet = {
        'src_ip': '192.168.1.1',
        'dst_ip': '10.0.0.1',
        'protocol': 6,
        'length': 100,
        'flags': 'S',
        'dst_port': 80,
        'direction': 'outbound'
    }
    
    features = extractor.extract_packet_features(packet)
    selected = extractor.get_selected_features(features)
    
    print("Extracted features:", len(features))
    print("Selected features for model:", len(selected))
    print("Sample selected features:", selected[:5])
