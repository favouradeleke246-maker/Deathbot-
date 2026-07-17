import time
import socket
import requests
import psycopg2
from config import DATABASE_URL, TELEGRAM_TOKEN, GROQ_API_KEY, GOOGLE_API_KEY, DEEPSEEK_API_KEY
from modules.utils import logger

class Diagnostics:
    @staticmethod
    def run_all():
        results = {}
        results['database'] = Diagnostics.test_database()
        results['telegram_api'] = Diagnostics.test_telegram_api()
        results['groq'] = Diagnostics.test_groq() if GROQ_API_KEY else {'status': 'SKIPPED', 'message': 'GROQ_API_KEY not set'}
        results['gemini'] = Diagnostics.test_gemini() if GOOGLE_API_KEY else {'status': 'SKIPPED', 'message': 'GOOGLE_API_KEY not set'}
        results['deepseek'] = Diagnostics.test_deepseek() if DEEPSEEK_API_KEY else {'status': 'SKIPPED', 'message': 'DEEPSEEK_API_KEY not set'}
        results['network'] = Diagnostics.test_network()
        results['uptime'] = {'status': 'OK', 'message': f'Bot running since {time.strftime("%Y-%m-%d %H:%M:%S")}'}
        return results

    @staticmethod
    def test_database():
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            return {'status': 'OK', 'message': 'Database connection successful'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    @staticmethod
    def test_telegram_api():
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getMe"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                return {'status': 'OK', 'message': 'Telegram API reachable'}
            else:
                return {'status': 'ERROR', 'message': f'HTTP {resp.status_code}'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    @staticmethod
    def test_groq():
        try:
            import groq
            client = groq.Client(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {'status': 'OK', 'message': 'Groq API responded'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    @staticmethod
    def test_gemini():
        try:
            import google.generativeai as genai
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-2.5-flash')
            model.generate_content("test")
            return {'status': 'OK', 'message': 'Gemini API responded'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    @staticmethod
    def test_deepseek():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
            client.chat.completions.create(
                model="deepseek-v4-flash",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {'status': 'OK', 'message': 'DeepSeek API responded'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    @staticmethod
    def test_network():
        try:
            socket.gethostbyname('google.com')
            return {'status': 'OK', 'message': 'Outbound internet reachable'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
