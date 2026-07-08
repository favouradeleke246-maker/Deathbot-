import random, time, logging, requests, sqlite3
from config import PROXY_LIST, DB_PATH, LOG_LEVEL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def random_proxy():
    return random.choice(PROXY_LIST) if PROXY_LIST else None

def random_user_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    return random.choice(agents)

def rate_limit(min_sec=1, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def safe_request(method, url, **kwargs):
    proxies = {'http': random_proxy(), 'https': random_proxy()} if random_proxy() else None
    headers = {'User-Agent': random_user_agent()}
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    if proxies:
        kwargs['proxies'] = proxies
    try:
        return requests.request(method, url, timeout=30, **kwargs)
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None
