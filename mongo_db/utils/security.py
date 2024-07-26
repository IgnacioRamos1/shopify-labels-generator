import os
import base64
from cryptography.fernet import Fernet

if 'AWS_EXECUTION_ENV' in os.environ:
    from utils.utils import get_parameter
    key = get_parameter('secret_key')
else:
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv('SECRET_KEY')

if key:
    key = base64.urlsafe_b64decode(key)

class TokenEncryptor:
    def __init__(self, key):
        self._key = key
        self.fernet = Fernet(self._key)

    def encrypt_token(self, token):
        return self.fernet.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token):
        return self.fernet.decrypt(encrypted_token.encode()).decode()

    @property
    def key(self):
        return self._key

encryptor = TokenEncryptor(key)
