import platform
import time
from scapy.all import sniff, IP, TCP, UDP, ICMP, DNS, DNSQR, Raw
from scapy.interfaces import get_working_ifaces
from detection.rule_engine import RuleEngine
from detection.anomaly_detection import AnomalyDetector
from detection.ml_detector import MLDetector
from utils.logger import setup_logger

class PacketSniffer:
    def __init__(self):
        self.logger = setup_logger('packet_sniffer')
        self.rule_engine = RuleEngine()
        self.anomaly_detector = AnomalyDetector()
        self.ml_detector = MLDetector()
        self.running = False
        self.interface = self._detect_interface()
        self.packet_count = 0
        
    def _detect_interface(self):
        system = platform.system()
        
        if system == "Windows":
            for iface in get_working_ifaces():
                if "npcap" in iface.name.lower() or "ether" in iface.description.lower():
                    self.logger.info(f"Selected interface: {iface.name}")
                    return iface.name
            ifaces = get_working_ifaces()
            if ifaces:
                return ifaces[0].name
        else:
            preferred = ['eth0', 'en0', 'wlan0', 'ens33', 'enp0s3']
            for iface in get_working_ifaces():
                if iface.name in preferred:
                    self.logger.info(f"Selected interface: {iface.name}")
                    return iface.name
            ifaces = get_working_ifaces()
            if ifaces:
                return ifaces[0].name
        
        fallback = "Ethernet" if system == "Windows" else "eth0"
        self.logger.warning(f"Using fallback interface: {fallback}")
        return fallback
    
    def process_packet(self, packet):
        try:
            if not packet.haslayer(IP):
                return
                
            self.packet_count += 1
            if self.packet_count % 100 == 0:
                self.logger.info(f"Processed {self.packet_count} packets...")
                
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = "Unknown"
            payload = ""
            
            if packet.haslayer(TCP):
                protocol = "TCP"
                sport = packet[TCP].sport
                dport = packet[TCP].dport
                flags = str(packet[TCP].flags)
                if packet.haslayer(Raw):
                    payload = str(packet[Raw].load)
            elif packet.haslayer(UDP):
                protocol = "UDP"
                sport = packet[UDP].sport
                dport = packet[UDP].dport
                flags = ""
                if packet.haslayer(DNS):
                    protocol = "DNS"
            elif packet.haslayer(ICMP):
                protocol = "ICMP"
                sport = dport = 0
                flags = ""
            else:
                return
            
            self.rule_engine.check_packet(packet, src_ip, dst_ip, protocol, sport, dport, flags, payload)
            self.anomaly_detector.analyze_packet(packet, src_ip, dst_ip, protocol, sport, dport)
            self.ml_detector.analyze_packet(packet, src_ip, dst_ip, protocol, sport, dport, payload)
            
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
    
    def start_sniffing(self):
        self.running = True
        self.logger.info(f"Starting packet capture on interface: {self.interface}")
        
        try:
            sniff(
                iface=self.interface,
                prn=self.process_packet,
                store=0,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            self.logger.error(f"Sniffing error: {e}")
    
    def stop_sniffing(self):
        self.running = False
        self.logger.info("Stopping packet capture")