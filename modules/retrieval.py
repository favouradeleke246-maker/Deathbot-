from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import re
import json
import time
from modules.utils import random_proxy, random_user_agent, logger

class ProfileRetriever:
    def __init__(self, headless=True):
        options = Options()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--user-agent={random_user_agent()}')
        proxy = random_proxy()
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        self.driver = webdriver.Chrome(options=options)

    def get_tiktok_profile(self, username):
        url = f'https://www.tiktok.com/@{username}'
        try:
            self.driver.get(url)
            time.sleep(3)
            html = self.driver.page_source
            match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                user = data.get('UserModule', {}).get('users', {}).get(username, {})
                if user:
                    return {
                        'username': username,
                        'nickname': user.get('nickname'),
                        'bio': user.get('signature'),
                        'followers': user.get('followerCount'),
                        'following': user.get('followingCount'),
                        'verified': user.get('verified'),
                        'avatar': user.get('avatarMedium')
                    }
            # Fallback
            try:
                nickname = self.driver.find_element(By.CSS_SELECTOR, 'h2[data-e2e="user-nickname"]').text
                bio = self.driver.find_element(By.CSS_SELECTOR, 'span[data-e2e="user-bio"]').text
                followers = self.driver.find_element(By.CSS_SELECTOR, 'strong[data-e2e="followers-count"]').text
                return {'username': username, 'nickname': nickname, 'bio': bio, 'followers': followers}
            except:
                pass
        except Exception as e:
            logger.error(f"TikTok scraping failed: {e}")
        return None

    def close(self):
        if self.driver:
            self.driver.quit()
