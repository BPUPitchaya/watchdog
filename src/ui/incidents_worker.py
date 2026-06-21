from PyQt6.QtCore import QThread, pyqtSignal


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
                    "src_ip": packet.get("src_ip", "192.168.1.1"),
                    "dst_ip": packet.get("dst_ip", "10.0.0.1"),
                    "protocol": 6 if packet.get("protocol", "TCP").upper() == "TCP" else 17,
                    "length": packet.get("length", 100),
                    "src_port": packet.get("src_port", 12345),
                    "dst_port": packet.get("dst_port", 80),
                    "flags": packet.get("flags", "S"),
                    "direction": "inbound",
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features, feature_names = self.extractor.get_selected_features(features)
                import numpy as np

                # Use numpy array without feature names to avoid sklearn warning
                features_array = np.array([selected_features])
                prediction = self.model.predict(features_array)[0]
                probabilities = self.model.predict_proba(features_array)[0]
                confidence = max(probabilities) * 100

                # Always enrich packet with AI results (even if not flagged)
                packet["ai_confidence"] = f"{confidence:.1f}%"
                packet["ai_threat"] = "ATTACK" if prediction == 1 else "Safe"

                # Flag if ATTACK prediction OR low confidence (< 60%)
                if confidence < 60.0 or prediction == 1:
                    flagged_packets.append(packet)
            else:
                # Layout-only mode or no model: set default values
                packet["ai_confidence"] = "N/A"
                packet["ai_threat"] = "UNKNOWN"

        self.finished.emit(flagged_packets)
