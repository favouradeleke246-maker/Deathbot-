import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from modules.utils import logger

class WaSeleniumSender:
    def __init__(self, profile_dir='/app/whatsapp-profile'):
        self.profile_dir = profile_dir
        self.driver = None

    def _get_driver(self):
        if self.driver is not None:
            return self.driver

        # Ensure profile directory exists
        os.makedirs(self.profile_dir, exist_ok=True)
        os.makedirs(os.path.join(self.profile_dir, 'Default'), exist_ok=True)

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        options.binary_location = '/usr/bin/google-chrome'
        options.add_argument(f'--user-data-dir={self.profile_dir}')

        # Try system chromedriver
        try:
            service = Service('/usr/local/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Fallback to webdriver-manager
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)

        self.driver.get('https://web.whatsapp.com')
        time.sleep(5)

        # Check if QR code is present (session invalid)
        try:
            qr = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="qrcode"]'))
            )
            logger.info("QR code detected – session expired. You need to scan the QR code once.")
            # We'll keep the session alive – the user will need to scan QR once.
            # For headless, we can't scan, so we raise an error.
            self.driver.quit()
            self.driver = None
            raise RuntimeError("WhatsApp Web session expired. Please run the bot once in non‑headless mode to scan QR, or provide valid profile.")
        except:
            # QR not found – session may be valid
            pass

        # Wait for chat list to load
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]'))
            )
            logger.info("WhatsApp Web session is valid.")
        except Exception as e:
            logger.warning(f"Chat list not loaded within 30s: {e}")
            # Still proceed – sometimes it's slow

        return self.driver

    def send_message(self, phone, message):
        driver = self._get_driver()
        chat_url = f'https://web.whatsapp.com/send?phone={phone}'
        driver.get(chat_url)
        try:
            wait = WebDriverWait(driver, 20)
            # Wait for message input
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
            except Exception:
                return {'success': False, 'output': 'Phone number may not be registered on WhatsApp or profile is invalid.'}
            message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
            message_box.send_keys(message)
            send_button = driver.find_element(By.XPATH, '//button[@data-testid="compose-btn-send"]')
            send_button.click()
            return {'success': True, 'output': f'Message sent to {phone}.'}
        except Exception as e:
            logger.error(f'WhatsApp send error: {e}')
            return {'success': False, 'output': str(e)}

    def send_image(self, phone, image_path, caption=''):
        driver = self._get_driver()
        chat_url = f'https://web.whatsapp.com/send?phone={phone}'
        driver.get(chat_url)
        try:
            wait = WebDriverWait(driver, 20)
            attach_button = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Attach"]')))
            attach_button.click()
            file_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@accept="*/*"]')))
            file_input.send_keys(os.path.abspath(image_path))
            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="compose-btn-send"]')))
            send_button.click()
            return {'success': True, 'output': f'Image sent to {phone}'}
        except Exception as e:
            logger.error(f'WhatsApp image send error: {e}')
            return {'success': False, 'output': str(e)}

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
