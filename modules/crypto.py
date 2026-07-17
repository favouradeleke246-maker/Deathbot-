from cryptography.fernet import Fernet
import os

KEY = os.getenv('ENCRYPTION_KEY')
if not KEY:
    KEY = Fernet.generate_key().decode()
cipher = Fernet(KEY.encode())

def encrypt(data):
    return cipher.encrypt(data.encode()).decode()

def decrypt(data):
    return cipher.decrypt(data.encode()).decode()
