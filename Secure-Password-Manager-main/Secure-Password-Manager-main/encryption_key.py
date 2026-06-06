import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionManager:
    def __init__(self):
        self.fernet = None

    def initialize(self, master_password):
        # We use a hardcoded salt for simplicity in this project.
        # In production, this should be random and stored in the DB.
        salt = b'my_static_application_salt_123' 
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
        self.fernet = Fernet(key)

    def encrypt(self, data):
        if not self.fernet:
            raise ValueError("Encryption not initialized! Log in first.")
        return self.fernet.encrypt(data)

    def decrypt(self, data):
        if not self.fernet:
            raise ValueError("Encryption not initialized! Log in first.")
        return self.fernet.decrypt(data)

# Create a single global instance
cipher = EncryptionManager()