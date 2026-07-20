import os
import json
import requests
from modules.social_media import SocialMedia
from modules.utils import logger

class XAttackChain:
    def __init__(self):
        self.social = SocialMedia()
        self.target = None
        self.info = {}

    def prep(self, username):
        self.target = username
        results = {}

        tweets = self.social.get_twitter_profile(username)
        results['step1'] = {'tweets_found': len(tweets.get('tweets', []))}
        results['step2'] = {'profile_exists': tweets.get('success', False)}

        if tweets.get('success'):
            results['step3'] = {'recent_tweet': tweets['tweets'][0] if tweets['tweets'] else 'No tweets'}

        results['step4'] = {'dm_ready': True, 'suggested_dm': "Hey, I noticed your tweet! Check this out: http://phishing.link"}
        results['step5'] = {'summary': 'Recon complete. Target active.'}
        self.info = results
        return results

    def confirm_summary(self):
        summary = f"🐦 **X (Twitter) Attack Chain – @{self.target}**\n\n"
        for step, data in self.info.items():
            if isinstance(data, dict):
                for k, v in data.items():
                    summary += f"- {k}: {v}\n"
            else:
                summary += f"- {step}: {data}\n"
        return summary

    def execute(self):
        actions = {}
        actions['send_dm'] = {'success': True, 'output': 'DM sent (simulated)'}
        actions['follow'] = {'success': True, 'output': 'Followed (simulated)'}
        actions['retweet'] = {'success': True, 'output': 'Retweeted (simulated)'}
        return actions
