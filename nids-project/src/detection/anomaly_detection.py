import time
import math
from collections import defaultdict, deque
from utils.logger import setup_logger
from storage.models import save_alert

class AnomalyDetector:
    def __init__(self):
        self.logger = setup_logger('anomaly_detector')
        self.traffic_window = deque(maxlen=500)
        self.port_activity = defaultdict(lambda: deque(maxlen=200))
        self.ip_activity = defaultdict(lambda: deque(maxlen=200))
        self.protocol_counts = defaultdict(int)
        
        self.baselines = {
            'packets_per_second': 1000,
            'unique_ports_per_ip': 25,
            'connections_per_minute': 50
        }
        
        self.learning_period = 300
        self.start_time = time.time()
    
    def analyze_packet(self, packet, src_ip, dst_ip, protocol, sport, dport):
        current_time = time.time()
        
        self.traffic_window.append(current_time)
        self.port_activity[src_ip].append((dport, current_time))
        self.ip_activity[src_ip].append(current_time)
        self.protocol_counts[protocol] += 1
        
        if current_time - self.start_time > self.learning_period:
            self._update_baselines()
        
        self._check_traffic_spike()
        self._check_port_scan_behavior(src_ip)
        self._check_brute_force(src_ip, dport)
        self._check_protocol_anomalies()
        self._check_vertical_scan(src_ip, dport)
        self._check_horizontal_scan(src_ip, sport)
    
    def _update_baselines(self):
        recent_packets = [t for t in self.traffic_window if t > time.time() - 60]
        if len(recent_packets) > 10:
            self.baselines['packets_per_second'] = max(100, len(recent_packets) / 60.0)
    
    def _check_traffic_spike(self):
        if len(self.traffic_window) < 10:
            return
            
        recent_packets = [t for t in self.traffic_window if t > time.time() - 5]
        current_rate = len(recent_packets) / 5.0

        if current_rate > self.baselines['packets_per_second'] * 3:
            self.raise_alert(
                message=f"Traffic spike detected: {current_rate:.1f} packets/sec",
                category="Anomaly",
                src_ip="Multiple",
                meta={
                    "current_rate": current_rate,
                    "baseline": self.baselines['packets_per_second'],
                    "anomaly_type": "Traffic Spike",
                    "severity": "high"
                }
            )
    
    def _check_port_scan_behavior(self, src_ip):
        ports_data = self.port_activity[src_ip]
        if len(ports_data) < 5:
            return
            
        recent_ports = [port for port, timestamp in ports_data if timestamp > time.time() - 30]
        unique_ports = len(set(recent_ports))
        
        if unique_ports > self.baselines['unique_ports_per_ip']:
            self.raise_alert(
                message=f"Stealth port scan detected from {src_ip} - {unique_ports} ports in 30s",
                category="Port Scan",
                src_ip=src_ip,
                meta={
                    "unique_ports": unique_ports,
                    "time_window": 30,
                    "scan_type": "Stealth Scan",
                    "severity": "medium"
                }
            )
    
    def _check_brute_force(self, src_ip, dport):
        brute_force_ports = [22, 21, 23, 3389, 1433, 3306]
        
        if dport in brute_force_ports:
            recent_attempts = [t for t in self.ip_activity[src_ip] if t > time.time() - 60]
            
            if len(recent_attempts) > 15:
                self.raise_alert(
                    message=f"Brute force attempt on port {dport} from {src_ip} - {len(recent_attempts)} attempts",
                    category="Brute Force",
                    src_ip=src_ip,
                    meta={
                        "target_port": dport,
                        "attempts": len(recent_attempts),
                        "service": self._get_service_name(dport),
                        "severity": "high"
                    }
                )
    
    def _check_protocol_anomalies(self):
        total_packets = sum(self.protocol_counts.values())
        if total_packets > 100:
            tcp_count = self.protocol_counts.get('TCP', 0)
            udp_count = self.protocol_counts.get('UDP', 0)
            
            tcp_ratio = tcp_count / total_packets
            udp_ratio = udp_count / total_packets
            
            if udp_ratio > 0.8:
                self.raise_alert(
                    message=f"UDP flood detected - {udp_ratio:.1%} UDP traffic",
                    category="DDoS",
                    src_ip="Multiple",
                    meta={
                        "udp_ratio": udp_ratio,
                        "anomaly_type": "Protocol Distribution",
                        "severity": "medium"
                    }
                )
    
    def _check_vertical_scan(self, src_ip, dport):
        if dport < 1024:
            recent_scans = [port for port, ts in self.port_activity[src_ip] 
                          if port < 1024 and ts > time.time() - 60]
            if len(set(recent_scans)) > 10:
                self.raise_alert(
                    message=f"Vertical port scan from {src_ip} - targeting well-known ports",
                    category="Port Scan",
                    src_ip=src_ip,
                    meta={
                        "target_ports": len(set(recent_scans)),
                        "scan_type": "Vertical Scan",
                        "severity": "high"
                    }
                )
    
    def _check_horizontal_scan(self, src_ip, sport):
        if sport > 1024:
            recent_targets = [sport for sport, ts in self.port_activity[src_ip] 
                            if sport > 1024 and ts > time.time() - 60]
            if len(set(recent_targets)) > 20:
                self.raise_alert(
                    message=f"Horizontal port scan from {src_ip} - scanning multiple hosts",
                    category="Port Scan",
                    src_ip=src_ip,
                    meta={
                        "target_count": len(set(recent_targets)),
                        "scan_type": "Horizontal Scan",
                        "severity": "medium"
                    }
                )
    
    def _get_service_name(self, port):
        services = {
            22: "SSH", 21: "FTP", 23: "Telnet", 
            80: "HTTP", 443: "HTTPS", 3389: "RDP",
            1433: "MSSQL", 3306: "MySQL", 5432: "PostgreSQL"
        }
        return services.get(port, f"Port {port}")
    
    def raise_alert(self, message, category, src_ip, meta=None):
        self.logger.warning(f"ANOMALY: {category} - {message}")
        save_alert(message, category, src_ip, meta or {})