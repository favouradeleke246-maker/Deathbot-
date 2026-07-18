import requests

def request_deactivation(phone):
    url = 'https://www.whatsapp.com/account/deactivate'
    data = {'phone': phone}
    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.status_code == 200 and 'confirmation' in resp.text:
            return {'success': True, 'output': 'Deactivation request sent. Target will receive SMS.'}
        else:
            return {'success': False, 'output': f'Request failed: {resp.text[:200]}'}
    except Exception as e:
        return {'success': False, 'output': str(e)}
