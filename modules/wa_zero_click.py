import re
import requests
from modules.utils import random_user_agent, random_proxy
from config import PHONE_VALIDATION_API_KEY

class WhatsAppZeroClickRCE:
    def exploit(self, phone):
        """
        Check if a phone number is registered on WhatsApp.
        Tries the official web endpoint first; if that fails (HTTP 400),
        falls back to AbstractAPI if a key is provided.
        """
        # Clean and format phone number
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        # Remove extra zero after country code (e.g., +2340... -> +234...)
        match = re.match(r'^\+(\d+)(0+)(\d+)$', cleaned)
        if match:
            country, zeros, rest = match.groups()
            cleaned = '+' + country + rest
        if len(cleaned) < 10:
            return {'success': False, 'output': 'Invalid phone number. Must include country code (e.g., +2348114764800).'}

        # Method 1: Try WhatsApp web endpoint
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
                    return {'success': True, 'output': f'✅ Phone {cleaned} is REGISTERED on WhatsApp.'}
                else:
                    return {'success': True, 'output': f'❌ Phone {cleaned} is NOT registered on WhatsApp.'}
            elif resp.status_code == 400:
                # Fallback to AbstractAPI if available
                if PHONE_VALIDATION_API_KEY:
                    return self._check_via_abstractapi(cleaned)
                else:
                    return {'success': False, 'output': '⚠️ WhatsApp public endpoint returned HTTP 400. Please set PHONE_VALIDATION_API_KEY in environment to use AbstractAPI fallback.'}
            else:
                return {'success': False, 'output': f'⚠️ WhatsApp API error: HTTP {resp.status_code}'}
        except Exception as e:
            # Fallback to AbstractAPI on any connection error
            if PHONE_VALIDATION_API_KEY:
                return self._check_via_abstractapi(cleaned)
            else:
                return {'success': False, 'output': f'⚠️ Error: {str(e)}'}

    def _check_via_abstractapi(self, phone):
        """Fallback: use AbstractAPI phone validation."""
        url = f"https://phonevalidation.abstractapi.com/v1/?api_key={PHONE_VALIDATION_API_KEY}&phone={phone}"
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('valid'):
                    return {'success': True, 'output': f'✅ Phone {phone} is VALID (AbstractAPI). It may be registered on WhatsApp.'}
                else:
                    return {'success': True, 'output': f'❌ Phone {phone} is INVALID (AbstractAPI).'}
            else:
                return {'success': False, 'output': f'⚠️ AbstractAPI error: HTTP {resp.status_code} – {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': f'⚠️ AbstractAPI error: {str(e)}'}
