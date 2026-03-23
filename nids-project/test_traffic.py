#!/usr/bin/env python3
"""
Test traffic generator for NIDS testing
WARNING: Only run on your own network or test environment!
"""

import os
import sys
import time
import socket
import threading
from scapy.all import *
from scapy.layers.inet import IP, TCP, UDP, ICMP

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.logger import setup_logger

logger = setup_logger('test_traffic')

class TrafficGenerator:
    def __init__(self, target_ip=None):
        self.target_ip = target_ip or self.get_local_ip()
        logger.info(f"Target IP for testing: {self.target_ip}")
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def generate_port_scan(self, ports_to_scan=20):
        """Generate port scan traffic"""
        logger.info(f"🚀 Generating port scan on {self.target_ip} (ports: {ports_to_scan})")
        
        # Scan common ports
        common_ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389]
        
        for port in common_ports[:ports_to_scan]:
            try:
                # Send SYN packet
                ip = IP(dst=self.target_ip)
                tcp = TCP(dport=port, flags="S")
                send(ip/tcp, verbose=0)
                time.sleep(0.1)  # Small delay between packets
                
            except Exception as e:
                logger.error(f"Port scan error: {e}")
    
    def generate_syn_flood(self, duration=5, packet_rate=10):
        """Generate SYN flood traffic (limited for testing)"""
        logger.info(f"🌊 Generating SYN flood on {self.target_ip} for {duration}s")
        
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            try:
                # Generate random source IP and port
                src_ip = f"10.0.0.{random.randint(1, 254)}"
                src_port = random.randint(1024, 65535)
                
                ip = IP(src=src_ip, dst=self.target_ip)
                tcp = TCP(sport=src_port, dport=80, flags="S")
                send(ip/tcp, verbose=0)
                
                packet_count += 1
                time.sleep(1.0 / packet_rate)  # Control packet rate
                
            except Exception as e:
                logger.error(f"SYN flood error: {e}")
        
        logger.info(f"SYN flood completed: {packet_count} packets sent")
    
    def generate_brute_force(self, target_port=22, attempts=10):
        """Generate brute force pattern traffic"""
        logger.info(f"🔑 Generating brute force pattern on port {target_port}")
        
        for i in range(attempts):
            try:
                src_ip = f"192.168.1.{random.randint(100, 200)}"
                
                ip = IP(src=src_ip, dst=self.target_ip)
                
                if target_port == 53:
                    # DNS brute force
                    udp = UDP(sport=random.randint(1024, 65535), dport=53)
                    send(ip/udp, verbose=0)
                else:
                    # TCP brute force (SSH, FTP, etc.)
                    tcp = TCP(sport=random.randint(1024, 65535), dport=target_port, flags="S")
                    send(ip/tcp, verbose=0)
                
                time.sleep(0.5)  # Simulate brute force timing
                
            except Exception as e:
                logger.error(f"Brute force error: {e}")
    
    def generate_icmp_flood(self, duration=3):
        """Generate ICMP flood traffic"""
        logger.info(f"📡 Generating ICMP flood on {self.target_ip}")
        
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            try:
                ip = IP(dst=self.target_ip)
                icmp = ICMP()
                send(ip/icmp, verbose=0)
                
                packet_count += 1
                time.sleep(0.1)  # Limit rate
                
            except Exception as e:
                logger.error(f"ICMP flood error: {e}")
        
        logger.info(f"ICMP flood completed: {packet_count} packets sent")
    
    def generate_mixed_attack(self):
        """Generate mixed attack patterns"""
        logger.info("🎭 Generating mixed attack patterns")
        
        # Run different attacks in threads
        threads = []
        
        # Port scan
        threads.append(threading.Thread(target=self.generate_port_scan, args=(10,)))
        
        # Brute force attempts
        threads.append(threading.Thread(target=self.generate_brute_force, args=(22, 5)))  # SSH
        threads.append(threading.Thread(target=self.generate_brute_force, args=(21, 5)))  # FTP
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        logger.info("Mixed attack generation completed")

def main():
    print("NIDS Test Traffic Generator")
    print("=" * 40)
    print("WARNING: Only run on your own network!")
    print("This will generate simulated attack traffic.")
    print("=" * 40)
    
    # Get target IP
    target_ip = input(f"Enter target IP [default: auto-detect]: ").strip()
    if not target_ip:
        target_ip = None
    
    generator = TrafficGenerator(target_ip)
    
    print("\nAvailable tests:")
    print("1. Port Scan")
    print("2. SYN Flood (limited)")
    print("3. SSH Brute Force") 
    print("4. FTP Brute Force")
    print("5. ICMP Flood")
    print("6. Mixed Attacks")
    print("7. All Tests")
    
    try:
        choice = input("\nSelect test (1-7): ").strip()
        
        if choice == "1":
            generator.generate_port_scan()
        elif choice == "2":
            generator.generate_syn_flood()
        elif choice == "3":
            generator.generate_brute_force(22, 8)
        elif choice == "4":
            generator.generate_brute_force(21, 8)
        elif choice == "5":
            generator.generate_icmp_flood()
        elif choice == "6":
            generator.generate_mixed_attack()
        elif choice == "7":
            print("Running all tests...")
            generator.generate_port_scan()
            time.sleep(2)
            generator.generate_syn_flood()
            time.sleep(2)
            generator.generate_brute_force(22, 6)
            generator.generate_brute_force(21, 6)
            time.sleep(2)
            generator.generate_icmp_flood()
        else:
            print("Invalid choice")
            return
        
        print(f"\n✅ Test traffic generation completed!")
        print("📊 Check the NIDS dashboard for detected alerts")
        
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Check if running as root (required for packet injection on Linux)
    if os.name != 'nt' and os.geteuid() != 0:
        print("⚠️  Note: Some tests may require root privileges on Linux")
        print("   Run with: sudo python test_traffic.py")
        print()
    
    main()