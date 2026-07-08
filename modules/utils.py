import random
import time
import logging
import requests
import json
import psycopg2
import psycopg2.extras
from config import DATABASE_URL, PROXY_LIST, PROCESSING_TIMEOUT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- PROXY ----
def random_proxy():
    if PROXY_LIST:
        return random.choice(PROXY_LIST)
    return None

def random_user_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    ]
    return random.choice(agents)

def rate_limit(min_sec=1, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def safe_request(method, url, **kwargs):
    proxies = None
    proxy = random_proxy()
    if proxy:
        proxies = {'http': proxy, 'https': proxy}
    headers = {'User-Agent': random_user_agent()}
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    if proxies and 'proxies' not in kwargs:
        kwargs['proxies'] = proxies
    if 'timeout' not in kwargs:
        kwargs['timeout'] = PROCESSING_TIMEOUT
    try:
        return requests.request(method, url, **kwargs)
    except Exception as e:
        logger.error(f"Request failed: {e}")
        return None

# ---- DATABASE (Neon) ----
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def db_insert_target(identifier, platform, osint_data, profile=None):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO targets (identifier, platform, osint, profile) VALUES (%s, %s, %s, %s) RETURNING id",
        (identifier, platform, json.dumps(osint_data), json.dumps(profile) if profile else None)
    )
    target_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return target_id

def db_get_target(target_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM targets WHERE id = %s", (target_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def db_update_target_profile(target_id, profile):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE targets SET profile = %s WHERE id = %s", (json.dumps(profile), target_id))
    conn.commit()
    cur.close()
    conn.close()

def db_log_attack(target_id, attack_type, result):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO attacks (target_id, attack, result) VALUES (%s, %s, %s)",
        (target_id, attack_type, json.dumps(result))
    )
    conn.commit()
    cur.close()
    conn.close()

def db_list_targets():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM targets ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
