"""
Zero-Knowledge Encryption Module

Provides client-side encryption capabilities for sensitive data,
ensuring that data is encrypted before being sent to the server.
"""

import os
import base64
from typing import Optional, Union

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("⚠ cryptography package not installed. Install with: pip install cryptography")
    Fernet = None


class ZeroKnowledgeEncryption:
    """
    Zero-knowledge encryption service for client-side data encryption.

    Ensures that sensitive data is encrypted before transmission and
    decrypted only on the client side.
    """

    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize the encryption service.

        Args:
            encryption_key: Optional encryption key. If not provided, a new key is generated.
        """
        if Fernet is None:
            raise ImportError(
                "cryptography package is required. Install with: pip install cryptography"
            )

        if encryption_key is None:
            encryption_key = Fernet.generate_key()

        self.key = encryption_key
        self.cipher_suite = Fernet(self.key)

    @classmethod
    def from_password(cls, password: str, salt: Optional[bytes] = None):
        """
        Create an encryption instance from a password.

        Args:
            password: User password
            salt: Optional salt for key derivation. If not provided, a new salt is generated.

        Returns:
            ZeroKnowledgeEncryption instance
        """
        if salt is None:
            salt = os.urandom(16)

        # Derive key from password
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

        instance = cls(encryption_key=key)
        instance.salt = salt

        return instance

    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data.

        Args:
            data: Data to encrypt (string or bytes)

        Returns:
            Encrypted data as bytes
        """
        if isinstance(data, str):
            data = data.encode('utf-8')

        return self.cipher_suite.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> str:
        """
        Decrypt data.

        Args:
            encrypted_data: Encrypted data as bytes

        Returns:
            Decrypted data as string
        """
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode('utf-8')

    def decrypt_to_bytes(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data and return as bytes.

        Args:
            encrypted_data: Encrypted data as bytes

        Returns:
            Decrypted data as bytes
        """
        return self.cipher_suite.decrypt(encrypted_data)

    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt

        Returns:
            Dictionary with specified fields encrypted
        """
        encrypted_data = data.copy()

        for field in fields_to_encrypt:
            if field in encrypted_data:
                value = str(encrypted_data[field])
                encrypted_value = self.encrypt(value)
                encrypted_data[field] = base64.b64encode(encrypted_value).decode('utf-8')

        return encrypted_data

    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt

        Returns:
            Dictionary with specified fields decrypted
        """
        decrypted_data = data.copy()

        for field in fields_to_decrypt:
            if field in decrypted_data:
                encrypted_value = base64.b64decode(decrypted_data[field])
                decrypted_value = self.decrypt(encrypted_value)
                decrypted_data[field] = decrypted_value

        return decrypted_data

    def get_key(self) -> bytes:
        """
        Get the encryption key.

        Returns:
            Encryption key as bytes
        """
        return self.key

    def get_key_string(self) -> str:
        """
        Get the encryption key as a base64-encoded string.

        Returns:
            Encryption key as string
        """
        return base64.b64encode(self.key).decode('utf-8')

    @classmethod
    def from_key_string(cls, key_string: str):
        """
        Create an encryption instance from a base64-encoded key string.

        Args:
            key_string: Base64-encoded encryption key

        Returns:
            ZeroKnowledgeEncryption instance
        """
        key = base64.b64decode(key_string.encode('utf-8'))
        return cls(encryption_key=key)


class FieldLevelEncryption:
    """
    Provides field-level encryption for database models and API payloads.
    """

    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize field-level encryption.

        Args:
            master_key: Master encryption key
        """
        self.crypto = ZeroKnowledgeEncryption(encryption_key=master_key)

    def encrypt_field(self, value: str, field_name: str) -> str:
        """
        Encrypt a single field value.

        Args:
            value: Value to encrypt
            field_name: Name of the field (used for logging/audit)

        Returns:
            Encrypted value as base64 string
        """
        encrypted = self.crypto.encrypt(value)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_field(self, encrypted_value: str, field_name: str) -> str:
        """
        Decrypt a single field value.

        Args:
            encrypted_value: Encrypted value as base64 string
            field_name: Name of the field (used for logging/audit)

        Returns:
            Decrypted value
        """
        encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
        return self.crypto.decrypt(encrypted_bytes)

    def encrypt_sensitive_data(self, data: dict) -> dict:
        """
        Automatically encrypt sensitive fields in a dictionary.

        Args:
            data: Dictionary containing data

        Returns:
            Dictionary with sensitive fields encrypted
        """
        # Define fields that should always be encrypted
        sensitive_fields = [
            'ssn', 'social_security_number',
            'tax_id', 'ein',
            'bank_account', 'account_number',
            'credit_card', 'card_number',
            'password', 'secret',
            'api_key', 'token',
            'private_key'
        ]

        encrypted_data = data.copy()

        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt_field(
                    str(encrypted_data[field]),
                    field
                )

        return encrypted_data

    def decrypt_sensitive_data(self, data: dict) -> dict:
        """
        Automatically decrypt sensitive fields in a dictionary.

        Args:
            data: Dictionary containing encrypted data

        Returns:
            Dictionary with sensitive fields decrypted
        """
        sensitive_fields = [
            'ssn', 'social_security_number',
            'tax_id', 'ein',
            'bank_account', 'account_number',
            'credit_card', 'card_number',
            'password', 'secret',
            'api_key', 'token',
            'private_key'
        ]

        decrypted_data = data.copy()

        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt_field(
                        decrypted_data[field],
                        field
                    )
                except Exception:
                    # Field might not be encrypted, leave as is
                    pass

        return decrypted_data


def generate_encryption_key() -> str:
    """
    Generate a new encryption key.

    Returns:
        Base64-encoded encryption key
    """
    key = Fernet.generate_key()
    return base64.b64encode(key).decode('utf-8')


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """
    Hash a password using PBKDF2.

    Args:
        password: Password to hash
        salt: Optional salt. If not provided, a new salt is generated.

    Returns:
        Tuple of (hashed_password, salt)
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )

    hashed = kdf.derive(password.encode())

    return (
        base64.b64encode(hashed).decode('utf-8'),
        base64.b64encode(salt).decode('utf-8')
    )


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Password to verify
        hashed_password: Base64-encoded hashed password
        salt: Base64-encoded salt

    Returns:
        True if password matches, False otherwise
    """
    salt_bytes = base64.b64decode(salt.encode('utf-8'))
    hashed_bytes = base64.b64decode(hashed_password.encode('utf-8'))

    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=100000,
        backend=default_backend()
    )

    try:
        kdf.verify(password.encode(), hashed_bytes)
        return True
    except Exception:
        return False
