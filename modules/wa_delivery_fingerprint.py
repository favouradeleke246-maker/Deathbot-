import requests
import re
from modules.utils import random_proxy, random_user_agent, logger

class WaDeliveryFingerprint:
    def exploit(self, phone):
        # Remove non‑numeric characters and ensure country code
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        if len(cleaned) < 10:
            return {'success': False, 'output': 'Phone number too short. Must include country code.'}

        url = f"https://web.whatsapp.com/check?phone={cleaned}"
        headers = {'User-Agent': random_user_agent()}
        proxies = {'http': random_proxy(), 'https': random_proxy()} if random_proxy() else None
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            if resp.status_code == 200:
                if 'registered' in resp.text:
                    return {'success': True, 'output': f'Phone {cleaned} is registered on WhatsApp'}
                else:
                    return {'success': True, 'output': f'Phone {cleaned} is not registered on WhatsApp'}
            else:
                return {'success': False, 'output': f'HTTP {resp.status_code} – WhatsApp API returned error: {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': f'Error: {str(e)}'}
