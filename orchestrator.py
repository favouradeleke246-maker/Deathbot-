import json
import logging
import threading
from modules.ai_analysis import AIAnalyzer
from modules.osint import OSINTEngine
from modules.analysis import Analyzer
from modules.tiktok_xss_csrf import TikTokXSS_CSRF
from modules.tiktok_idor_delete import TikTokIDORDelete
from modules.tiktok_sms_spoof import TikTokSMSSpoof
from modules.wa_zero_click import WhatsAppZeroClickRCE
from modules.wa_delivery_fingerprint import WaDeliveryFingerprint
from modules.verification import Verify
from modules.utils import db_insert_target, db_get_target, db_update_target_profile, db_log_attack, db_list_targets, db_log_diagnostic
from config import TIKTOK_SESSION, SMS_GATEWAY_API_KEY, SMS_GATEWAY_URL, VIRUSTOTAL_API_KEY, ENABLE_SCHEDULER
from plugins import load_plugins

# New modules (all upgrades)
from modules.advanced_osint import AdvancedOSINT
from modules.advanced_attacks import AdvancedAttacks
from modules.reporting import ReportGenerator
from modules.threat_intel import ThreatIntel
from modules.social_media import SocialMedia
from modules.wizard import Wizard
from modules.admin_manager import AdminManager
from modules.diagnostics import Diagnostics
from modules.scheduler import start_scheduler
from modules.sentiment import SentimentAnalyzer
from modules.phishing import create_tracking_link
from modules.plugin_manager import fetch_plugins, load_plugin
from modules.monitor import monitor_target
from modules.learner import Learner
from modules.defensive import check_api_keys_exposure
from modules.collab import Collaboration
from modules.external import shodan_lookup
from modules.crypto import encrypt, decrypt
from modules.geolocation import get_location
from modules.darkweb import search_breaches
from modules.scoring import calculate_score

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.ai = AIAnalyzer(self)
        self.osint = OSINTEngine()
        self._retriever = None
        self.tiktok_xss = TikTokXSS_CSRF()
        self.tiktok_idor = TikTokIDORDelete(TIKTOK_SESSION, '123456') if TIKTOK_SESSION else None
        self.tiktok_sms = TikTokSMSSpoof(SMS_GATEWAY_API_KEY, SMS_GATEWAY_URL) if SMS_GATEWAY_API_KEY else None
        self.wa_rce = WhatsAppZeroClickRCE()
        self.wa_fp = WaDeliveryFingerprint()
        self.verifier = Verify()
        self.plugins = load_plugins(self)

        # New features
        self.adv_osint = AdvancedOSINT()
        self.adv_attacks = AdvancedAttacks()
        self.report = ReportGenerator()
        self.threat = ThreatIntel()
        self.social = SocialMedia()
        self.wizard = Wizard()
        self.admin = AdminManager()
        self.diagnostics = Diagnostics()
        self.sentiment = SentimentAnalyzer()
        self.collab = Collaboration()
        self.learner = Learner()

        # Start scheduler if enabled
        if ENABLE_SCHEDULER:
            start_scheduler()

    @property
    def retriever(self):
        if self._retriever is None:
            try:
                from modules.retrieval import ProfileRetriever
                self._retriever = ProfileRetriever()
            except Exception as e:
                logger.error(f"ProfileRetriever init failed: {e}")
                self._retriever = None
        return self._retriever

    # ---------- Existing Core Methods ----------
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
        if self.retriever is None:
            return {'error': 'Retrieval module unavailable (Chrome missing).'}
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        if platform.lower() == 'tiktok':
            try:
                profile = self.retriever.get_tiktok_profile(target['identifier'])
                if profile:
                    db_update_target_profile(target_id, profile)
                    return profile
                return {'error': 'Profile retrieval failed'}
            except Exception as e:
                return {'error': f'Scraping error: {str(e)}'}
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
        try:
            rce = self.wa_rce.exploit(phone)
            fp = self.wa_fp.exploit(phone)
            return {'rce': rce, 'fingerprint': fp}
        except Exception as e:
            return {'error': str(e)}

    def verify_target(self, target_id, platform):
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        if platform.lower() == 'whatsapp':
            return self.verifier.check_whatsapp_registration(target['identifier'])
        return {'success': False, 'output': 'Platform not supported'}

    def log_attack(self, target_id, attack_type, result):
        db_log_attack(target_id, attack_type, result)

    def list_targets(self):
        return db_list_targets()

    def social_engineer(self, params):
        target_info = params.get('target_info', '')
        if self.ai and self.ai.ai_manager:
            try:
                prompt = f"Generate a convincing SMS or email to trick a user into clicking a malicious link. Target info: {target_info}. Keep it short and urgent."
                response = self.ai.ai_manager.generate(prompt, max_tokens=100, temperature=0.7)
                return {'success': True, 'output': response}
            except Exception as e:
                return {'success': False, 'output': f'AI generation failed: {e}'}
        else:
            return {
                'success': True,
                'output': f"Hi, this is support. We need to verify your account. Please click: http://phishing.link"
            }

    # ---------- New Upgrade Methods ----------
    def breach_check(self, email):
        return self.adv_osint.email_breach(email)

    def whois_lookup(self, domain):
        return self.adv_osint.whois_lookup(domain)

    def dns_enum(self, domain):
        return self.adv_osint.dns_enum(domain)

    def reverse_image(self, image_url):
        return self.adv_osint.reverse_image_search(image_url)

    def generate_phish(self, email, template='generic'):
        return self.adv_attacks.phishing_email(email, template)

    def credential_stuff(self, username, password_list):
        return self.adv_attacks.credential_stuffing(username, password_list)

    def session_hijack(self, cookie):
        return self.adv_attacks.session_hijacking(cookie)

    def generate_report_pdf(self, target_id):
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        data = {
            'id': target['id'],
            'identifier': target['identifier'],
            'platform': target['platform'],
            'osint': target.get('osint', {}),
            'profile': target.get('profile', {}),
            'created': target.get('created_at')
        }
        return self.report.generate_pdf(data)

    def virustotal_ip(self, ip):
        return self.threat.virustotal_ip(ip, VIRUSTOTAL_API_KEY)

    def nmap_scan(self, host, ports='1-1024'):
        return self.threat.nmap_scan(host, ports)

    def instagram_profile(self, username):
        return self.social.get_instagram_profile(username)

    def twitter_profile(self, username):
        return self.social.get_twitter_profile(username)

    def run_diagnostics(self):
        results = self.diagnostics.run_all()
        for name, result in results.items():
            db_log_diagnostic(name, result.get('status', 'UNKNOWN'), result)
        return results

    def switch_ai_model(self, provider):
        if hasattr(self.ai, 'ai_manager'):
            self.ai.ai_manager.set_active_provider(provider)
            return {'success': True, 'message': f'Switched to {provider}'}
        return {'success': False, 'error': 'AI manager not available'}

    # Upgrade 1: Attack Chaining
    def execute_chain(self, target_id, chain):
        results = []
        for step in chain:
            step_type = step.get('step')
            params = step.get('params', {})
            if step_type == 'osint':
                results.append(self.track(params.get('identifier')))
            elif step_type == 'phish':
                results.append(self.generate_phish(params.get('email'), params.get('template')))
            elif step_type == 'stuff':
                results.append(self.credential_stuff(params.get('username'), params.get('passwords')))
            elif step_type == 'session':
                results.append(self.session_hijack(params.get('cookie')))
            elif step_type == 'social':
                results.append(self.social_engineer(params))
            else:
                results.append({'error': f'Unknown step: {step_type}'})
        return results

    # Upgrade 6: Sentiment
    def sentiment_analysis(self, text):
        return self.sentiment.analyze(text)

    # Upgrade 7: Phishing link shortener
    def create_phishing_link(self, email):
        return create_tracking_link(email)

    # Upgrade 9: Plugin management
    def fetch_plugins(self):
        return fetch_plugins()

    def load_plugin(self, name):
        return load_plugin(name)

    # Upgrade 10: Monitoring
    def start_monitor(self, target_id, chat_id, send_func):
        threading.Thread(target=monitor_target, args=(target_id, chat_id, send_func), daemon=True).start()

    # Upgrade 11: Self‑learning
    def record_outcome(self, target_id, attack, success):
        self.learner.record_outcome(target_id, attack, success)

    def get_best_attack(self, target_id):
        return self.learner.get_best_attack(target_id)

    # Upgrade 12: Defensive
    def defensive_scan(self):
        return check_api_keys_exposure()

    # Upgrade 13: Collaboration
    def share_target(self, target_id, user_id):
        self.collab.share_target(target_id, user_id)

    def unshare_target(self, target_id, user_id):
        self.collab.unshare_target(target_id, user_id)

    # Upgrade 14: External tools
    def shodan_ip(self, ip):
        return shodan_lookup(ip)

    # Upgrade 17: Encryption
    def encrypt_data(self, data):
        return encrypt(data)

    def decrypt_data(self, data):
        return decrypt(data)

    # Upgrade 18: Geolocation
    def geolocate_ip(self, ip):
        return get_location(ip)

    # Upgrade 19: Dark web
    def darkweb_search(self, email):
        return search_breaches(email)

    # Upgrade 20: Scoring
    def score_target(self, target_id):
        target = db_get_target(target_id)
        if not target:
            return {'error': 'Target not found'}
        score = calculate_score(target.get('osint', {}))
        return {'target_id': target_id, 'score': score}
