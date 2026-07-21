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

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--remote-debugging-port=9222')
        options.binary_location = '/usr/bin/google-chrome'
        options.add_argument(f'--user-data-dir={self.profile_dir}')

        # Try system driver first
        try:
            service = Service('/usr/local/bin/chromedriver')
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get('https://web.whatsapp.com')
            logger.info("Chrome launched, waiting for page to load...")
            time.sleep(10)  # initial wait for heavy JS
            logger.info("Using system chromedriver")
        except Exception as e:
            logger.warning(f"System chromedriver failed: {e}")
            # Fallback to webdriver-manager
            try:
                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
                self.driver.get('https://web.whatsapp.com')
                time.sleep(10)
                logger.info("Using webdriver-manager driver")
            except Exception as e2:
                logger.error(f"WebDriverManager also failed: {e2}")
                raise RuntimeError("No ChromeDriver available.")

        # Wait for either QR code or chat list (up to 60s)
        try:
            WebDriverWait(self.driver, 60).until(
                lambda d: d.find_elements(By.XPATH, '//div[@data-testid="qrcode"]') or
                          d.find_elements(By.XPATH, '//div[@data-testid="chat-list"]')
            )
            logger.info("Page loaded (QR or chat list detected).")
        except Exception as e:
            logger.warning(f"Timeout waiting for page elements: {e}")

        # Check if QR code is present
        qr = self.driver.find_elements(By.XPATH, '//div[@data-testid="qrcode"]')
        if qr:
            logger.error("QR code found – session expired.")
            self.driver.quit()
            self.driver = None
            raise RuntimeError("WhatsApp Web session expired. Please re-export fresh cookies.")

        # Wait a bit longer for the chat list to fully render (some profiles take longer)
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="chat-list"]'))
            )
            logger.info("Chat list loaded successfully.")
        except Exception as e:
            logger.warning(f"Chat list not found within 30s: {e}")

        return self.driver

    def send_message(self, phone, message):
        driver = self._get_driver()
        # Remove spaces and ensure country code
        clean_phone = ''.join(filter(str.isdigit, phone))
        if not clean_phone.startswith('234') and not clean_phone.startswith('+'):
            clean_phone = '+234' + clean_phone  # fallback for Nigeria
        chat_url = f'https://web.whatsapp.com/send?phone={clean_phone}'
        driver.get(chat_url)
        logger.info(f"Navigating to chat: {chat_url}")
        try:
            # Wait for the message input box (up to 45 seconds)
            wait = WebDriverWait(driver, 45)
            message_box = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')))
            logger.info("Message box found, typing message...")
            message_box.send_keys(message)
            # Wait for send button and click
            send_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="compose-btn-send"]')))
            send_button.click()
            logger.info("Send button clicked.")
            return {'success': True, 'output': f'Message sent to {phone}.'}
        except Exception as e:
            logger.error(f'WhatsApp send error: {e}')
            # Return debug info
            try:
                page_title = driver.title
                current_url = driver.current_url
                return {'success': False, 'output': f'Failed to send: {str(e)}. Page title: "{page_title}", URL: {current_url}'}
            except:
                return {'success': False, 'output': str(e)}

    def send_image(self, phone, image_path, caption=''):
        driver = self._get_driver()
        clean_phone = ''.join(filter(str.isdigit, phone))
        chat_url = f'https://web.whatsapp.com/send?phone={clean_phone}'
        driver.get(chat_url)
        try:
            wait = WebDriverWait(driver, 30)
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
