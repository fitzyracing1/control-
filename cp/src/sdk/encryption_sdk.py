"""Core Encryption SDK - Main interface for cryptographic operations."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, Dict, Any
import secrets
from abc import ABC, abstractmethod

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class KeyDerivationAlgorithm(Enum):
    """Supported key derivation functions."""
    PBKDF2 = "PBKDF2"
    HKDF = "HKDF"


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "AES-256-GCM"
    AES_256_CBC = "AES-256-CBC"


@dataclass
class KeyDerivationConfig:
    """Configuration for key derivation."""
    algorithm: KeyDerivationAlgorithm = KeyDerivationAlgorithm.PBKDF2
    iterations: int = 100000
    salt_length: int = 16
    hash_algorithm: str = "SHA256"
    derived_key_length: int = 32


@dataclass
class CipherConfig:
    """Configuration for cipher operations."""
    algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_size: int = 32  # 256 bits
    iv_size: int = 16
    tag_size: int = 128  # bits
    backend: Any = field(default_factory=default_backend)


@dataclass
class EncryptionResult:
    """Result of encryption operation."""
    ciphertext: bytes
    iv: bytes
    tag: Optional[bytes] = None
    salt: Optional[bytes] = None
    algorithm: str = "AES-256-GCM"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert result to dictionary with hex-encoded values."""
        result = {
            "ciphertext": self.ciphertext.hex(),
            "iv": self.iv.hex(),
            "algorithm": self.algorithm,
        }
        if self.tag:
            result["tag"] = self.tag.hex()
        if self.salt:
            result["salt"] = self.salt.hex()
        return result


@dataclass
class DecryptionResult:
    """Result of decryption operation."""
    plaintext: str
    algorithm: str = "AES-256-GCM"
    verified: bool = True


class BaseEncryptor(ABC):
    """Abstract base class for encryptors."""
    
    @abstractmethod
    def encrypt(self, plaintext: str, key: bytes) -> EncryptionResult:
        """Encrypt plaintext."""
        pass
    
    @abstractmethod
    def decrypt(self, result: EncryptionResult, key: bytes) -> DecryptionResult:
        """Decrypt ciphertext."""
        pass


class EncryptionSDK:
    """
    Comprehensive Encryption SDK for secure banking operations.
    
    Provides a unified interface for:
    - AES encryption/decryption (GCM and CBC modes)
    - Password hashing and verification
    - Key generation and management
    - Secure random number generation
    """
    
    def __init__(
        self,
        cipher_config: Optional[CipherConfig] = None,
        kdf_config: Optional[KeyDerivationConfig] = None,
    ):
        """
        Initialize Encryption SDK.
        
        Args:
            cipher_config: Configuration for cipher operations
            kdf_config: Configuration for key derivation
        """
        self.cipher_config = cipher_config or CipherConfig()
        self.kdf_config = kdf_config or KeyDerivationConfig()
        self.backend = default_backend()
    
    def generate_key(self, size: Optional[int] = None) -> bytes:
        """
        Generate a cryptographically secure random key.
        
        Args:
            size: Key size in bytes (defaults to config.key_size)
            
        Returns:
            Random key bytes
        """
        size = size or self.cipher_config.key_size
        return secrets.token_bytes(size)
    
    def generate_iv(self, size: Optional[int] = None) -> bytes:
        """
        Generate a cryptographically secure random IV.
        
        Args:
            size: IV size in bytes (defaults to config.iv_size)
            
        Returns:
            Random IV bytes
        """
        size = size or self.cipher_config.iv_size
        return secrets.token_bytes(size)
    
    def generate_salt(self, size: Optional[int] = None) -> bytes:
        """
        Generate a cryptographically secure random salt.
        
        Args:
            size: Salt size in bytes (defaults to config.salt_length)
            
        Returns:
            Random salt bytes
        """
        size = size or self.kdf_config.salt_length
        return secrets.token_bytes(size)
    
    def derive_key(
        self,
        password: str,
        salt: Optional[bytes] = None,
    ) -> Tuple[bytes, bytes]:
        """
        Derive a key from a password using configured KDF.
        
        Args:
            password: Password to derive key from
            salt: Salt for derivation (generated if not provided)
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = self.generate_salt()
        
        if self.kdf_config.algorithm == KeyDerivationAlgorithm.PBKDF2:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.kdf_config.derived_key_length,
                salt=salt,
                iterations=self.kdf_config.iterations,
                backend=self.backend,
            )
            derived_key = kdf.derive(password.encode())
            return derived_key, salt
        else:
            raise NotImplementedError(
                f"Key derivation algorithm {self.kdf_config.algorithm} not yet supported"
            )
    
    def encrypt_aes_gcm(
        self,
        plaintext: str,
        key: bytes,
    ) -> EncryptionResult:
        """
        Encrypt plaintext using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            key: 32-byte encryption key
            
        Returns:
            EncryptionResult containing ciphertext, IV, and tag
        """
        if len(key) != self.cipher_config.key_size:
            raise ValueError(
                f"Key must be {self.cipher_config.key_size} bytes, "
                f"got {len(key)}"
            )
        
        iv = self.generate_iv()
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv),
            backend=self.backend,
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv=iv,
            tag=encryptor.tag,
            algorithm="AES-256-GCM",
        )
    
    def decrypt_aes_gcm(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
        tag: bytes,
    ) -> DecryptionResult:
        """
        Decrypt ciphertext using AES-256-GCM.
        
        Args:
            ciphertext: Data to decrypt
            key: 32-byte decryption key
            iv: Initialization vector
            tag: Authentication tag
            
        Returns:
            DecryptionResult containing plaintext
            
        Raises:
            cryptography.exceptions.InvalidTag: If authentication fails
        """
        if len(key) != self.cipher_config.key_size:
            raise ValueError(
                f"Key must be {self.cipher_config.key_size} bytes, "
                f"got {len(key)}"
            )
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(iv, tag),
            backend=self.backend,
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return DecryptionResult(
            plaintext=plaintext.decode(),
            algorithm="AES-256-GCM",
            verified=True,
        )
    
    def encrypt_aes_cbc(
        self,
        plaintext: str,
        key: bytes,
    ) -> EncryptionResult:
        """
        Encrypt plaintext using AES-256-CBC.
        
        Args:
            plaintext: Data to encrypt
            key: 32-byte encryption key
            
        Returns:
            EncryptionResult containing ciphertext and IV
        """
        if len(key) != self.cipher_config.key_size:
            raise ValueError(
                f"Key must be {self.cipher_config.key_size} bytes, "
                f"got {len(key)}"
            )
        
        iv = self.generate_iv()
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend,
        )
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        plaintext_bytes = plaintext.encode()
        padding_length = 16 - (len(plaintext_bytes) % 16)
        plaintext_bytes += bytes([padding_length] * padding_length)
        
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        
        return EncryptionResult(
            ciphertext=ciphertext,
            iv=iv,
            algorithm="AES-256-CBC",
        )
    
    def decrypt_aes_cbc(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
    ) -> DecryptionResult:
        """
        Decrypt ciphertext using AES-256-CBC.
        
        Args:
            ciphertext: Data to decrypt
            key: 32-byte decryption key
            iv: Initialization vector
            
        Returns:
            DecryptionResult containing plaintext
        """
        if len(key) != self.cipher_config.key_size:
            raise ValueError(
                f"Key must be {self.cipher_config.key_size} bytes, "
                f"got {len(key)}"
            )
        
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend,
        )
        decryptor = cipher.decryptor()
        plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = plaintext_bytes[-1]
        plaintext_bytes = plaintext_bytes[:-padding_length]
        
        return DecryptionResult(
            plaintext=plaintext_bytes.decode(),
            algorithm="AES-256-CBC",
            verified=True,
        )
    
    def hash_password(
        self,
        password: str,
        salt: Optional[bytes] = None,
    ) -> Tuple[bytes, bytes]:
        """
        Hash a password using PBKDF2.
        
        Args:
            password: Password to hash
            salt: Salt for hashing (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        derived_key, salt = self.derive_key(password, salt)
        return derived_key, salt
    
    def verify_password(
        self,
        password: str,
        hashed: bytes,
        salt: bytes,
    ) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed: Hashed password
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        derived_key, _ = self.derive_key(password, salt)
        return derived_key == hashed
