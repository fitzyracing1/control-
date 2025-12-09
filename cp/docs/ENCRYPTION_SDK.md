# Banking Encryption SDK

A comprehensive cryptographic SDK for secure banking operations, providing enterprise-grade encryption, key management, and password security.

## Overview

The Banking Encryption SDK is a production-ready cryptographic library designed specifically for financial applications. It provides:

- **AES Encryption**: Support for both GCM (authenticated) and CBC modes
- **Key Management**: Secure key generation, storage, and rotation with policies
- **Password Security**: PBKDF2 hashing with configurable policies and strength checking
- **Type Safety**: Full type hints for better IDE support and code quality
- **Extensible Design**: Abstract base classes for custom implementations

## Installation

```python
from src.sdk import (
    EncryptionSDK,
    AESCipher,
    KeyManager,
    PasswordManager,
    AESMode,
    KeyRotationPolicy,
)
```

## Quick Start

### Basic Encryption

```python
from src.sdk import EncryptionSDK

# Initialize SDK
sdk = EncryptionSDK()

# Generate a key
key = sdk.generate_key()

# Encrypt data
plaintext = "Sensitive financial data"
result = sdk.encrypt_aes_gcm(plaintext, key)

# Decrypt data
decrypted = sdk.decrypt_aes_gcm(
    result.ciphertext,
    key,
    result.iv,
    result.tag
)

print(f"Original: {plaintext}")
print(f"Decrypted: {decrypted.plaintext}")
```

### Password Management

```python
from src.sdk import PasswordManager, PasswordPolicy

# Create password manager with custom policy
policy = PasswordPolicy(
    min_length=16,
    require_special=True,
    max_age_days=90,
)
pwd_manager = PasswordManager(policy)

# Hash password
hashed, salt = pwd_manager.hash_password("MySecurePassword123!")

# Verify password
is_valid = pwd_manager.verify_password("MySecurePassword123!", hashed, salt)

# Validate against policy
is_compliant, errors = pwd_manager.validate_password("WeakPassword")
# Returns (False, ["Password must be at least 16 characters long", ...])

# Check strength
strength = pwd_manager.check_strength("MySecurePassword123!")
# Returns: PasswordStrength.VERY_STRONG

# Generate secure password
generated = pwd_manager.generate_password(length=20)
```

### Key Management

```python
from src.sdk import KeyManager, KeyRotationPolicy

# Create key manager
key_mgr = KeyManager()

# Generate key with rotation policy
key_id = key_mgr.generate_key(
    key_size=32,
    rotation_policy=KeyRotationPolicy.MONTHLY,
    tags={"env": "production", "app": "payments"}
)

# Retrieve key
key = key_mgr.get_key(key_id)

# Check rotation status
needs_rotation = key_mgr.check_rotation_needed()

# Rotate key
new_key_id = key_mgr.rotate_key(key_id)

# List keys by tag
payment_keys = key_mgr.list_keys_by_tag("app", "payments")
```

### Advanced AES Configuration

```python
from src.sdk import AESCipher, AESConfig, AESMode

# Configure GCM mode (authenticated encryption)
config = AESConfig(mode=AESMode.GCM)
cipher = AESCipher(config)

sdk = EncryptionSDK()
key = sdk.generate_key()

# Encrypt
result = cipher.encrypt("Payment data", key)

# Decrypt with authentication verification
decrypted = cipher.decrypt(result, key)
print(f"Verified: {decrypted.verified}")
```

## Components

### EncryptionSDK

Main SDK class providing core cryptographic operations.

**Key Methods:**
- `generate_key(size)` - Generate random encryption key
- `generate_iv(size)` - Generate random initialization vector
- `generate_salt(size)` - Generate random salt
- `derive_key(password, salt)` - Derive key from password
- `encrypt_aes_gcm(plaintext, key)` - Encrypt with GCM mode
- `decrypt_aes_gcm(ciphertext, key, iv, tag)` - Decrypt GCM
- `encrypt_aes_cbc(plaintext, key)` - Encrypt with CBC mode
- `decrypt_aes_cbc(ciphertext, key, iv)` - Decrypt CBC
- `hash_password(password, salt)` - Hash password
- `verify_password(password, hashed, salt)` - Verify password

### AESCipher

Specialized wrapper for AES encryption with support for multiple modes.

**Features:**
- Automatic IV generation
- Authentication tag handling (GCM)
- PKCS7 padding (CBC)
- Mode switching via configuration

### KeyManager

Enterprise-grade key management with rotation policies.

**Features:**
- Secure key generation and storage
- Metadata tracking (creation time, algorithm, rotation status)
- Key rotation with policy enforcement
- Tag-based key grouping
- Soft deletion (deactivation)
- Key rotation status checks

### PasswordManager

Comprehensive password security management.

**Features:**
- PBKDF2-SHA256 hashing with configurable iterations
- Policy-based validation
- Strength checking (5 levels)
- Shannon entropy calculation
- Secure password generation
- Salt management

## Configuration

### CipherConfig

```python
from src.sdk import EncryptionSDK, CipherConfig, EncryptionAlgorithm

config = CipherConfig(
    algorithm=EncryptionAlgorithm.AES_256_GCM,
    key_size=32,  # bytes
    iv_size=16,   # bytes
    tag_size=128, # bits
)
sdk = EncryptionSDK(cipher_config=config)
```

### KeyDerivationConfig

```python
from src.sdk import EncryptionSDK, KeyDerivationConfig, KeyDerivationAlgorithm

config = KeyDerivationConfig(
    algorithm=KeyDerivationAlgorithm.PBKDF2,
    iterations=100000,
    salt_length=16,
    hash_algorithm="SHA256",
    derived_key_length=32,
)
sdk = EncryptionSDK(kdf_config=config)
```

### PasswordPolicy

```python
from src.sdk import PasswordManager, PasswordPolicy

policy = PasswordPolicy(
    min_length=16,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    special_characters="!@#$%^&*()-_=+[]{}|;:,.<>?",
    max_age_days=90,
    min_entropy_bits=50.0,
)
pwd_manager = PasswordManager(policy)
```

## Data Structures

### EncryptionResult

Returned by encryption operations:

```python
@dataclass
class EncryptionResult:
    ciphertext: bytes      # Encrypted data
    iv: bytes              # Initialization vector
    tag: Optional[bytes]   # Authentication tag (GCM only)
    salt: Optional[bytes]  # Salt (key derivation)
    algorithm: str         # Used algorithm name
    
    # Convert to hex strings for storage/transmission
    def to_dict() -> Dict[str, str]
```

### DecryptionResult

Returned by decryption operations:

```python
@dataclass
class DecryptionResult:
    plaintext: str         # Decrypted data
    algorithm: str         # Used algorithm name
    verified: bool         # Authentication status
```

### KeyMetadata

Metadata for managed keys:

```python
@dataclass
class KeyMetadata:
    key_id: str                         # Unique key ID
    created_at: datetime                # Creation timestamp
    algorithm: str                      # Encryption algorithm
    key_size: int                       # Key size in bytes
    rotation_policy: KeyRotationPolicy  # Rotation policy
    last_rotated: Optional[datetime]    # Last rotation time
    next_rotation: Optional[datetime]   # Scheduled rotation
    active: bool                        # Active status
    tags: Dict[str, str]                # Custom tags
```

## Security Considerations

### Password Hashing

- Algorithm: PBKDF2-SHA256
- Iterations: 100,000 (configurable)
- Salt: 16 bytes random
- Derived key: 32 bytes (256 bits)

### AES Encryption

**GCM Mode:**
- Provides authenticated encryption
- Includes authentication tag
- Detects tampering
- **Recommended for most use cases**

**CBC Mode:**
- Traditional block cipher mode
- Requires separate MAC for authentication
- PKCS7 padding applied automatically

### Key Management

- Keys stored in-memory only (no persistence by default)
- Key metadata can be exported for recovery
- Rotation policies prevent key aging
- Deactivation supports key revocation

## Error Handling

```python
from cryptography.exceptions import InvalidTag

try:
    decrypted = sdk.decrypt_aes_gcm(ciphertext, key, iv, tag)
except InvalidTag:
    print("Authentication failed - data may be tampered")
except ValueError as e:
    print(f"Invalid parameters: {e}")
```

## Performance

Benchmarks (approximate, varies by system):

| Operation | Time |
|-----------|------|
| Key generation (256-bit) | < 1 ms |
| Password hashing | ~100 ms |
| AES-256 encryption (1KB) | < 1 ms |
| AES-256 decryption (1KB) | < 1 ms |

## Integration with Banking App

```python
# In src/security/auth.py or user registration
from src.sdk import PasswordManager

class UserRegistration:
    def __init__(self):
        self.pwd_manager = PasswordManager()
    
    def register_user(self, username: str, password: str):
        # Validate password
        is_valid, errors = self.pwd_manager.validate_password(password)
        if not is_valid:
            raise ValueError(f"Password policy violation: {errors}")
        
        # Hash password
        hashed, salt = self.pwd_manager.hash_password(password)
        
        # Store user with hashed password and salt
        return User(username=username, password_hash=hashed, password_salt=salt)
```

## Testing

Run the test suite:

```bash
python -m pytest tests/test_encryption_sdk.py -v
```

## License

MIT License - See LICENSE file for details
