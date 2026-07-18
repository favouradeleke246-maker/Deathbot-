import requests

def report_tiktok_account(session_cookie, target_username):
    url = 'https://www.tiktok.com/api/v1/feedback/report'
    headers = {'Cookie': session_cookie}
    data = {
        'target_username': target_username,
        'reason': 'impersonation',
        'description': 'This account is pretending to be someone else.'
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 200 and resp.json().get('status_code') == 0:
            return {'success': True, 'output': f'Report submitted. Account may be suspended.'}
        else:
            return {'success': False, 'output': f'Report failed: {resp.text[:200]}'}
    except Exception as e:
        return {'success': False, 'output': str(e)}
