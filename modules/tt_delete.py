import requests

def delete_tiktok_account(session_cookie, user_id):
    url = 'https://www.tiktok.com/api/v1/account/delete'
    headers = {'Cookie': session_cookie, 'User-Agent': 'TikTok/26.2.1 (Android; 11)'}
    data = {'user_id': user_id}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 200 and resp.json().get('status_code') == 0:
            return {'success': True, 'output': 'TikTok account deleted successfully.'}
        else:
            return {'success': False, 'output': f'Delete failed: {resp.text[:200]}'}
    except Exception as e:
        return {'success': False, 'output': str(e)}
