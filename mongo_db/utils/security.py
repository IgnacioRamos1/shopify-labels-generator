import os
from nacl import secret
import binascii


if 'AWS_EXECUTION_ENV' in os.environ:
    from utils.utils import get_parameter
    hex_key = get_parameter('secret_key')

else:
    from dotenv import load_dotenv
    load_dotenv()
    hex_key = os.getenv('SECRET_KEY')


key = binascii.unhexlify(hex_key)

box = secret.SecretBox(key)

def encrypt_string(string):
    encrypted = box.encrypt(string.encode())
    return binascii.hexlify(encrypted).decode()  # Convertir a hexadecimal para almacenar como str

def decrypt_string(encrypted_string_hex):
    encrypted_bytes = binascii.unhexlify(encrypted_string_hex)  # Convertir de hex a bytes
    return box.decrypt(encrypted_bytes).decode()
