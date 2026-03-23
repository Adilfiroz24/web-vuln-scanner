import sqlite3
import json
import os
from datetime import datetime, timedelta
from utils.logger import setup_logger
from utils.geoip_lookup import get_geoip_info

class Database:
    def __init__(self):
        self.logger = setup_logger('database')
        self.db_path = os.path.join(os.path.dirname(__file__), 'nids.db')
        self.init_db()
    
    def init_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    category TEXT NOT NULL,
                    src_ip TEXT NOT NULL,
                    country TEXT,
                    country_code TEXT,
                    latitude REAL,
                    longitude REAL,
                    severity TEXT DEFAULT 'medium',
                    metadata TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_category ON alerts(category)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_ip ON alerts(src_ip)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity)')
            
            conn.commit()
            conn.close()
            self.logger.info("Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")

db = Database()

def save_alert(message, category, src_ip, metadata=None):
    try:
        geo_info = get_geoip_info(src_ip)
        meta_json = json.dumps(metadata) if metadata else "{}"
        
        severity = metadata.get('severity', 'medium') if metadata else 'medium'
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts 
            (message, category, src_ip, country, country_code, latitude, longitude, severity, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            message, 
            category, 
            src_ip,
            geo_info.get('country', 'Unknown'),
            geo_info.get('country_code', 'XX'),
            geo_info.get('lat', 0),
            geo_info.get('lon', 0),
            severity,
            meta_json
        ))
        
        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return alert_id
        
    except Exception as e:
        db.logger.error(f"Error saving alert: {e}")
        return None

def get_all_alerts(limit=100, offset=0):
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts 
            ORDER BY timestamp DESC 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'message': row[1],
                'category': row[2],
                'src_ip': row[3],
                'country': row[4],
                'country_code': row[5],
                'latitude': row[6],
                'longitude': row[7],
                'severity': row[8],
                'metadata': json.loads(row[9]) if row[9] else {},
                'timestamp': row[10]
            })
        
        conn.close()
        return alerts
        
    except Exception as e:
        db.logger.error(f"Error getting alerts: {e}")
        return []

def get_total_alerts():
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM alerts')
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception as e:
        db.logger.error(f"Error getting total alerts: {e}")
        return 0

def get_category_count():
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT category, COUNT(*) FROM alerts GROUP BY category')
        
        categories = {}
        for row in cursor.fetchall():
            categories[row[0]] = row[1]
        
        conn.close()
        return categories
        
    except Exception as e:
        db.logger.error(f"Error getting category count: {e}")
        return {}

def get_top_attackers(limit=10):
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT src_ip, country, COUNT(*) as attack_count
            FROM alerts 
            GROUP BY src_ip 
            ORDER BY attack_count DESC 
            LIMIT ?
        ''', (limit,))
        
        attackers = []
        for row in cursor.fetchall():
            attackers.append({
                'ip': row[0],
                'country': row[1],
                'count': row[2]
            })
        
        conn.close()
        return attackers
        
    except Exception as e:
        db.logger.error(f"Error getting top attackers: {e}")
        return []

def get_alerts_over_time(hours=24):
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as count
            FROM alerts 
            WHERE timestamp >= datetime('now', ?)
            GROUP BY hour
            ORDER BY hour
        ''', (f'-{hours} hours',))
        
        time_data = []
        for row in cursor.fetchall():
            time_data.append({
                'time': row[0],
                'count': row[1]
            })
        
        conn.close()
        return time_data
        
    except Exception as e:
        db.logger.error(f"Error getting alerts over time: {e}")
        return []

def get_protocol_distribution():
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT metadata FROM alerts WHERE metadata IS NOT NULL')
        
        protocols = {}
        for row in cursor.fetchall():
            try:
                meta = json.loads(row[0])
                protocol = meta.get('protocol', 'Unknown')
                protocols[protocol] = protocols.get(protocol, 0) + 1
            except:
                continue
        
        conn.close()
        return protocols
        
    except Exception as e:
        db.logger.error(f"Error getting protocol distribution: {e}")
        return {}

def get_recent_alerts(limit=10):
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM alerts 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'message': row[1],
                'category': row[2],
                'src_ip': row[3],
                'timestamp': row[10]
            })
        
        conn.close()
        return alerts
        
    except Exception as e:
        db.logger.error(f"Error getting recent alerts: {e}")
        return []

def get_attack_stats():
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE severity = "high"')
        high_severity = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM alerts WHERE timestamp >= datetime("now", "-1 hour")')
        last_hour = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT src_ip) FROM alerts')
        unique_attackers = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'high_severity_alerts': high_severity,
            'last_hour_alerts': last_hour,
            'unique_attackers': unique_attackers
        }
        
    except Exception as e:
        db.logger.error(f"Error getting attack stats: {e}")
        return {}

def get_map_data():
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                latitude, 
                longitude, 
                country,
                src_ip,
                category,
                COUNT(*) as attack_count
            FROM alerts 
            WHERE latitude != 0 AND longitude != 0
            GROUP BY src_ip
            ORDER BY attack_count DESC
            LIMIT 50
        ''')
        
        map_data = []
        for row in cursor.fetchall():
            map_data.append({
                'lat': row[0],
                'lon': row[1],
                'country': row[2],
                'ip': row[3],
                'category': row[4],
                'count': row[5]
            })
        
        conn.close()
        return map_data
        
    except Exception as e:
        db.logger.error(f"Error getting map data: {e}")
        return []