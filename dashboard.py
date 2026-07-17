import os
import json
from flask import Flask, render_template, jsonify, request
from orchestrator import Orchestrator
from modules.utils import db_list_targets, db_get_target
import requests

app = Flask(__name__)
orch = Orchestrator()

@app.route('/')
def index():
    targets = db_list_targets()
    return render_template('index.html', targets=targets)

@app.route('/api/target/<int:tid>')
def target_detail(tid):
    target = db_get_target(tid)
    if target:
        return jsonify(target)
    return jsonify({'error': 'Target not found'}), 404

@app.route('/api/all_targets')
def all_targets():
    targets = db_list_targets()
    return jsonify(targets)

@app.route('/api/map_data')
def map_data():
    targets = db_list_targets()
    markers = []
    for t in targets:
        osint = t.get('osint', {})
        ip = osint.get('ip')
        if ip:
            try:
                resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    lat = data.get('latitude')
                    lon = data.get('longitude')
                    if lat and lon:
                        markers.append({
                            'id': t['id'],
                            'identifier': t['identifier'],
                            'lat': float(lat),
                            'lon': float(lon),
                            'city': data.get('city', 'Unknown'),
                            'country': data.get('country_name', 'Unknown')
                        })
            except:
                pass
    return jsonify(markers)

@app.route('/api/stats')
def stats():
    targets = db_list_targets()
    return jsonify({
        'total_targets': len(targets),
        'recent_5': targets[:5] if targets else []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
