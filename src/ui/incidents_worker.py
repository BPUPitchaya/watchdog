import sys
from PyQt6.QtCore import QThread, pyqtSignal
import numpy as np

class IncidentsWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, packets, model, extractor, layout_only):
        super().__init__()
        self.packets = packets
        self.model = model
        self.extractor = extractor
        self.layout_only = layout_only

    def run(self):
        flagged_packets = []
        for packet in self.packets:
            if not self.layout_only and self.model and self.extractor:
                packet_data = {
                    'src_ip': packet.get('src_ip', '192.168.1.1'),
                    'dst_ip': packet.get('dst_ip', '10.0.0.1'),
                    'protocol': 6 if packet.get('protocol', 'TCP').upper() == 'TCP' else 17,
                    'length': packet.get('length', 100),
                    'src_port': packet.get('src_port', 12345),
                    'dst_port': packet.get('dst_port', 80),
                    'flags': packet.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features, feature_names = self.extractor.get_selected_features(features)
                import pandas as pd
                features_df = pd.DataFrame([selected_features], columns=feature_names)
                prediction = self.model.predict(features_df)[0]
                probabilities = self.model.predict_proba(features_df)[0]
                confidence = max(probabilities) * 100
                
                # Flag if ATTACK prediction OR low confidence (< 60%)
                if confidence < 60.0:
                    # Enrich packet with AI results
                    packet['ai_confidence'] = f"{confidence:.1f}%"
                    packet['ai_threat'] = "ATTACK" if prediction == 1 else "NORMAL"
                    flagged_packets.append(packet)
        
        self.finished.emit(flagged_packets)
