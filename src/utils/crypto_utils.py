"""
Encryption utilities for securing sensitive data at rest
Provides functions to encrypt/decrypt JSON data using Fernet symmetric encryption
"""

import json
import os
import stat
from pathlib import Path

from cryptography.fernet import Fernet


class PacketDataCrypto:
    """Handles encryption and decryption of packet data files"""

    def __init__(self, key_file: str = ".packet_encryption_key"):
        """
        Initialize crypto handler with key management

        Args:
            key_file: Path to encryption key file
        """
        self.key_file = Path(key_file)
        self._ensure_key()

    def _ensure_key(self):
        """Generate or load encryption key"""
        if self.key_file.exists():
            with open(self.key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(self.key)
            # Restrict key file permissions
            os.chmod(self.key_file, stat.S_IRUSR | stat.S_IWUSR)

    def encrypt_data(self, data: dict) -> bytes:
        """
        Encrypt dictionary data

        Args:
            data: Dictionary to encrypt

        Returns:
            Encrypted bytes
        """
        cipher = Fernet(self.key)
        json_str = json.dumps(data)
        return cipher.encrypt(json_str.encode("utf-8"))

    def decrypt_data(self, encrypted_data: bytes) -> dict:
        """
        Decrypt encrypted data

        Args:
            encrypted_data: Encrypted bytes

        Returns:
            Decrypted dictionary
        """
        cipher = Fernet(self.key)
        decrypted_bytes = cipher.decrypt(encrypted_data)
        return json.loads(decrypted_bytes.decode("utf-8"))

    def write_encrypted_file(self, data: dict, file_path: str):
        """
        Write encrypted data to file

        Args:
            data: Dictionary to encrypt and write
            file_path: Path to output file
        """
        encrypted = self.encrypt_data(data)
        with open(file_path, "wb") as f:
            f.write(encrypted)
        # Set file permissions
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)

    def read_encrypted_file(self, file_path: str) -> dict:
        """
        Read and decrypt data from file

        Args:
            file_path: Path to encrypted file

        Returns:
            Decrypted dictionary
        """
        with open(file_path, "rb") as f:
            encrypted = f.read()
        return self.decrypt_data(encrypted)

    def file_exists(self, file_path: str) -> bool:
        """Check if encrypted file exists"""
        return Path(file_path).exists()


# Global crypto instance
_crypto_instance = None


def get_crypto() -> PacketDataCrypto:
    """Get or create global crypto instance"""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = PacketDataCrypto()
    return _crypto_instance
