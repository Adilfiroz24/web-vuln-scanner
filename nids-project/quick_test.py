import sys
import os
import time
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from storage.models import save_alert

def test_alert_system():
    print("Starting NIDS Quick Test...")
    print("This will generate test alerts to verify the system\n")
    
    test_alerts = [
        {
            "message": "Port scan detected from 192.168.1.100 - 25 unique ports scanned",
            "category": "Port Scan",
            "src_ip": "192.168.1.100",
            "meta": {"unique_ports": 25, "scan_type": "SYN Scan"}
        },
        {
            "message": "SYN flood attack from 10.0.0.50 - 1500 SYN packets/second",
            "category": "SYN Flood", 
            "src_ip": "10.0.0.50",
            "meta": {"packet_rate": 1500, "duration": "10s"}
        },
        {
            "message": "Brute force attempt on SSH port from 203.0.113.45",
            "category": "Brute Force",
            "src_ip": "203.0.113.45", 
            "meta": {"target_port": 22, "attempts": 15, "service": "SSH"}
        },
        {
            "message": "Traffic anomaly detected - 5000 packets/second (normal: 1000)",
            "category": "Anomaly",
            "src_ip": "Multiple",
            "meta": {"current_rate": 5000, "baseline": 1000, "anomaly_type": "Traffic Spike"}
        },
        {
            "message": "XMAS scan detected from 198.51.100.23",
            "category": "Port Scan",
            "src_ip": "198.51.100.23",
            "meta": {"scan_type": "XMAS Scan", "flags": "FPU"}
        }
    ]
    
    print("Generating test alerts...")
    
    for i, alert in enumerate(test_alerts, 1):
        print(f"  {i}. {alert['category']}: {alert['message']}")
        
        alert_id = save_alert(
            alert["message"],
            alert["category"], 
            alert["src_ip"],
            alert["meta"]
        )
        
        if alert_id:
            print(f"     Alert saved (ID: {alert_id})")
        else:
            print(f"     Failed to save alert")
        
        time.sleep(2)
    
    print(f"\nQuick test completed!")
    print(f"Check the dashboard at http://localhost:5000 to see the alerts")
    print(f"Alerts saved to database: src/storage/nids.db")

if __name__ == "__main__":
    print("NIDS Quick Test Utility")
    print("=" * 40)
    
    try:
        test_alert_system()
        
        print("\nAll tests completed successfully!")
        print("\nNext steps:")
        print("1. Start the main NIDS: python src/main.py")
        print("2. Open http://localhost:5000 in your browser") 
        print("3. Run test_traffic.py to generate real network traffic")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        print("Make sure the database is initialized and dependencies are installed")