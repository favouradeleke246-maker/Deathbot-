import requests
from modules.utils import random_proxy, random_user_agent, logger

class WaDeliveryFingerprint:
    def exploit(self, phone):
        """
        Checks if a phone number is registered on WhatsApp using the official web check endpoint.
        This is a real API call.
        """
        url = f"https://web.whatsapp.com/check?phone={phone}"
        headers = {'User-Agent': random_user_agent()}
        proxies = {'http': random_proxy(), 'https': random_proxy()} if random_proxy() else None
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=30)
            if resp.status_code == 200:
                if 'registered' in resp.text:
                    return {'success': True, 'output': f'Phone {phone} is registered on WhatsApp'}
                else:
                    return {'success': True, 'output': f'Phone {phone} is not registered on WhatsApp'}
            else:
                return {'success': False, 'output': f'HTTP {resp.status_code} – WhatsApp API returned error'}
        except Exception as e:
            return {'success': False, 'output': f'Error: {str(e)}'}
