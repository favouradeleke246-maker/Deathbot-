import re
import requests
from modules.utils import random_user_agent, random_proxy

class WhatsAppZeroClickRCE:
    def exploit(self, phone):
        """
        Check if a phone number is registered on WhatsApp.
        This is a real API call to WhatsApp's public endpoint.
        """
        # Clean and format phone number
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        # Remove extra zero after country code
        match = re.match(r'^\+(\d+)(0+)(\d+)$', cleaned)
        if match:
            country, zeros, rest = match.groups()
            cleaned = '+' + country + rest
        if len(cleaned) < 10:
            return {'success': False, 'output': 'Invalid phone number. Must include country code.'}

        url = f"https://web.whatsapp.com/check?phone={cleaned}"
        headers = {'User-Agent': random_user_agent()}
        proxies = {'http': random_proxy(), 'https': random_proxy()} if random_proxy() else None
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            if resp.status_code == 200:
                if 'registered' in resp.text:
                    return {'success': True, 'output': f'✅ Phone {cleaned} is REGISTERED on WhatsApp.'}
                else:
                    return {'success': True, 'output': f'❌ Phone {cleaned} is NOT registered on WhatsApp.'}
            else:
                return {'success': False, 'output': f'⚠️ API error: HTTP {resp.status_code}'}
        except Exception as e:
            return {'success': False, 'output': f'⚠️ Error: {str(e)}'}
