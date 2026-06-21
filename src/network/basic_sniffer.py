"""
Basic packet sniffer using Scapy for Watchdog.
This module demonstrates basic packet capture functionality.
"""

# Set scapy configuration before import to prevent route limit issues
from scapy.config import conf

conf.max_list_count = 50000  # Increase limit significantly to prevent route overflow

import os
import sys
import threading
import time

from scapy.all import IP, TCP, sniff

from src.utils.crypto_utils import get_crypto

# Import logging
from src.utils.logger import get_logger, get_user_message, log_exception

logger = get_logger("basic_sniffer")
crypto = get_crypto()


class BasicSniffer:
    """Basic network packet sniffer."""

    def __init__(self) -> None:
        self.is_running = False
        self.keep_running = True
        self.packet_count = 0
        self.captured_packets = []
        self.data_file = "packet_data.json"
        self.stop_signal_file = "stop_signal.txt"

        # Load existing packet count if file exists
        try:
            if crypto.file_exists(self.data_file):
                data = crypto.read_encrypted_file(self.data_file)
                self.packet_count = data.get("packet_count", 0)
                logger.info(f"Loaded existing packet count: {self.packet_count}")
        except Exception as e:
            log_exception(logger, "loading packet data", e)
            logger.warning("Could not load encrypted packet data, starting fresh")

    def packet_callback(self, packet) -> None:
        """Callback function for each captured packet."""
        try:
            if IP in packet:
                self.packet_count += 1

                # Extract basic packet information
                src_ip = packet[IP].src
                dst_ip = packet[IP].dst
                protocol = packet[IP].proto
                length = len(packet)

                # Extract ports if available
                src_port = packet.getfieldval("sport") if hasattr(packet, "sport") else 0
                dst_port = packet.getfieldval("dport") if hasattr(packet, "dport") else 0

                # Extract TCP flags if available
                flags = "S"  # Default
                if TCP in packet:
                    flags = str(packet[TCP].flags)  # Convert FlagValue to string for JSON serialization

                # Determine protocol name
                if protocol == 6:  # TCP
                    protocol_name = "TCP"
                elif protocol == 17:  # UDP
                    protocol_name = "UDP"
                else:
                    protocol_name = f"PROTO-{protocol}"

                # Store packet info with all fields needed for ML
                packet_info = {
                    "count": self.packet_count,
                    "src_ip": src_ip,
                    "dst_ip": dst_ip,
                    "protocol": protocol_name,
                    "length": length,
                    "src_port": src_port,
                    "dst_port": dst_port,
                    "flags": flags,
                    "timestamp": time.time(),
                }

                self.captured_packets.append(packet_info)

                # Write to shared file
                self.write_data()

                # Print packet info (for testing)
                print(f"Packet #{self.packet_count}: {src_ip} -> {dst_ip} [{protocol_name}]")
                logger.debug(
                    f"Captured packet #{self.packet_count}: {src_ip} -> {dst_ip} [{protocol_name}]"
                )
        except Exception as e:
            log_exception(logger, "packet callback", e)
            logger.error(f"Failed to process packet: {e}")

    def write_data(self) -> None:
        """Write packet data to shared file with encryption."""
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
        }

        try:
            crypto.write_encrypted_file(data, self.data_file)
        except PermissionError as e:
            log_exception(logger, "writing packet data", e, get_user_message("permission_denied"))
        except OSError as e:
            log_exception(logger, "writing packet data", e, "Failed to write packet data to file.")
        except Exception as e:
            log_exception(logger, "writing packet data", e)

    def monitor_stop_signal(self) -> None:
        """Monitor for stop signal file and stop sniffing when detected."""
        while True:
            if os.path.exists(self.stop_signal_file):
                print("Stop signal received. Stopping sniffer...")
                os.remove(self.stop_signal_file)
                self.keep_running = False
                self.stop_sniffing()
                break
            time.sleep(0.1)

    def start_sniffing(self, packet_count: int = 0, interface: str | None = None) -> None:
        """Start packet capture."""
        if self.is_running:
            logger.warning("Sniffer is already running!")
            print("Sniffer is already running!")
            return

        self.is_running = True
        # Don't reset packet_count - keep it continuous
        # self.packet_count = 0  # Removed this line
        # self.captured_packets = []  # Don't clear all packets, just manage size

        if packet_count > 0:
            print(
                f"Starting packet capture (capturing {packet_count} packets, total count: {self.packet_count})..."
            )
            logger.info(f"Starting packet capture for {packet_count} packets")
        else:
            print(f"Starting continuous packet capture (total count: {self.packet_count})...")
            logger.info("Starting continuous packet capture")
        self.write_data()

        try:
            # Start sniffing - if packet_count=0, run continuously
            sniff(
                prn=self.packet_callback,
                store=0,
                count=packet_count if packet_count > 0 else 0,  # 0 = continuous
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
            self.write_data()
            print(f"Packet capture completed. Total packets captured: {self.packet_count}.")
            logger.info(f"Packet capture completed. Total packets: {self.packet_count}")

    def stop_sniffing(self) -> None:
        """Stop packet capture."""
        self.is_running = False
        print("Stopping packet capture...")
        logger.info("Stopping packet capture")
        # Write stopped status to file
        self.write_data()
        print("Status updated to 'stopped'")

    def get_captured_packets(self) -> list:
        """Return list of captured packets."""
        return self.captured_packets.copy()

    def get_packet_count(self) -> int:
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
        print(
            f"  {packet['count']}: {packet['src_ip']} -> {packet['dst_ip']} [{packet['protocol']}]"
        )


if __name__ == "__main__":
    # Check if running with root privileges
    if os.geteuid() != 0:
        print(f"Error: {get_user_message('permission_denied')}")
        print("Run with: sudo python basic_sniffer.py")
        logger.error("Attempted to run without root privileges")
        sys.exit(1)

    sniffer = BasicSniffer()

    if len(sys.argv) > 1 and sys.argv[1] == "start":
        # Start stop signal monitor thread
        stop_monitor_thread = threading.Thread(target=sniffer.monitor_stop_signal, daemon=True)
        stop_monitor_thread.start()
        try:
            while sniffer.keep_running:
                if not sniffer.is_running:
                    sniffer.start_sniffing(packet_count=0)  # 0 = continuous

                time.sleep(0.5)  # Brief pause between captures

        except KeyboardInterrupt:
            print("\nStopping sniffer...")
            logger.info("Stopping sniffer via KeyboardInterrupt")
            sniffer.stop_sniffing()
    else:
        # Run single capture
        test_sniffer()
