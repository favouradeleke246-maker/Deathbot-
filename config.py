import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', '120'))
PROXY_LIST = [p.strip() for p in os.getenv('PROXY_LIST', '').split(',') if p.strip()]
TIKTOK_SESSION = os.getenv('TIKTOK_SESSION', '')
SMS_GATEWAY_API_KEY = os.getenv('SMS_GATEWAY_API_KEY', '')
SMS_GATEWAY_URL = os.getenv('SMS_GATEWAY_URL', 'https://api.smsgateway.com/send')
PLUGIN_DIR = 'modules/plugins'

# New AI & Admin settings
DEFAULT_AI = os.getenv('DEFAULT_AI', 'groq')
OLLAMA_URL = os.getenv('OLLAMA_URL', '')
SUPER_ADMIN_ID = int(os.getenv('SUPER_ADMIN_ID', '0'))
VIRUSTOTAL_API_KEY = os.getenv('VIRUSTOTAL_API_KEY', '')
