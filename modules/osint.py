import subprocess, json, os
from modules.utils import logger

class OSINTEngine:
    def __init__(self):
        self.sherlock = 'sherlock'  # assume installed via pip
        self.maigret = 'maigret'
    def scan_username(self, username):
        results = {'sherlock': {}, 'maigret': {}}
        try:
            cmd = [self.sherlock, username, '--csv', '--output', '/tmp/sherlock.csv']
            subprocess.run(cmd, capture_output=True, check=True)
            with open('/tmp/sherlock.csv', 'r') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            results['sherlock'][parts[1]] = parts[2]
        except Exception as e:
            logger.error(f"Sherlock failed: {e}")
        try:
            cmd = [self.maigret, username, '--json', '--output', '/tmp/maigret.json']
            subprocess.run(cmd, capture_output=True, check=True)
            with open('/tmp/maigret.json', 'r') as f:
                data = json.load(f)
                for site, info in data.get('sites', {}).items():
                    if info.get('status') == 'found':
                        results['maigret'][site] = info.get('url', '')
        except Exception as e:
            logger.error(f"Maigret failed: {e}")
        return results
    def scan_email(self, email):
        try:
            import holehe
            data = holehe.check(email)
            return {svc: info.get('url') for svc, info in data.items() if info.get('exists')}
        except:
            return {}
