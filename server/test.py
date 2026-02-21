import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet


def derive_key(master_password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # High iterations make it harder to brute-force
    )

    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


my_salt = b'\x00' * 16
""" OR THE BELOW CAN BE USED
    import os
    import secrets

# Method A: Using secrets (Recommended for Python 3.6+)
    salt = secrets.token_bytes(16) 

# Method B: Using os.urandom
    salt = os.urandom(16)
"""

FERNET_KEY = derive_key("test", my_salt)
cipher_suite = Fernet(FERNET_KEY)


def encrypt_password(plain_text: str):
    return cipher_suite.encrypt(plain_text.encode()).decode()


def decrypt_password(encrypted_text: str):
    return cipher_suite.decrypt(encrypted_text.encode()).decode()


raw_pass = "TestTrial1234"

encrypted = encrypt_password(raw_pass)
print(f"Encrypted = {encrypted}")

# Pass the ENCRYPTED string to the decryptor
decrypted = decrypt_password(encrypted)
print(f"Decrypted = {decrypted}")
