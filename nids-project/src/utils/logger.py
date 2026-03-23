import logging
import os

def setup_logger(name, log_level=logging.INFO):
    logs_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    alert_handler = logging.FileHandler(
        os.path.join(logs_dir, 'alerts.log')
    )
    alert_handler.setLevel(logging.WARNING)
    alert_handler.setFormatter(formatter)
    
    packet_handler = logging.FileHandler(
        os.path.join(logs_dir, 'packets.log')
    )
    packet_handler.setLevel(logging.DEBUG)
    packet_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(alert_handler)
    logger.addHandler(packet_handler)
    logger.addHandler(console_handler)
    
    return logger