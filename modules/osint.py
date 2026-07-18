import subprocess
import json
import os
import shlex
from modules.utils import logger

class OSINTEngine:
    def scan_username(self, username):
        results = {'sherlock': {}, 'maigret': {}}
        # Sherlock
        try:
            cmd = ['sherlock', username, '--csv', '--output', '/tmp/sherlock.csv']
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, check=True, timeout=120)
            with open('/tmp/sherlock.csv', 'r') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 3:
                            results['sherlock'][parts[1]] = parts[2]
        except subprocess.TimeoutExpired:
            logger.error("Sherlock timed out after 120s.")
        except FileNotFoundError:
            logger.error("Sherlock command not found. Is it installed?")
        except Exception as e:
            logger.error(f"Sherlock failed: {e}")
        # Maigret
        try:
            cmd = ['maigret', username, '--json', '--output', '/tmp/maigret.json']
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, check=True, timeout=180)
            with open('/tmp/maigret.json', 'r') as f:
                data = json.load(f)
                for site, info in data.get('sites', {}).items():
                    if info.get('status') == 'found':
                        results['maigret'][site] = info.get('url', '')
        except subprocess.TimeoutExpired:
            logger.error("Maigret timed out after 180s.")
        except FileNotFoundError:
            logger.error("Maigret command not found. Is it installed?")
        except Exception as e:
            logger.error(f"Maigret failed: {e}")
        return results

    def scan_email(self, email):
        try:
            import holehe
            data = holehe.check(email)
            results = {}
            for service, info in data.items():
                if info.get('rateLimit') is False and info.get('exists'):
                    results[service] = info.get('url', '')
            return results
        except Exception as e:
            logger.error(f"Holehe failed: {e}")
            return {}
