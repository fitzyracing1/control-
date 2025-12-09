"""AES Cipher wrapper for the Encryption SDK."""

from enum import Enum
from typing import Optional
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from src.sdk.encryption_sdk import EncryptionResult, DecryptionResult, CipherConfig


class AESMode(Enum):
    """AES encryption modes."""
    GCM = "GCM"
    CBC = "CBC"


@dataclass
class AESConfig(CipherConfig):
    """Configuration specific to AES cipher."""
    mode: AESMode = AESMode.GCM


class AESCipher:
    """
    Specialized AES cipher for encryption and decryption.
    
    Supports both GCM (Galois/Counter Mode) for authenticated encryption
    and CBC (Cipher Block Chaining) for traditional block encryption.
    """
    
    def __init__(self, config: Optional[AESConfig] = None):
        """
        Initialize AES Cipher.
        
        Args:
            config: AES-specific configuration
        """
        self.config = config or AESConfig()
        self.backend = default_backend()
    
    def encrypt(self, plaintext: str, key: bytes) -> EncryptionResult:
        """
        Encrypt plaintext using configured AES mode.
        
        Args:
            plaintext: Data to encrypt
            key: Encryption key (must be 32 bytes for AES-256)
            
        Returns:
            EncryptionResult with ciphertext and IV
        """
        if self.config.mode == AESMode.GCM:
            return self._encrypt_gcm(plaintext, key)
        elif self.config.mode == AESMode.CBC:
            return self._encrypt_cbc(plaintext, key)
        else:
            raise ValueError(f"Unsupported AES mode: {self.config.mode}")
    
    def decrypt(self, result: EncryptionResult, key: bytes) -> DecryptionResult:
        """
        Decrypt ciphertext using configured AES mode.
        
        Args:
            result: Encryption result containing ciphertext, IV, and tag
            key: Decryption key
            
        Returns:
            DecryptionResult with plaintext
        """
        if self.config.mode == AESMode.GCM:
            if not result.tag:
                raise ValueError("GCM mode requires authentication tag")
            return self._decrypt_gcm(result.ciphertext, key, result.iv, result.tag)
        elif self.config.mode == AESMode.CBC:
            return self._decrypt_cbc(result.ciphertext, key, result.iv)
        else:
            raise ValueError(f"Unsupported AES mode: {self.config.mode}")
    
    def _encrypt_gcm(self, plaintext: str, key: bytes) -> EncryptionResult:
        """Internal GCM encryption."""
        from src.sdk.encryption_sdk import EncryptionSDK
        sdk = EncryptionSDK(cipher_config=self.config)
        return sdk.encrypt_aes_gcm(plaintext, key)
    
    def _decrypt_gcm(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
    ) -> DecryptionResult:
        """Internal GCM decryption."""
        from src.sdk.encryption_sdk import EncryptionSDK
        sdk = EncryptionSDK(cipher_config=self.config)
        return sdk.decrypt_aes_gcm(ciphertext, key, iv, tag)
    
    def _encrypt_cbc(self, plaintext: str, key: bytes) -> EncryptionResult:
        """Internal CBC encryption."""
        from src.sdk.encryption_sdk import EncryptionSDK
        sdk = EncryptionSDK(cipher_config=self.config)
        return sdk.encrypt_aes_cbc(plaintext, key)
    
    def _decrypt_cbc(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
    ) -> DecryptionResult:
        """Internal CBC decryption."""
        from src.sdk.encryption_sdk import EncryptionSDK
        sdk = EncryptionSDK(cipher_config=self.config)
        return sdk.decrypt_aes_cbc(ciphertext, key, iv)
