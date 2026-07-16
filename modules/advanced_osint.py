import requests
import socket
import whois
from modules.utils import logger

class AdvancedOSINT:
    @staticmethod
    def email_breach(email):
        """Check if email appears in known data breaches (HaveIBeenPwned)."""
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                breaches = [b['Name'] for b in resp.json()]
                return {'success': True, 'breaches': breaches}
            elif resp.status_code == 404:
                return {'success': True, 'breaches': []}
            else:
                return {'success': False, 'error': f'HTTP {resp.status_code}'}
        except Exception as e:
            logger.error(f"Breach check failed: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def whois_lookup(domain):
        """Get WHOIS information for a domain."""
        try:
            w = whois.whois(domain)
            return {
                'success': True,
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers
            }
        except Exception as e:
            logger.error(f"WHOIS failed: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def dns_enum(domain):
        """Simple DNS resolution."""
        try:
            ip = socket.gethostbyname(domain)
            return {'success': True, 'ip': ip}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def reverse_image_search(image_url):
        """Search for similar images using TinEye (public endpoint)."""
        try:
            # Use TinEye's public search (limited)
            resp = requests.get(f'https://tineye.com/search?url={image_url}', timeout=10)
            if resp.status_code == 200:
                return {'success': True, 'status': 'Check TinEye manually for matches', 'url': f'https://tineye.com/search?url={image_url}'}
            else:
                return {'success': False, 'error': f'HTTP {resp.status_code}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
