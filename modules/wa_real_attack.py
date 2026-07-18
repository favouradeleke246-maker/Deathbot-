"""
Real WhatsApp attack module – sends messages via Selenium (headless).
No GUI dependencies – runs on Railway without DISPLAY.
"""
import re
from modules.utils import logger

class WaRealAttack:
    @staticmethod
    def send_message(phone, message):
        """
        Send a WhatsApp message using Selenium (via WaSeleniumSender).
        This method is called from orchestrator, which has the sender instance.
        """
        # This is a placeholder – the actual sending is done by orchestrator.wa_sender
        # We keep this for compatibility, but the real method is in orchestrator.
        return {'success': False, 'output': 'Use /wa_send via orchestrator (Selenium).'}

    @staticmethod
    def send_image(phone, image_path, caption=''):
        return {'success': False, 'output': 'Image sending not implemented in headless mode.'}

    @staticmethod
    def call_number(phone):
        # This can be done via webbrowser – but webbrowser also needs DISPLAY.
        # We'll use a simple HTTP request to simulate.
        import requests
        try:
            # Open WhatsApp call link (no display needed)
            url = f'https://wa.me/{phone}?call=1'
            # Just return the link – user can click it.
            return {'success': True, 'output': f'WhatsApp call link: {url}'}
        except Exception as e:
            return {'success': False, 'output': str(e)}
