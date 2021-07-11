
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

import random
import string

try:
    from config import AES_KEY_LENGTH
except ModuleNotFoundError:
    AES_KEY_LENGTH = 32

def random_string(length):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))

def random_aes_key():
    return get_random_bytes(AES_KEY_LENGTH)

def aes_encrypt(key: bytes, data: bytes, cnt):
    return b''

def aes_decrypt(key: bytes, data: bytes, cnt):
    return b''

if __name__ == '__main__':
    print(random_aes_key())