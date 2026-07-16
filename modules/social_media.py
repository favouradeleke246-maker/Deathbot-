import requests
from bs4 import BeautifulSoup
import snscrape.modules.twitter as sntwitter
from modules.utils import logger

class SocialMedia:
    @staticmethod
    def get_instagram_profile(username):
        """Scrape public Instagram profile."""
        url = f"https://www.instagram.com/{username}/"
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Simple extraction – could be expanded
                return {'success': True, 'username': username, 'exists': True}
            else:
                return {'success': False, 'error': 'Profile not found'}
        except Exception as e:
            logger.error(f"Instagram scrape failed: {e}")
            return {'success': False, 'error': str(e)}

    @staticmethod
    def get_twitter_profile(username):
        """Retrieve recent tweets using snscrape."""
        try:
            tweets = []
            scraper = sntwitter.TwitterSearchScraper(f'from:{username}')
            for i, tweet in enumerate(scraper.get_items()):
                if i >= 5: break
                tweets.append(tweet.content)
            return {'success': True, 'username': username, 'tweets': tweets}
        except Exception as e:
            logger.error(f"Twitter scrape failed: {e}")
            return {'success': False, 'error': str(e)}
