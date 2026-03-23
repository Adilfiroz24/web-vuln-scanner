import requests
import os
from utils.logger import setup_logger

logger = setup_logger('telegram_alert')

class TelegramAlert:
    def __init__(self):
        self.enabled = False
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
        
        if all([self.bot_token, self.chat_id]):
            self.enabled = True
            logger.info("Telegram alerts enabled")
        else:
            logger.warning("Telegram alerts disabled - missing configuration")
    
    def send_alert(self, alert_data):
        """Send Telegram alert"""
        if not self.enabled:
            return False
            
        try:
            # Create message
            message = f"""
🚨 *NIDS Security Alert*

*Category:* {alert_data['category']}
*Message:* {alert_data['message']}
*Source IP:* `{alert_data['src_ip']}`
*Country:* {alert_data['country']}
*Time:* {alert_data['timestamp']}

*Severity:* {alert_data.get('severity', 'medium').upper()}
            """
            
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Telegram alert sent for {alert_data['category']}")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

# Global instance
telegram_alerter = TelegramAlert()

def send_telegram_alert(alert_data):
    """Send Telegram alert (wrapper function)"""
    return telegram_alerter.send_alert(alert_data)