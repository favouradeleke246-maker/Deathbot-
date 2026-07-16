import requests
import nmap
from modules.utils import logger

class ThreatIntel:
    @staticmethod
    def virustotal_ip(ip, api_key=None):
        """Check IP reputation with VirusTotal (requires API key)."""
        if not api_key:
            return {'success': False, 'error': 'No VirusTotal API key provided.'}
        url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
        headers = {'x-apikey': api_key}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                stats = data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                return {'success': True, 'detections': stats.get('malicious', 0), 'total': sum(stats.values())}
            else:
                return {'success': False, 'error': f'HTTP {resp.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def nmap_scan(host, ports='1-1024'):
        """Perform a lightweight port scan."""
        try:
            nm = nmap.PortScanner()
            nm.scan(host, ports)
            open_ports = []
            if host in nm.all_hosts():
                for proto in nm[host].all_protocols():
                    for port in nm[host][proto].keys():
                        if nm[host][proto][port]['state'] == 'open':
                            open_ports.append(port)
            return {'success': True, 'open_ports': open_ports}
        except Exception as e:
            logger.error(f"Nmap scan failed: {e}")
            return {'success': False, 'error': str(e)}
