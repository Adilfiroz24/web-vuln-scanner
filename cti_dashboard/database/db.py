import sqlite3
import datetime
from config import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_FILE)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lookups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ioc_value TEXT NOT NULL,
            ioc_type TEXT NOT NULL,
            result TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_lookup(ioc_value, ioc_type, result):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO lookups (ioc_value, ioc_type, result) VALUES (?, ?, ?)',
                   (ioc_value, ioc_type, result))
    conn.commit()
    conn.close()

def get_recent_lookups(limit=10):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT ioc_value, ioc_type, result, timestamp FROM lookups ORDER BY timestamp DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_lookup_stats(days=7):
    conn = get_db()
    cursor = conn.cursor()
    date_from = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT DATE(timestamp) as date, 
               SUM(CASE WHEN result LIKE '%malicious%' THEN 1 ELSE 0 END) as malicious,
               SUM(CASE WHEN result NOT LIKE '%malicious%' THEN 1 ELSE 0 END) as benign
        FROM lookups
        WHERE DATE(timestamp) >= ?
        GROUP BY DATE(timestamp)
        ORDER BY date
    ''', (date_from,))
    rows = cursor.fetchall()
    conn.close()
    return rows