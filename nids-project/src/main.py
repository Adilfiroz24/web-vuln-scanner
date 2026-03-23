import threading
import time
import signal
import sys
import os
import platform

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sniffing.packet_sniffer import PacketSniffer
from dashboard.app import create_app
from storage.db import init_db
from utils.logger import setup_logger

class NIDSController:
    def __init__(self):
        self.logger = setup_logger('nids_controller')
        self.sniffer = None
        self.app = None
        self.running = False
        
    def start(self):
        try:
            if platform.system() == "Windows":
                try:
                    import ctypes
                    if not ctypes.windll.shell32.IsUserAnAdmin():
                        self.logger.warning("Not running as Administrator. Packet capture may not work.")
                except:
                    pass
            
            init_db()
            
            self.app = create_app()
            flask_thread = threading.Thread(
                target=lambda: self.app.run(
                    host='0.0.0.0', 
                    port=5000, 
                    debug=False, 
                    use_reloader=False
                ),
                name="Flask-Thread"
            )
            flask_thread.daemon = True
            flask_thread.start()
            
            self.logger.info("Starting Flask server...")
            time.sleep(3)
            
            self.logger.info("Starting packet sniffer...")
            self.sniffer = PacketSniffer()
            sniffer_thread = threading.Thread(
                target=self.sniffer.start_sniffing,
                name="Sniffer-Thread"
            )
            sniffer_thread.daemon = True
            sniffer_thread.start()
            
            self.running = True
            self.logger.info("NIDS Started Successfully!")
            self.logger.info("Dashboard: http://localhost:5000")
            self.logger.info("Sniffing packets... Press Ctrl+C to stop")
            
            while self.running:
                time.sleep(1)
                
        except Exception as e:
            self.logger.error(f"Failed to start NIDS: {e}")
            self.stop()
    
    def stop(self):
        self.running = False
        if self.sniffer:
            self.sniffer.stop_sniffing()
        self.logger.info("NIDS Stopped")

def signal_handler(sig, frame):
    print("\nShutting down NIDS...")
    controller.stop()
    sys.exit(0)

if __name__ == "__main__":
    print("NIDS - Network Intrusion Detection System")
    print("=" * 50)
    
    controller = NIDSController()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
    except Exception as e:
        print(f"Fatal error: {e}")