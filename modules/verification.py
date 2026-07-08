import requests
from modules.utils import safe_request, logger
from .wa_delivery_fingerprint import WaDeliveryFingerprint

class Verify:
    @staticmethod
    def check_tiktok_login(username, password):
        url = 'https://www.tiktok.com/api/v1/auth/login/'
        data = {'username': username, 'password': password}
        resp = safe_request('POST', url, data=data)
        if resp and resp.status_code == 200 and 'sessionid' in resp.cookies:
            return {'success': True, 'output': 'Login successful'}
        return {'success': False, 'output': 'Login failed'}

    @staticmethod
    def check_whatsapp_registration(phone):
        return WaDeliveryFingerprint().exploit(phone)
