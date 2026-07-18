"""
Real WhatsApp attack module – sends message, triggers call.
Uses pywhatkit for quick message sending.
"""
import pywhatkit as kit
import re
from modules.utils import logger

class WaRealAttack:
    @staticmethod
    def send_message(phone, message, wait_time=15, tab_close=True):
        clean_phone = re.sub(r'[^0-9]', '', phone)
        if len(clean_phone) < 10:
            return {'success': False, 'output': 'Invalid phone number.'}
        try:
            kit.sendwhatmsg_instantly(clean_phone, message, wait_time=wait_time, tab_close=tab_close)
            return {'success': True, 'output': f'Message sent to {phone}.'}
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return {'success': False, 'output': f'Error: {str(e)}'}

    @staticmethod
    def send_image(phone, image_path, caption=''):
        try:
            kit.sendwhats_image(phone, image_path, caption, wait_time=15)
            return {'success': True, 'output': f'Image sent to {phone}.'}
        except Exception as e:
            return {'success': False, 'output': f'Image send error: {e}'}

    @staticmethod
    def call_number(phone):
        import webbrowser
        try:
            url = f'https://wa.me/{phone}?call=1'
            webbrowser.open(url)
            return {'success': True, 'output': f'Opened WhatsApp call to {phone} in browser.'}
        except Exception as e:
            return {'success': False, 'output': f'Call error: {e}'}
