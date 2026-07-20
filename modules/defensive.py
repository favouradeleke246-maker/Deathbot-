import os
import requests
from config import TELEGRAM_TOKEN, GROQ_API_KEY, GOOGLE_API_KEY, DATABASE_URL, SUPER_ADMIN_ID

def check_api_keys_exposure():
    keys_to_check = {
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'GROQ_API_KEY': GROQ_API_KEY,
        'GOOGLE_API_KEY': GOOGLE_API_KEY,
        'DATABASE_URL': DATABASE_URL,
        'SUPER_ADMIN_ID': str(SUPER_ADMIN_ID)
    }
    findings = []
    for name, value in keys_to_check.items():
        if not value or len(value) < 4:
            continue
        search_term = value[:8]
        url = f'https://api.github.com/search/code?q={search_term}'
        headers = {'Accept': 'application/vnd.github.v3+json'}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                total = data.get('total_count', 0)
                if total > 0:
                    items = data.get('items', [])[:3]
                    findings.append({
                        'key': name,
                        'exposed': True,
                        'count': total,
                        'examples': [{'repo': item['repository']['full_name'], 'url': item['html_url']} for item in items]
                    })
                else:
                    findings.append({'key': name, 'exposed': False})
            else:
                findings.append({'key': name, 'error': f'GitHub API error: {resp.status_code}'})
        except Exception as e:
            findings.append({'key': name, 'error': str(e)})
    return {
        'status': 'Scan completed',
        'findings': findings,
        'recommendation': 'If any key is exposed, revoke it immediately and rotate your credentials.'
    }
