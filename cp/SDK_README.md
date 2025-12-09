# Banking Encryption SDK - README

A production-grade cryptographic SDK for secure banking operations with comprehensive encryption, key management, and password security features.

## 📋 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Components](#-components)
- [Usage Examples](#-usage-examples)
- [API Reference](#-api-reference)
- [Security](#-security)
- [Testing](#-testing)

## ✨ Features

### Core Cryptography
- **AES-256 Encryption** with GCM (authenticated) and CBC modes
- **PBKDF2-SHA256** password hashing with 100,000 iterations
- **Secure Key Derivation** from passwords
- **Cryptographically Secure Random** generation

### Key Management
- Generate and store encryption keys securely
- Key rotation with configurable policies (Daily, Weekly, Monthly, Yearly)
- Metadata tracking (creation time, algorithm, rotation status)
- Key tagging for organizational purposes
- Soft deletion support (key deactivation)

### Password Security
- Policy-based password validation
- 5-level password strength checking
- Shannon entropy calculation
- Secure password generation
- Password verification with salt

### Enterprise Features
- Full type hints for IDE support
- Comprehensive error handling
- Extensible architecture with abstract base classes
- Zero external dependencies (uses only cryptography)

## 🚀 Installation

The SDK is included in the banking application. Import from the main package:

```python
from src.sdk import (
    EncryptionSDK,
    AESCipher,
    KeyManager,
    PasswordManager,
)
```

## 🎯 Quick Start

### 1. Basic Encryption

```python
from src.sdk import EncryptionSDK

# Initialize SDK
sdk = EncryptionSDK()

# Generate a key
key = sdk.generate_key()  # 256-bit random key

# Encrypt data
plaintext = "Confidential transaction data"
result = sdk.encrypt_aes_gcm(plaintext, key)

# Decrypt
decrypted = sdk.decrypt_aes_gcm(
    result.ciphertext,
    key,
    result.iv,
    result.tag
)
print(decrypted.plaintext)  # "Confidential transaction data"
```

### 2. Password Management

```python
from src.sdk import PasswordManager

pwd_mgr = PasswordManager()

# Hash password
hashed, salt = pwd_mgr.hash_password("UserPassword123!")

# Verify password
is_valid = pwd_mgr.verify_password("UserPassword123!", hashed, salt)  # True
is_valid = pwd_mgr.verify_password("WrongPassword", hashed, salt)      # False

# Validate against policy
is_compliant, errors = pwd_mgr.validate_password("weak")
# Returns: (False, ["Password must be at least 12 characters long", ...])

# Check strength
strength = pwd_mgr.check_strength("MySecurePassword123!")
# Returns: PasswordStrength.STRONG
```

### 3. Key Management

```python
from src.sdk import KeyManager, KeyRotationPolicy

mgr = KeyManager()

# Generate key with rotation policy
key_id = mgr.generate_key(
    rotation_policy=KeyRotationPolicy.MONTHLY,
    tags={"service": "payments"}
)

# Retrieve key
key = mgr.get_key(key_id)

# Rotate key
new_key_id = mgr.rotate_key(key_id)
# Old key is automatically deactivated

# List keys by tag
payment_keys = mgr.list_keys_by_tag("service", "payments")
```

## 📦 Components

### EncryptionSDK

Main SDK class providing all core cryptographic operations.

**Encryption Methods:**
```python
sdk = EncryptionSDK()

# AES-256-GCM (authenticated encryption)
result = sdk.encrypt_aes_gcm(plaintext: str, key: bytes) -> EncryptionResult
plaintext = sdk.decrypt_aes_gcm(ciphertext, key, iv, tag) -> DecryptionResult

# AES-256-CBC (traditional block cipher)
result = sdk.encrypt_aes_cbc(plaintext: str, key: bytes) -> EncryptionResult
plaintext = sdk.decrypt_aes_cbc(ciphertext, key, iv) -> DecryptionResult
```

**Key Derivation:**
```python
sdk = EncryptionSDK()

# Generate random keys/salts
key = sdk.generate_key(size=32)           # 256-bit random key
iv = sdk.generate_iv(size=16)             # 128-bit initialization vector
salt = sdk.generate_salt(size=16)         # 128-bit salt

# Derive key from password
derived_key, salt = sdk.derive_key("password", salt=None)
```

**Password Operations:**
```python
sdk = EncryptionSDK()

# Hash password
hashed, salt = sdk.hash_password("password")
# Verify password
is_valid = sdk.verify_password("password", hashed, salt)
```

### AESCipher

Specialized AES encryption wrapper with mode support.

```python
from src.sdk import AESCipher, AESConfig, AESMode

# GCM mode (recommended for banking)
config = AESConfig(mode=AESMode.GCM)
cipher = AESCipher(config)

key = sdk.generate_key()
encrypted = cipher.encrypt("transaction data", key)
decrypted = cipher.decrypt(encrypted, key)

# CBC mode
config = AESConfig(mode=AESMode.CBC)
cipher = AESCipher(config)
```

### KeyManager

Enterprise key lifecycle management.

```python
from src.sdk import KeyManager, KeyRotationPolicy

mgr = KeyManager()

# Generate key
key_id = mgr.generate_key(
    key_size=32,
    rotation_policy=KeyRotationPolicy.MONTHLY,
    tags={"app": "payments"}
)

# Operations
key = mgr.get_key(key_id)                        # Get key bytes
metadata = mgr.get_metadata(key_id)              # Get metadata
new_id = mgr.rotate_key(key_id)                  # Rotate key
mgr.deactivate_key(key_id)                       # Soft delete
keys = mgr.list_active_keys()                    # List all active
keys = mgr.list_keys_by_tag("app", "payments")   # Search by tag
needs = mgr.check_rotation_needed()               # Find expired keys
metadata = mgr.export_metadata()                  # Export all metadata
mgr.save_metadata("backup.json")                  # Save to file
```

### PasswordManager

Comprehensive password security management.

```python
from src.sdk import PasswordManager, PasswordPolicy, PasswordStrength

# Default policy
pwd_mgr = PasswordManager()

# Custom policy
policy = PasswordPolicy(
    min_length=16,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    max_age_days=90,
    min_entropy_bits=50.0,
)
pwd_mgr = PasswordManager(policy)

# Password hashing
hashed, salt = pwd_mgr.hash_password("password")
is_valid = pwd_mgr.verify_password("password", hashed, salt)

# Validation
is_compliant, errors = pwd_mgr.validate_password("password")

# Strength checking
strength = pwd_mgr.check_strength("password")  # Returns PasswordStrength enum

# Generation
password = pwd_mgr.generate_password(length=20, include_special=True)
```

## 💡 Usage Examples

### Financial Transaction Encryption

```python
from src.sdk import EncryptionSDK, KeyManager
import json

sdk = EncryptionSDK()
key_mgr = KeyManager()

# Generate key for transactions
tx_key_id = key_mgr.generate_key(
    rotation_policy=KeyRotationPolicy.WEEKLY,
    tags={"type": "transactions"}
)

# Encrypt transaction
transaction = {
    "from": "ACC001",
    "to": "ACC002",
    "amount": 10000.00,
    "currency": "USD"
}

tx_key = key_mgr.get_key(tx_key_id)
tx_json = json.dumps(transaction)
encrypted = sdk.encrypt_aes_gcm(tx_json, tx_key)

# Decrypt transaction (verify integrity with GCM)
decrypted = sdk.decrypt_aes_gcm(
    encrypted.ciphertext,
    tx_key,
    encrypted.iv,
    encrypted.tag
)
if decrypted.verified:
    tx = json.loads(decrypted.plaintext)
```

### User Registration Flow

```python
from src.sdk import PasswordManager, PasswordPolicy

pwd_mgr = PasswordManager()

def register_user(username: str, password: str):
    # Validate password strength
    is_valid, errors = pwd_mgr.validate_password(password)
    if not is_valid:
        raise ValueError(f"Weak password: {errors}")
    
    # Hash password
    hashed, salt = pwd_mgr.hash_password(password)
    
    # Store user (hashed and salt in database)
    return {
        "username": username,
        "password_hash": hashed.hex(),
        "password_salt": salt.hex(),
    }

def login_user(username: str, password: str):
    user = get_user_from_db(username)
    hashed = bytes.fromhex(user["password_hash"])
    salt = bytes.fromhex(user["password_salt"])
    
    if pwd_mgr.verify_password(password, hashed, salt):
        return create_session(user)
    raise AuthenticationError("Invalid credentials")
```

### Secure Data Storage

```python
from src.sdk import EncryptionSDK

sdk = EncryptionSDK()

class SecureStorage:
    def __init__(self):
        self.encryption_key = sdk.generate_key()
    
    def encrypt_data(self, data: str) -> dict:
        """Encrypt and return serializable result."""
        result = sdk.encrypt_aes_gcm(data, self.encryption_key)
        return result.to_dict()  # Returns hex-encoded strings
    
    def decrypt_data(self, encrypted_dict: dict) -> str:
        """Decrypt from serialized result."""
        from src.sdk import EncryptionResult
        
        result = EncryptionResult(
            ciphertext=bytes.fromhex(encrypted_dict["ciphertext"]),
            iv=bytes.fromhex(encrypted_dict["iv"]),
            tag=bytes.fromhex(encrypted_dict["tag"]),
        )
        
        decrypted = sdk.decrypt_aes_gcm(
            result.ciphertext,
            self.encryption_key,
            result.iv,
            result.tag,
        )
        return decrypted.plaintext
```

## 🔒 Security

### Cryptographic Standards

- **Encryption**: AES-256 (NIST approved)
- **Authentication**: GCM mode (authenticated encryption)
- **Hashing**: PBKDF2-SHA256 with 100,000 iterations
- **Random Generation**: Python's `secrets` module (cryptographically secure)
- **Key Size**: 256-bit keys (32 bytes)

### Best Practices

1. **Use GCM Mode**: GCM provides authenticated encryption, detecting tampering
2. **Key Rotation**: Rotate keys regularly (monthly recommended for sensitive data)
3. **Salt Usage**: Always use unique salts for password hashing
4. **Password Policy**: Enforce strong password policies (minimum 12 characters)
5. **Key Storage**: Never log or print actual key values
6. **IV Handling**: Never reuse IV with same key (SDK generates unique IVs)

### Data Structure Security

```python
# GCM encryption includes authentication
result = sdk.encrypt_aes_gcm(plaintext, key)
# result.tag prevents tampering detection

# CBC encryption should use separate MAC
result = sdk.encrypt_aes_cbc(plaintext, key)
# Consider HMAC for authentication if needed
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run only SDK tests
python -m pytest tests/test_encryption_sdk.py -v

# Run with coverage
python -m pytest tests/ --cov=src.sdk

# Run specific test
python -m pytest tests/test_encryption_sdk.py::TestEncryptionSDK::test_encrypt_aes_gcm -v
```

### Test Coverage

- 42 dedicated SDK tests
- 100% test pass rate
- Covers all major components
- Tests encryption, decryption, key management, and password security

### Example Tests

```python
# See tests/test_encryption_sdk.py for comprehensive examples:

class TestEncryptionSDK:
    def test_encrypt_aes_gcm()      # Encryption with authentication
    def test_decrypt_aes_gcm()      # Decryption and verification
    def test_hash_password()         # Password hashing
    def test_verify_password()       # Password verification

class TestKeyManager:
    def test_generate_key()          # Key generation
    def test_rotate_key()            # Key rotation
    def test_list_keys_by_tag()      # Key search

class TestPasswordManager:
    def test_validate_password()     # Policy validation
    def test_check_strength()        # Strength assessment
    def test_generate_password()     # Secure generation
```

## 📚 Documentation

- **Full SDK Documentation**: See `docs/ENCRYPTION_SDK.md`
- **API Reference**: See docstrings in source files
- **Examples**: See `examples/encryption_sdk_examples.py`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Security Details**: See `docs/SECURITY.md`

## 🔧 Configuration

### CipherConfig

```python
from src.sdk import EncryptionSDK, CipherConfig, EncryptionAlgorithm

config = CipherConfig(
    algorithm=EncryptionAlgorithm.AES_256_GCM,
    key_size=32,      # bytes (256-bit)
    iv_size=16,       # bytes (128-bit)
    tag_size=128,     # bits
)
sdk = EncryptionSDK(cipher_config=config)
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
```

## 📝 Version

- **SDK Version**: 1.0.0
- **Python**: 3.8+
- **Dependencies**: cryptography>=41.0.0

## 📄 License

MIT License - See LICENSE file

## 🤝 Support

For issues or questions:
1. Check the documentation in `docs/ENCRYPTION_SDK.md`
2. Review examples in `examples/encryption_sdk_examples.py`
3. Check test cases for usage patterns

---

**Built for the Safe Banking Application** 🏦🔐
