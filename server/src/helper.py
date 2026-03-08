import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

""" Encryption with Fernet"""


def derive_key(master_password: str, salt: bytes):

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # High iterations make it harder to brute-force
    )

    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt_with_master(data: str, master_password: str, salt: bytes) -> str:
    """Encrypt data using master password"""
    key = derive_key(master_password, salt)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()


def decrypt_with_master(encrypted_data: str,
                        master_password: str,
                        salt: bytes) -> str:
    """Decrypt data using master password"""
    key = derive_key(master_password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()


def verify_password(password: str, salt: bytes, stored_hash: bytes) -> bool:
    """Verify password against stored hash"""
    key = derive_key(password, salt).hex()
    return key == stored_hash
