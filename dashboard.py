import os
import json
from flask import Flask, render_template, jsonify
from orchestrator import Orchestrator
from modules.utils import db_list_targets, db_get_target

app = Flask(__name__)
orch = Orchestrator()

@app.route('/')
def index():
    """Show all targets in a table."""
    targets = db_list_targets()
    return render_template('index.html', targets=targets)

@app.route('/api/target/<int:tid>')
def target_detail(tid):
    """Return JSON data for a specific target."""
    target = db_get_target(tid)
    if target:
        return jsonify(target)
    return jsonify({'error': 'Target not found'}), 404

@app.route('/api/stats')
def stats():
    """Simple statistics about the database."""
    targets = db_list_targets()
    return jsonify({
        'total_targets': len(targets),
        'recent_5': targets[:5] if targets else []
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
