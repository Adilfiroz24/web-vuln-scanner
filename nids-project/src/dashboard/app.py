from flask import Flask, render_template, jsonify, request
from storage.models import (
    get_all_alerts, get_total_alerts, get_category_count,
    get_top_attackers, get_alerts_over_time, get_protocol_distribution,
    get_recent_alerts, get_attack_stats, get_map_data
)
from utils.logger import setup_logger
import os

logger = setup_logger('dashboard')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'nids-secret-key-2024')
    
    @app.route('/')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/attack-logs')
    def attack_logs():
        return render_template('attack_logs.html')
    
    @app.route('/reports')
    def reports():
        return render_template('reports.html')
    
    @app.route('/settings')
    def settings():
        return render_template('settings.html')
    
    @app.route('/api/alerts')
    def api_alerts():
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        alerts = get_all_alerts(limit=limit, offset=offset)
        return jsonify(alerts)
    
    @app.route('/api/stats')
    def api_stats():
        stats = {
            'total_alerts': get_total_alerts(),
            'category_count': get_category_count(),
            'top_attackers': get_top_attackers(10),
            'alerts_over_time': get_alerts_over_time(24),
            'protocol_distribution': get_protocol_distribution(),
            'recent_alerts': get_recent_alerts(10),
            'attack_stats': get_attack_stats(),
            'map_data': get_map_data()
        }
        return jsonify(stats)
    
    @app.route('/api/map-data')
    def api_map_data():
        map_data = get_map_data()
        return jsonify(map_data)
    
    @app.route('/api/export/alerts')
    def export_alerts():
        alerts = get_all_alerts(limit=1000)
        return jsonify(alerts)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)