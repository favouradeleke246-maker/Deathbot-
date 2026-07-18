import requests

def delete_whatsapp_account(session_cookie):
    url = 'https://web.whatsapp.com/account/delete'
    headers = {'Cookie': session_cookie, 'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.post(url, headers=headers, timeout=10)
        if resp.status_code == 200 and 'deleted' in resp.text:
            return {'success': True, 'output': 'WhatsApp account permanently deleted.'}
        else:
            return {'success': False, 'output': f'Delete failed: {resp.status_code} – {resp.text[:200]}'}
    except Exception as e:
        return {'success': False, 'output': str(e)}
