import requests

def get_location(ip):
    try:
        resp = requests.get(f"https://ipapi.co/{ip}/json/", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {'error': 'Geolocation failed'}
