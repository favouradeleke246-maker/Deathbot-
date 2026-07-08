import os

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
DATABASE_URL = os.getenv('DATABASE_URL', '')
TIKTOK_SESSION = os.getenv('TIKTOK_SESSION', '')
SMS_GATEWAY_API_KEY = os.getenv('SMS_GATEWAY_API_KEY', '')
SMS_GATEWAY_URL = os.getenv('SMS_GATEWAY_URL', 'https://api.smsgateway.com/send')
PROXY_LIST = os.getenv('PROXY_LIST', '').split(',') if os.getenv('PROXY_LIST') else []
PLUGIN_DIR = 'modules/plugins'

# NEW: Timeout for all operations (in seconds)
PROCESSING_TIMEOUT = int(os.getenv('PROCESSING_TIMEOUT', '120'))
