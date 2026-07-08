import requests
from modules.utils import random_proxy, random_user_agent, logger, PROCESSING_TIMEOUT

class WaDeliveryFingerprint:
    def exploit(self, phone):
        url = f"https://web.whatsapp.com/check?phone={phone}"
        headers = {'User-Agent': random_user_agent()}
        proxies = {'http': random_proxy(), 'https': random_proxy()} if random_proxy() else None
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=PROCESSING_TIMEOUT)
            if resp.status_code == 200:
                if 'registered' in resp.text:
                    return {'success': True, 'output': f'Phone {phone} registered on WhatsApp'}
                else:
                    return {'success': True, 'output': f'Phone {phone} not registered'}
            else:
                return {'success': False, 'output': f'HTTP {resp.status_code}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}
