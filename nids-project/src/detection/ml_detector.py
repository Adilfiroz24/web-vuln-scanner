import time
import math
from collections import defaultdict, deque
from utils.logger import setup_logger
from storage.models import save_alert

class MLDetector:
    def __init__(self):
        self.logger = setup_logger('ml_detector')
        self.packet_features = deque(maxlen=1000)
        self.ip_behavior = defaultdict(lambda: {
            'packet_count': 0,
            'unique_ports': set(),
            'start_time': time.time()
        })
        
        self.feature_means = None
        self.feature_stds = None
        self.is_trained = False
        self.training_start = time.time()
    
    def analyze_packet(self, packet, src_ip, dst_ip, protocol, sport, dport, payload):
        features = self._extract_features(packet, src_ip, protocol, sport, dport, payload)
        self.packet_features.append(features)
        
        if len(self.packet_features) > 100 and not self.is_trained:
            self._train_model()
        
        if self.is_trained:
            anomaly_score = self._calculate_anomaly_score(features)
            if anomaly_score > 2.0:
                self.raise_alert(
                    message=f"ML anomaly detected from {src_ip} - score: {anomaly_score:.2f}",
                    category="ML Anomaly",
                    src_ip=src_ip,
                    meta={
                        "anomaly_score": anomaly_score,
                        "protocol": protocol,
                        "target_port": dport,
                        "severity": "medium"
                    }
                )
    
    def _extract_features(self, packet, src_ip, protocol, sport, dport, payload):
        current_time = time.time()
        ip_info = self.ip_behavior[src_ip]
        
        ip_info['packet_count'] += 1
        ip_info['unique_ports'].add(dport)
        
        features = [
            ip_info['packet_count'],
            len(ip_info['unique_ports']),
            current_time - ip_info['start_time'],
            len(payload) if payload else 0,
            sport,
            dport,
            1 if protocol == 'TCP' else 0,
            1 if protocol == 'UDP' else 0,
            1 if protocol == 'ICMP' else 0,
            1 if dport < 1024 else 0
        ]
        
        return features
    
    def _train_model(self):
        try:
            if len(self.packet_features) < 2:
                return
                
            num_features = len(self.packet_features[0])
            self.feature_means = [0] * num_features
            self.feature_stds = [0] * num_features
            
            for i in range(num_features):
                values = [features[i] for features in self.packet_features]
                self.feature_means[i] = sum(values) / len(values)
                
                variance = sum((x - self.feature_means[i]) ** 2 for x in values) / len(values)
                self.feature_stds[i] = math.sqrt(variance) if variance > 0 else 1
            
            self.is_trained = True
            self.logger.info("ML model trained successfully")
        except Exception as e:
            self.logger.error(f"ML training error: {e}")
    
    def _calculate_anomaly_score(self, features):
        try:
            if not self.feature_means or not self.feature_stds:
                return 0
                
            score = 0
            for i in range(len(features)):
                if self.feature_stds[i] > 0:
                    normalized = (features[i] - self.feature_means[i]) / self.feature_stds[i]
                    score += normalized * normalized
            
            return math.sqrt(score)
        except:
            return 0
    
    def raise_alert(self, message, category, src_ip, meta=None):
        self.logger.warning(f"ML DETECTION: {category} - {message}")
        save_alert(message, category, src_ip, meta or {})