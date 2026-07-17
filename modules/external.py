import shodan
from config import SHODAN_API_KEY

def shodan_lookup(ip):
    if not SHODAN_API_KEY:
        return {'error': 'SHODAN_API_KEY not set'}
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        return api.host(ip)
    except Exception as e:
        return {'error': str(e)}
