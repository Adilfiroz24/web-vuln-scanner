from flask import Flask, render_template, request, jsonify
from services import virustotal, abuseipdb
from database import db

app = Flask(__name__)

db.init_db()

@app.route('/')
def index():
    recent = db.get_recent_lookups()
    return render_template('dashboard.html', recent=recent)

@app.route('/lookup', methods=['POST'])
def lookup():
    ioc = request.form['ioc']
    ioc_type = request.form['type']
    
    result = {}
    if ioc_type == 'ip':
        vt_result = virustotal.query_virustotal(ioc)
        abuse_result = abuseipdb.query_abuseipdb(ioc)
        result = {'virustotal': vt_result, 'abuseipdb': abuse_result}
        if vt_result and vt_result.get('malicious', 0) > 0:
            db.insert_lookup(ioc, ioc_type, 'malicious')
        else:
            db.insert_lookup(ioc, ioc_type, 'benign')
    elif ioc_type in ['domain', 'hash']:
        vt_result = virustotal.query_virustotal(ioc)
        result = {'virustotal': vt_result}
        if vt_result and vt_result.get('malicious', 0) > 0:
            db.insert_lookup(ioc, ioc_type, 'malicious')
        else:
            db.insert_lookup(ioc, ioc_type, 'benign')
    else:
        return "Invalid IOC type", 400
    
    return render_template('dashboard.html', result=result, ioc=ioc, recent=db.get_recent_lookups())

@app.route('/data')
def data():
    stats = db.get_lookup_stats()
    labels = [row[0] for row in stats]
    malicious = [row[1] for row in stats]
    benign = [row[2] for row in stats]
    return jsonify({'labels': labels, 'malicious': malicious, 'benign': benign})

if __name__ == '__main__':
    app.run(debug=True)