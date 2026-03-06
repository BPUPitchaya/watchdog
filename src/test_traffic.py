"""
Test Traffic Generator for Watchdog Integration Testing
Generates simulated network traffic to test ML detection system.
"""

from scapy.all import send, IP, TCP, UDP, RandIP, RandShort
import time
import random

def send_normal_traffic(count=10):
    """Send normal-looking traffic."""
    print(f"Sending {count} normal packets...")
    for i in range(count):
        # DNS query
        send(IP(src="192.168.1.100", dst="8.8.8.8")/UDP(sport=RandShort(), dport=53), verbose=0)
        time.sleep(0.1)
        
        # HTTP request
        send(IP(src="192.168.1.100", dst="142.250.195.131")/TCP(sport=RandShort(), dport=80, flags="S"), verbose=0)
        time.sleep(0.1)

def send_attack_traffic(count=5):
    """Send traffic that might trigger attack detection."""
    print(f"Sending {count} potential attack packets...")
    for i in range(count):
        # SYN flood like - many SYN packets
        for j in range(20):  # Increased from 5 to 20
            send(IP(src=RandIP(), dst="192.168.1.100")/TCP(sport=RandShort(), dport=80, flags="S"), verbose=0)
            time.sleep(0.01)  # Faster sending
        
        # Unusual port scan like
        send(IP(src=RandIP(), dst="192.168.1.100")/TCP(sport=RandShort(), dport=random.randint(1, 1024), flags="S"), verbose=0)
        time.sleep(0.1)

def main():
    """Main test function."""
    print("Starting traffic simulation for Watchdog testing...")
    print("Run integrated_watchdog.py first, then this script.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            send_normal_traffic(5)
            time.sleep(2)
            send_attack_traffic(2)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nTraffic simulation stopped.")

if __name__ == "__main__":
    main()
