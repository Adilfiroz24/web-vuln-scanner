from .logger import setup_logger

logger = setup_logger('notifier')

socketio = None

def init_notifier(sio):
    global socketio
    socketio = sio
    logger.info("Notifier initialized")

def send_alert_notification(alert_data):
    try:
        if socketio:
            socketio.emit('new_alert', alert_data)
            logger.debug(f"Alert notification sent: {alert_data['category']}")
        else:
            logger.warning("SocketIO not initialized - alert not sent")
    except Exception as e:
        logger.error(f"Error sending alert notification: {e}")

def send_dashboard_update(stats_data):
    try:
        if socketio:
            socketio.emit('stats_update', stats_data)
    except Exception as e:
        logger.error(f"Error sending dashboard update: {e}")