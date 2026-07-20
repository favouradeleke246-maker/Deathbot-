import os
import json
import requests
from modules.tiktok_real_attack import TikTokRealAttack
from modules.osint import OSINTEngine
from modules.utils import logger
from config import TIKTOK_SESSION

class TikTokAttackChain:
    def __init__(self):
        self.real = TikTokRealAttack(TIKTOK_SESSION) if TIKTOK_SESSION else None
        self.osint = OSINTEngine()
        self.target = None
        self.info = {}
        self.video_id = None
        self.comment_text = None

    def prep(self, username, video_id=None):
        self.target = username
        self.video_id = video_id
        results = {}

        results['step1'] = {'session_valid': bool(TIKTOK_SESSION)}
        osint_data = self.osint.scan_username(username)
        if osint_data.get('tookie') or osint_data.get('sherlock'):
            results['step2'] = {'profile_found': True, 'data': osint_data}
        else:
            results['step2'] = {'profile_found': False}

        if self.real:
            try:
                check = self.real.follow_target(username)
                results['step3'] = {'session_active': check.get('success', False)}
            except:
                results['step3'] = {'session_active': False}
        else:
            results['step3'] = {'session_active': False}

        results['step4'] = {'comment_ready': True, 'suggested_comment': "Check out this amazing content!"}
        if video_id:
            results['step5'] = {'video_targeted': True}
        else:
            results['step5'] = {'video_targeted': False}

        results['step6'] = {'summary': 'Recon complete. Ready for actions.'}
        self.info = results
        return results

    def confirm_summary(self):
        summary = f"🎯 **TikTok Attack Chain – @{self.target}**\n\n"
        for step, data in self.info.items():
            if isinstance(data, dict):
                for k, v in data.items():
                    summary += f"- {k}: {v}\n"
            else:
                summary += f"- {step}: {data}\n"
        return summary

    def execute(self):
        if not self.real:
            return {'error': 'TIKTOK_SESSION not set. Cannot execute actions.'}
        actions = {}

        actions['follow'] = self.real.follow_target(self.target)

        if self.video_id:
            comment = self.info.get('step4', {}).get('suggested_comment', 'Nice video!')
            actions['comment'] = self.real.post_comment(self.video_id, comment)
        else:
            actions['comment'] = {'success': False, 'output': 'No video_id provided'}

        actions['reset'] = {'success': False, 'output': 'Email not available'}
        actions['delete'] = {'success': False, 'output': 'user_id not available'}

        return actions
