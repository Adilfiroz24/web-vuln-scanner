import json
import os
import re
import time
from utils.logger import setup_logger
from storage.models import save_alert

class RuleEngine:
    def __init__(self):
        self.logger = setup_logger('rule_engine')
        self.signatures = self.load_signatures()
        self.port_scan_tracker = {}
        self.syn_flood_tracker = {}
        self.http_attack_patterns = [
            r"union.*select", r"select.*from", r"insert.*into", 
            r"drop.*table", r"1=1", r"or.*1=1", r"script>", 
            r"<script", r"eval\(", r"base64_decode", r"cmd\.exe",
            r"bin/bash", r"etc/passwd", r"../..", r"\.\./"
        ]
        
    def load_signatures(self):
        try:
            rules_path = os.path.join(os.path.dirname(__file__), '..', '..', 'signature_rules.json')
            with open(rules_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading signatures: {e}")
            return {"rules": []}
    
    def check_packet(self, packet, src_ip, dst_ip, protocol, sport, dport, flags, payload):
        for rule in self.signatures.get("rules", []):
            if self._matches_rule(packet, rule, src_ip, dst_ip, protocol, sport, dport, flags, payload):
                self.raise_alert(
                    message=rule["description"],
                    category=rule["category"],
                    src_ip=src_ip,
                    meta={
                        "rule_id": rule["id"],
                        "protocol": protocol,
                        "source_port": sport,
                        "dest_port": dport,
                        "severity": rule["severity"]
                    }
                )
        
        self._detect_port_scan(src_ip, dport, flags)
        self._detect_syn_flood(src_ip)
        self._detect_http_attacks(payload, src_ip, dport)
        self._detect_dns_tunneling(packet, src_ip)
        self._detect_null_scan(flags, src_ip)
        self._detect_xmas_scan(flags, src_ip)
    
    def _matches_rule(self, packet, rule, src_ip, dst_ip, protocol, sport, dport, flags, payload):
        try:
            if rule.get("protocol") and rule["protocol"] != protocol:
                return False
            
            if rule.get("dst_port") and rule["dst_port"] != dport:
                return False
                
            if rule.get("src_ip") and rule["src_ip"] != src_ip:
                return False
                
            if rule.get("flags") and protocol == "TCP":
                if rule["flags"] not in flags:
                    return False
            
            if rule.get("content") and payload:
                if rule["content"].lower() in payload.lower():
                    return True
                else:
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Rule matching error: {e}")
            return False
    
    def _detect_port_scan(self, src_ip, dport, flags):
        if src_ip not in self.port_scan_tracker:
            self.port_scan_tracker[src_ip] = {
                'ports': set(),
                'syn_count': 0,
                'start_time': time.time()
            }
        
        tracker = self.port_scan_tracker[src_ip]
        tracker['ports'].add(dport)
        
        if flags == "S":
            tracker['syn_count'] += 1
        
        unique_ports = len(tracker['ports'])
        
        if unique_ports > 15 and tracker['syn_count'] > 10:
            self.raise_alert(
                message=f"Advanced port scan detected from {src_ip} - {unique_ports} unique ports",
                category="Port Scan",
                src_ip=src_ip,
                meta={
                    "unique_ports": unique_ports,
                    "syn_count": tracker['syn_count'],
                    "scan_type": "SYN Scan",
                    "severity": "high"
                }
            )
            self.port_scan_tracker[src_ip] = {'ports': set(), 'syn_count': 0, 'start_time': time.time()}
    
    def _detect_syn_flood(self, src_ip):
        current_time = time.time()
        
        if src_ip not in self.syn_flood_tracker:
            self.syn_flood_tracker[src_ip] = {
                'count': 0,
                'start_time': current_time
            }
        
        tracker = self.syn_flood_tracker[src_ip]
        tracker['count'] += 1
        
        if current_time - tracker['start_time'] > 10:
            if tracker['count'] > 100:
                self.raise_alert(
                    message=f"SYN Flood attack from {src_ip} - {tracker['count']} SYN packets in 10 seconds",
                    category="DDoS",
                    src_ip=src_ip,
                    meta={
                        "packet_count": tracker['count'],
                        "duration": 10,
                        "attack_type": "SYN Flood",
                        "severity": "critical"
                    }
                )
            self.syn_flood_tracker[src_ip] = {'count': 0, 'start_time': current_time}
    
    def _detect_http_attacks(self, payload, src_ip, dport):
        if dport in [80, 443, 8080] and payload:
            for pattern in self.http_attack_patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    self.raise_alert(
                        message=f"Web attack detected from {src_ip} - {pattern}",
                        category="Web Attack",
                        src_ip=src_ip,
                        meta={
                            "pattern": pattern,
                            "target_port": dport,
                            "attack_type": "Injection",
                            "severity": "high"
                        }
                    )
                    break
    
    def _detect_dns_tunneling(self, packet, src_ip):
        from scapy.all import DNS, DNSQR
        
        if packet.haslayer(DNS) and packet[DNS].qr == 0:
            if packet.haslayer(DNSQR):
                dns_query = packet[DNSQR].qname.decode() if packet[DNSQR].qname else ""
                if len(dns_query) > 100:
                    self.raise_alert(
                        message=f"DNS tunneling suspected from {src_ip} - long query: {dns_query[:50]}...",
                        category="Data Exfiltration",
                        src_ip=src_ip,
                        meta={
                            "query_length": len(dns_query),
                            "query_sample": dns_query[:50],
                            "attack_type": "DNS Tunneling",
                            "severity": "medium"
                        }
                    )
    
    def _detect_null_scan(self, flags, src_ip):
        if flags == "":
            self.raise_alert(
                message=f"NULL scan detected from {src_ip}",
                category="Port Scan",
                src_ip=src_ip,
                meta={
                    "scan_type": "NULL Scan",
                    "severity": "high"
                }
            )
    
    def _detect_xmas_scan(self, flags, src_ip):
        if "FPU" in flags:
            self.raise_alert(
                message=f"XMAS scan detected from {src_ip}",
                category="Port Scan",
                src_ip=src_ip,
                meta={
                    "scan_type": "XMAS Scan",
                    "severity": "high"
                }
            )
    
    def raise_alert(self, message, category, src_ip, meta=None):
        self.logger.warning(f"ALERT: {category} - {message}")
        save_alert(message, category, src_ip, meta or {})