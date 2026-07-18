import requests
from modules.utils import logger, safe_request

class TikTokRealAttack:
    def __init__(self, session_cookie):
        self.session = requests.Session()
        if session_cookie:
            self.session.cookies.set('sessionid', session_cookie)
        self.base_url = 'https://www.tiktok.com'

    def post_comment(self, video_id, comment_text):
        if not self.session.cookies.get('sessionid'):
            return {'success': False, 'output': 'No valid TikTok session.'}
        url = f'{self.base_url}/api/comment/publish/'
        payload = {'video_id': video_id, 'text': comment_text, 'reply_id': 0, 'visible_to': 0}
        try:
            resp = self.session.post(url, data=payload)
            if resp.status_code == 200 and resp.json().get('status_code') == 0:
                return {'success': True, 'output': f'Comment posted on video {video_id}.'}
            else:
                return {'success': False, 'output': f'Comment failed: {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def trigger_password_reset(self, username, email):
        url = f'{self.base_url}/api/v1/account/reset_password/'
        data = {'username': username, 'email': email}
        try:
            resp = self.session.post(url, data=data)
            if resp.status_code == 200 and resp.json().get('status_code') == 0:
                return {'success': True, 'output': f'Password reset email sent to {email}'}
            else:
                return {'success': False, 'output': f'Reset failed: {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}

    def follow_target(self, target_username):
        url = f'{self.base_url}/api/relationship/follow/'
        data = {'username': target_username}
        try:
            resp = self.session.post(url, data=data)
            if resp.status_code == 200 and resp.json().get('status_code') == 0:
                return {'success': True, 'output': f'Followed @{target_username}'}
            else:
                return {'success': False, 'output': f'Follow failed: {resp.text[:200]}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}
