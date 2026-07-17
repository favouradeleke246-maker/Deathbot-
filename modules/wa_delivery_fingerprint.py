import re
import requests
from modules.utils import random_user_agent, random_proxy
from config import PHONE_VALIDATION_API_KEY

class WaDeliveryFingerprint:
    def exploit(self, phone):
        """
        Same logic as the RCE module – checks if number is valid/registered.
        """
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        match = re.match(r'^\+(\d+)(0+)(\d+)$', cleaned)
        if match:
            country, zeros, rest = match.groups()
            cleaned = '+' + country + rest
        if len(cleaned) < 10:
            return {'success': False, 'output': 'Invalid phone number.'}

        # Primary: WhatsApp web endpoint
        url = f"https://web.whatsapp.com/check?phone={cleaned}"
        headers = {
            'User-Agent': random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        proxies = {'http': random_proxy(), 'https': random_proxy()} if random_proxy() else None
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            if resp.status_code == 200:
                if 'registered' in resp.text:
                    return {'success': True, 'output': f'✅ Phone {cleaned} is registered on WhatsApp.'}
                else:
                    return {'success': True, 'output': f'❌ Phone {cleaned} is not registered on WhatsApp.'}
            elif resp.status_code == 400:
                if PHONE_VALIDATION_API_KEY:
                    return self._check_via_abstractapi(cleaned)
                else:
                    return {'success': False, 'output': '⚠️ WhatsApp API unavailable. Set PHONE_VALIDATION_API_KEY for fallback.'}
            else:
                return {'success': False, 'output': f'⚠️ HTTP {resp.status_code}'}
        except Exception as e:
            if PHONE_VALIDATION_API_KEY:
                return self._check_via_abstractapi(cleaned)
            else:
                return {'success': False, 'output': f'⚠️ Error: {str(e)}'}

    def _check_via_abstractapi(self, phone):
        url = f"https://phonevalidation.abstractapi.com/v1/?api_key={PHONE_VALIDATION_API_KEY}&phone={phone}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('valid'):
                    return {'success': True, 'output': f'✅ Phone {phone} is VALID (AbstractAPI).'}
                else:
                    return {'success': True, 'output': f'❌ Phone {phone} is INVALID.'}
            else:
                return {'success': False, 'output': f'⚠️ AbstractAPI error: HTTP {resp.status_code}'}
        except Exception as e:
            return {'success': False, 'output': f'⚠️ AbstractAPI error: {str(e)}'}
