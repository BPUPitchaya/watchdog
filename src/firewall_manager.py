"""
Firewall Manager for Watchdog
Automates IP blocking using pfctl on macOS with safety mechanisms.
"""

import subprocess
import threading
import time
import os

class FirewallManager:
    """Manages firewall rules for IP blocking."""
    
    def __init__(self, table_name="watchdog_blocked"):
        self.table_name = table_name
        self.whitelist = {
            "8.8.8.8",      # Google DNS
            "8.8.4.4",      # Google DNS
            "1.1.1.1",      # Cloudflare DNS
            "1.0.0.1",      # Cloudflare DNS
            "208.67.222.222",  # OpenDNS
            "208.67.220.220",  # OpenDNS
            "192.168.1.1",  # Common gateway
            "127.0.0.1",    # Localhost
            "0.0.0.0",      # Invalid
        }
        self.blocked_ips = set()
        self.timers = {}  # ip -> timer
        
        # Ensure table exists
        self._create_table()
    
    def _create_table(self):
        """Create the pf table if it doesn't exist."""
        try:
            # Check if table exists
            result = subprocess.run(
                ["sudo", "pfctl", "-t", self.table_name, "-T", "show"],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                # Create table
                subprocess.run(
                    ["sudo", "pfctl", "-t", self.table_name, "-T", "create"],
                    check=True
                )
        except subprocess.CalledProcessError:
            print(f"Warning: Could not create pf table {self.table_name}")
    
    def _run_pfctl(self, args):
        """Run pfctl with sudo."""
        cmd = ["sudo", "pfctl"] + args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"pfctl error: {e}")
            print(f"stderr: {e.stderr}")
            return None
    
    def block_ip(self, ip, timeout=None):
        """Block an IP address."""
        if not self._is_valid_ip(ip):
            print(f"Invalid IP: {ip}")
            return False
        
        if ip in self.whitelist:
            print(f"IP {ip} is whitelisted, not blocking")
            return False
        
        if ip in self.blocked_ips:
            print(f"IP {ip} already blocked")
            return True
        
        # Add to pf table
        result = self._run_pfctl(["-t", self.table_name, "-T", "add", ip])
        if result is not None:
            self.blocked_ips.add(ip)
            print(f"Blocked IP: {ip}")
            
            # Set timeout if specified
            if timeout:
                timer = threading.Timer(timeout, self.unblock_ip, args=[ip])
                timer.start()
                self.timers[ip] = timer
                print(f"Block timeout set for {ip}: {timeout} seconds")
            
            return True
        return False
    
    def unblock_ip(self, ip):
        """Unblock an IP address."""
        if ip not in self.blocked_ips:
            print(f"IP {ip} not blocked")
            return False
        
        # Remove from pf table
        result = self._run_pfctl(["-t", self.table_name, "-T", "delete", ip])
        if result is not None:
            self.blocked_ips.discard(ip)
            print(f"Unblocked IP: {ip}")
            
            # Cancel timer if exists
            if ip in self.timers:
                self.timers[ip].cancel()
                del self.timers[ip]
            
            return True
        return False
    
    def get_blocked_ips(self):
        """Get list of currently blocked IPs."""
        result = self._run_pfctl(["-t", self.table_name, "-T", "show"])
        if result:
            return result.split('\n')
        return []
    
    def _is_valid_ip(self, ip):
        """Basic IP validation."""
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False
        return True
    
    def add_to_whitelist(self, ip):
        """Add IP to whitelist."""
        self.whitelist.add(ip)
        print(f"Added {ip} to whitelist")
    
    def remove_from_whitelist(self, ip):
        """Remove IP from whitelist."""
        self.whitelist.discard(ip)
        print(f"Removed {ip} from whitelist")

def main():
    """Test the firewall manager."""
    fm = FirewallManager()
    
    print("Blocked IPs:", fm.get_blocked_ips())
    
    # Test blocking
    test_ip = "192.0.2.1"  # Test IP
    fm.block_ip(test_ip, timeout=30)
    
    print("Blocked IPs after:", fm.get_blocked_ips())
    
    time.sleep(35)  # Wait for timeout
    
    print("Blocked IPs after timeout:", fm.get_blocked_ips())

if __name__ == "__main__":
    main()
