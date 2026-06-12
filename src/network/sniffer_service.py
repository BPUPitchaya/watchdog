"""
Network sniffer service that runs independently and writes to shared data file.
This allows the UI to run without root privileges while the sniffer runs with sudo.
"""

import json
import os
import threading
import time

import joblib
from scapy.all import IP, TCP, UDP, sniff

from src.ml.feature_extractor import FeatureExtractor

# Import logging
from src.utils.logger import get_logger, get_user_message, log_exception
from src.utils.crypto_utils import get_crypto

logger = get_logger("sniffer_service")
crypto = get_crypto()


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
            if crypto.file_exists(self.data_file):
                data = crypto.read_encrypted_file(self.data_file)
                self.packet_count = data.get("packet_count", 0)
                logger.info(f"Loaded existing packet count: {self.packet_count}")
        except Exception as e:
            log_exception(logger, "loading packet data", e)
            logger.warning("Could not load encrypted packet data, starting fresh")

    def packet_callback(self, packet):
        """Callback function for each captured packet."""
        try:
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
                    flags = "N"
            elif protocol == 17:  # UDP
                protocol_name = "udp"
                if UDP in packet:
                    src_port = packet[UDP].sport
                    dst_port = packet[UDP].dport
                else:
                    src_port = 0
                    dst_port = 0
                flags = "N"
            else:
                protocol_name = f"proto_{protocol}"
                src_port = 0
                dst_port = 0
                flags = "N"

            # Create packet data for feature extraction
            packet_data = {
                "src_ip": src_ip,
                "dst_ip": dst_ip,
                "protocol": protocol,
                "length": length,
                "src_port": src_port,
                "dst_port": dst_port,
                "flags": flags,
                "direction": (
                    "outbound" if src_ip.startswith("192.168.") else "inbound"
                ),  # Simplified
            }

            # If ML is not available, store packet without prediction
            if self.model is None or self.extractor is None:
                packet_info = {
                    "count": self.packet_count,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "protocol": protocol_name,
                    "timestamp": time.time(),
                    "prediction": "unavailable",
                    "is_attack": False,
                }
                self.captured_packets.append(packet_info)
                print(
                    f"✓ Traffic (no ML): {src_ip}:{src_port} -> {dst_ip}:{dst_port} [{protocol_name}]"
                )
            else:
                # Add to buffer for batch processing
                self.packet_buffer.append(
                    {
                        "packet_data": packet_data,
                        "src_ip": src_ip,
                        "dst_ip": dst_ip,
                        "protocol_name": protocol_name,
                        "src_port": src_port,
                        "dst_port": dst_port,
                        "count": self.packet_count,
                        "timestamp": time.time(),
                    }
                )

                # Process batch if buffer is full
                if len(self.packet_buffer) >= self.batch_size:
                    self.process_batch()

            # Write to file periodically
            current_time = time.time()
            if current_time - self.last_write_time >= self.write_interval:
                self.write_data()
                self.last_write_time = current_time
        except Exception as e:
            log_exception(logger, "packet callback", e)
            logger.error(f"Failed to process packet: {e}")

    def process_batch(self):
        """Process buffered packets in batch for ML inference."""
        if not self.packet_buffer:
            return

        try:
            # Extract features for all packets in buffer
            features_list = []
            feature_names = None
            for packet in self.packet_buffer:
                features = self.extractor.extract_packet_features(packet["packet_data"])
                selected_features, names = self.extractor.get_selected_features(features)
                if feature_names is None:
                    feature_names = names
                features_list.append(selected_features)

            # Convert to DataFrame with feature names for batch prediction
            import pandas as pd

            features_df = pd.DataFrame(features_list, columns=feature_names)

            # Batch prediction
            predictions = self.model.predict(features_df)
            label_map = {0: "normal", 1: "attack"}

            # Process results and store packet info
            for i, packet in enumerate(self.packet_buffer):
                prediction = predictions[i]
                predicted_label = label_map.get(prediction, "unknown")

                packet_info = {
                    "count": packet["count"],
                    "src_ip": packet["src_ip"],
                    "dst_ip": packet["dst_ip"],
                    "protocol": packet["protocol_name"],
                    "timestamp": packet["timestamp"],
                    "prediction": predicted_label,
                    "is_attack": prediction == 1,
                }

                self.captured_packets.append(packet_info)

                # Print packet info and alerts
                if prediction == 1:
                    print(
                        f"⚠️  POTENTIAL ATTACK DETECTED: {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']} [{packet['protocol_name']}] - Predicted: {predicted_label}"
                    )
                    logger.warning(
                        f"Attack detected: {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']} [{packet['protocol_name']}]"
                    )
                else:
                    print(
                        f"✓ Normal traffic: {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']} [{packet['protocol_name']}]"
                    )
                    logger.debug(
                        f"Normal traffic: {packet['src_ip']}:{packet['src_port']} -> {packet['dst_ip']}:{packet['dst_port']} [{packet['protocol_name']}]"
                    )

        except Exception as e:
            log_exception(logger, "batch prediction", e, get_user_message("ml_prediction_failed"))
            print(f"Error in batch prediction: {e}")
            # Fallback: process packets as normal (no prediction)
            for packet in self.packet_buffer:
                packet_info = {
                    "count": packet["count"],
                    "src_ip": packet["src_ip"],
                    "dst_ip": packet["dst_ip"],
                    "protocol": packet["protocol_name"],
                    "timestamp": packet["timestamp"],
                    "prediction": "error",
                    "is_attack": False,
                }
                self.captured_packets.append(packet_info)

        # Clear buffer
        self.packet_buffer = []

    def write_data(self):
        """Write packet data to shared file."""
        # Keep only the last 100 packets in memory to avoid memory issues
        packets_to_save = (
            self.captured_packets[-100:]
            if len(self.captured_packets) > 100
            else self.captured_packets
        )

        data = {
            "status": "running" if self.is_running else "stopped",
            "packet_count": self.packet_count,
            "packets": packets_to_save,
            "alerts": [p for p in packets_to_save if p.get("is_attack", False)],
        }

        try:
            crypto.write_encrypted_file(data, self.data_file)
        except PermissionError as e:
            log_exception(logger, "writing packet data", e, get_user_message("permission_denied"))
        except OSError as e:
            log_exception(logger, "writing packet data", e, "Failed to write packet data to file.")
        except Exception as e:
            log_exception(logger, "writing packet data", e)

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
            logger.warning("Sniffer is already running!")
            print("Sniffer is already running!")
            return

        self.is_running = True
        # Don't reset packet_count - keep it continuous
        # self.packet_count = 0  # Removed this line
        # self.captured_packets = []  # Don't clear all packets, just manage size

        # Load ML components if not loaded
        if self.model is None:
            try:
                self.model = joblib.load("models/random_forest_model.pkl")
                self.extractor = FeatureExtractor()
                print("ML model and feature extractor loaded successfully.")
                logger.info("ML model and feature extractor loaded successfully")
            except FileNotFoundError:
                log_exception(
                    logger,
                    "loading ML model",
                    FileNotFoundError("Model file not found"),
                    get_user_message("ml_model_not_found"),
                )
                print(f"ERROR: {get_user_message('ml_model_not_found')}")
                self.model = None
                self.extractor = None
            except Exception as e:
                log_exception(
                    logger, "loading ML components", e, get_user_message("ml_prediction_failed")
                )
                print(f"ERROR: {get_user_message('ml_prediction_failed')}")
                self.model = None
                self.extractor = None

        print(
            f"Starting packet capture (capturing {packet_count} packets, total count: {self.packet_count})..."
        )
        logger.info(f"Starting packet capture for {packet_count} packets")
        self.write_data()

        try:
            # Start sniffing
            sniff(
                prn=self.packet_callback,
                store=0,
                count=packet_count,
                iface=interface,
                stop_filter=lambda x: not self.is_running,  # Check for stop signal
            )
        except KeyboardInterrupt:
            print("\nPacket capture stopped by user.")
            logger.info("Packet capture stopped by user (KeyboardInterrupt)")
        except PermissionError as e:
            log_exception(logger, "packet capture", e, get_user_message("permission_denied"))
            print(f"\n{get_user_message('permission_denied')}")
        except OSError as e:
            if "Operation not permitted" in str(e) or "Permission denied" in str(e):
                log_exception(logger, "packet capture", e, get_user_message("permission_denied"))
                print(f"\n{get_user_message('permission_denied')}")
            else:
                log_exception(logger, "packet capture", e, get_user_message("network_interface"))
                print(f"\n{get_user_message('network_interface')}")
        except Exception as e:
            log_exception(logger, "packet capture", e, get_user_message("packet_capture_failed"))
            print(f"\n{get_user_message('packet_capture_failed')}")
        finally:
            self.is_running = False
            # Process any remaining packets
            if self.packet_buffer:
                print(f"Processing {len(self.packet_buffer)} remaining packets...")
                logger.info(f"Processing {len(self.packet_buffer)} remaining packets")
                self.process_batch()
            self.write_data()
            print(f"Packet capture completed. Total packets captured: {self.packet_count}.")
            logger.info(f"Packet capture completed. Total packets: {self.packet_count}")

    def stop_sniffing(self):
        """Stop packet capture."""
        self.is_running = False
        print("Stopping packet capture...")
        logger.info("Stopping packet capture")

        # Process any remaining packets in buffer
        if self.packet_buffer:
            print(f"Processing {len(self.packet_buffer)} remaining packets in buffer...")
            logger.info(f"Processing {len(self.packet_buffer)} remaining packets in buffer")
            self.process_batch()

        # Write stopped status to file
        self.write_data()
        print("Status updated to 'stopped'")


def main():
    """Main entry point for the sniffer service."""
    import sys

    # Check if running with root privileges
    if os.geteuid() != 0:
        print(f"Error: {get_user_message('permission_denied')}")
        print("Run with: sudo python sniffer_service.py")
        logger.error("Attempted to run without root privileges")
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
            logger.info("Stopping sniffer service via KeyboardInterrupt")
            service.stop_sniffing()
    else:
        # Run single capture
        service.start_sniffing(packet_count=50)


if __name__ == "__main__":
    main()
