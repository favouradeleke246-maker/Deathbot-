import os
import json
import requests
from modules.social_media import SocialMedia
from modules.utils import logger

class InstagramAttackChain:
    def __init__(self):
        self.social = SocialMedia()
        self.target = None
        self.info = {}

    def prep(self, username):
        self.target = username
        results = {}

        profile = self.social.get_instagram_profile(username)
        results['step1'] = {'profile_exists': profile.get('success', False)}

        if profile.get('success'):
            results['step2'] = {'followers': profile.get('followers'), 'posts': profile.get('posts')}
        else:
            results['step2'] = {'error': 'Profile not found'}

        results['step3'] = {'private': False}
        results['step4'] = {'dm_ready': True, 'suggested_dm': "Hi, I'm a fan of your work! Check this out: http://phishing.link"}
        results['step5'] = {'summary': 'Recon complete. Target is reachable.'}
        self.info = results
        return results

    def confirm_summary(self):
        summary = f"📸 **Instagram Attack Chain – @{self.target}**\n\n"
        for step, data in self.info.items():
            if isinstance(data, dict):
                for k, v in data.items():
                    summary += f"- {k}: {v}\n"
            else:
                summary += f"- {step}: {data}\n"
        return summary

    def execute(self):
        actions = {}
        actions['send_dm'] = {'success': True, 'output': 'DM sent (simulated – API not available)'}
        actions['follow'] = {'success': True, 'output': 'Follow request sent (simulated)'}
        actions['like'] = {'success': True, 'output': 'Liked post (simulated)'}
        return actions
