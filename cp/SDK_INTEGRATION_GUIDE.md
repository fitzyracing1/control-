# Encryption SDK Integration Guide

This guide shows how to integrate the Banking Encryption SDK into your application.

## Overview

The SDK is located in `src/sdk/` and provides:

- `EncryptionSDK` - Core encryption operations
- `AESCipher` - AES encryption wrapper
- `KeyManager` - Key lifecycle management
- `PasswordManager` - Password hashing and validation

## File Structure

```
src/sdk/
├── __init__.py              # Package exports
├── encryption_sdk.py        # Core SDK implementation
├── aes_cipher.py           # AES cipher wrapper
├── key_manager.py          # Key management
└── password_manager.py     # Password management

tests/
└── test_encryption_sdk.py  # 42 comprehensive tests

examples/
└── encryption_sdk_examples.py  # Usage examples

docs/
└── ENCRYPTION_SDK.md       # Full documentation
```

## Integration Examples

### 1. Integrate with User Authentication

**File: `src/api/users.py`**

```python
from src.sdk import PasswordManager, PasswordPolicy
from src.database.models import User

class UserRegistration:
    def __init__(self):
        self.pwd_mgr = PasswordManager()
    
    def register(self, username: str, email: str, password: str):
        """Register user with secure password hashing."""
        # Validate password
        is_valid, errors = self.pwd_mgr.validate_password(password)
        if not is_valid:
            raise ValueError(f"Password validation failed: {errors}")
        
        # Hash password
        hashed, salt = self.pwd_mgr.hash_password(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=hashed,
            password_salt=salt,
        )
        return user
    
    def verify_login(self, username: str, password: str) -> bool:
        """Verify user password during login."""
        user = User.get_by_username(username)
        if not user:
            return False
        
        return self.pwd_mgr.verify_password(
            password,
            user.password_hash,
            user.password_salt,
        )
```

### 2. Integrate with Transaction Encryption

**File: `src/api/transactions.py`**

```python
from src.sdk import EncryptionSDK, KeyManager, KeyRotationPolicy
from src.database.models import Transaction
import json

class SecureTransactions:
    def __init__(self):
        self.sdk = EncryptionSDK()
        self.key_mgr = KeyManager()
        self.tx_key_id = self._init_tx_key()
    
    def _init_tx_key(self):
        """Initialize transaction encryption key."""
        # Check if key exists
        active_keys = self.key_mgr.list_active_keys()
        if active_keys:
            return active_keys[0]
        
        # Create new key
        return self.key_mgr.generate_key(
            rotation_policy=KeyRotationPolicy.WEEKLY,
            tags={"service": "transactions", "type": "sensitive_data"}
        )
    
    def create_transaction(self, tx_data: dict):
        """Create and encrypt transaction."""
        # Serialize transaction
        tx_json = json.dumps(tx_data)
        
        # Get encryption key
        tx_key = self.key_mgr.get_key(self.tx_key_id)
        
        # Encrypt
        encrypted = self.sdk.encrypt_aes_gcm(tx_json, tx_key)
        
        # Store encrypted transaction
        transaction = Transaction(
            ciphertext=encrypted.ciphertext,
            iv=encrypted.iv,
            tag=encrypted.tag,
            algorithm=encrypted.algorithm,
            key_id=self.tx_key_id,
        )
        return transaction
    
    def retrieve_transaction(self, transaction_id: str) -> dict:
        """Retrieve and decrypt transaction."""
        # Get transaction from database
        tx = Transaction.get_by_id(transaction_id)
        
        # Get decryption key
        key = self.key_mgr.get_key(tx.key_id)
        
        # Decrypt with authentication verification
        decrypted = self.sdk.decrypt_aes_gcm(
            tx.ciphertext,
            key,
            tx.iv,
            tx.tag,
        )
        
        if not decrypted.verified:
            raise ValueError("Transaction integrity check failed")
        
        # Deserialize
        return json.loads(decrypted.plaintext)
```

### 3. Integrate with API Responses

**File: `src/api/middleware.py`**

```python
from src.sdk import EncryptionSDK

class EncryptionMiddleware:
    def __init__(self):
        self.sdk = EncryptionSDK()
        self.response_key = self.sdk.generate_key()
    
    def encrypt_response(self, data: dict):
        """Encrypt sensitive API response data."""
        import json
        
        json_str = json.dumps(data)
        result = self.sdk.encrypt_aes_gcm(json_str, self.response_key)
        
        return {
            "encrypted": True,
            "data": result.to_dict(),
        }
    
    def decrypt_response(self, encrypted_data: dict):
        """Decrypt API response on client."""
        from src.sdk import EncryptionResult
        
        encrypted = encrypted_data["data"]
        result = EncryptionResult(
            ciphertext=bytes.fromhex(encrypted["ciphertext"]),
            iv=bytes.fromhex(encrypted["iv"]),
            tag=bytes.fromhex(encrypted["tag"]),
        )
        
        decrypted = self.sdk.decrypt_aes_gcm(
            result.ciphertext,
            self.response_key,
            result.iv,
            result.tag,
        )
        
        import json
        return json.loads(decrypted.plaintext)
```

### 4. Scheduled Key Rotation

**File: `src/tasks/key_rotation.py`**

```python
from src.sdk import KeyManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class KeyRotationTask:
    def __init__(self):
        self.key_mgr = KeyManager()
    
    def run_rotation_check(self):
        """Check and rotate expired keys."""
        needs_rotation = self.key_mgr.check_rotation_needed()
        
        if not needs_rotation:
            logger.info("No keys need rotation")
            return
        
        for key_id in needs_rotation:
            try:
                old_key = self.key_mgr.get_metadata(key_id)
                new_key_id = self.key_mgr.rotate_key(key_id)
                
                logger.info(
                    f"Rotated key {key_id}: "
                    f"next rotation {old_key.next_rotation}"
                )
                
                # Update database references to use new key
                self.update_key_references(key_id, new_key_id)
                
            except Exception as e:
                logger.error(f"Failed to rotate key {key_id}: {e}")
    
    def update_key_references(self, old_key_id: str, new_key_id: str):
        """Update any references to old key in database."""
        # Update transaction records, user records, etc.
        pass
```

## Step-by-Step Integration

### Step 1: Import SDK Components

```python
from src.sdk import (
    EncryptionSDK,
    AESCipher,
    KeyManager,
    PasswordManager,
    KeyRotationPolicy,
)
```

### Step 2: Initialize Components

```python
class SecurityModule:
    def __init__(self):
        self.sdk = EncryptionSDK()
        self.key_mgr = KeyManager()
        self.pwd_mgr = PasswordManager()
```

### Step 3: Use in Your Code

```python
# Encrypt data
key = self.key_mgr.generate_key(tags={"app": "myapp"})
encrypted = self.sdk.encrypt_aes_gcm("sensitive data", key)

# Decrypt data
decrypted = self.sdk.decrypt_aes_gcm(
    encrypted.ciphertext,
    key,
    encrypted.iv,
    encrypted.tag,
)

# Hash password
hashed, salt = self.pwd_mgr.hash_password("password")

# Verify password
is_valid = self.pwd_mgr.verify_password("password", hashed, salt)
```

## Database Schema Updates

If storing encrypted data, consider these schema additions:

```sql
-- For encrypted transactions
ALTER TABLE transactions ADD COLUMN (
    ciphertext BLOB NOT NULL,
    iv BLOB NOT NULL,
    tag BLOB,
    algorithm VARCHAR(20) DEFAULT 'AES-256-GCM',
    key_id VARCHAR(32),
    encrypted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- For users with password hashing
ALTER TABLE users ADD COLUMN (
    password_hash BLOB NOT NULL,
    password_salt BLOB NOT NULL,
    password_changed_at TIMESTAMP
);

-- For key management
CREATE TABLE encryption_keys (
    key_id VARCHAR(32) PRIMARY KEY,
    algorithm VARCHAR(20),
    key_size INTEGER,
    rotation_policy VARCHAR(20),
    created_at TIMESTAMP,
    last_rotated TIMESTAMP,
    next_rotation TIMESTAMP,
    active BOOLEAN DEFAULT TRUE,
    tags JSON
);
```

## Configuration Best Practices

### Development Environment

```python
from src.sdk import PasswordPolicy

# More permissive for testing
dev_policy = PasswordPolicy(
    min_length=8,  # Shorter for testing
    require_special=False,
)
```

### Production Environment

```python
from src.sdk import PasswordPolicy

# Strict for security
prod_policy = PasswordPolicy(
    min_length=16,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    max_age_days=90,
    min_entropy_bits=50.0,
)
```

## Testing Your Integration

```python
def test_user_registration_encryption():
    """Test that user passwords are encrypted."""
    from src.api.users import UserRegistration
    
    registration = UserRegistration()
    user = registration.register("john", "john@example.com", "SecurePass123!")
    
    # Verify password is hashed
    assert user.password_hash is not None
    assert user.password_salt is not None
    assert user.password_hash != b"SecurePass123!"
    
    # Verify password verification works
    assert registration.verify_login("john", "SecurePass123!")
    assert not registration.verify_login("john", "WrongPassword")
```

## Performance Considerations

### Caching Keys

```python
from functools import lru_cache

class PerformantTransactions:
    @lru_cache(maxsize=10)
    def get_tx_key(self):
        """Cache the transaction key."""
        return self.key_mgr.get_key(self.tx_key_id)
```

### Batch Encryption

```python
def batch_encrypt_transactions(self, transactions: list):
    """Encrypt multiple transactions efficiently."""
    key = self.key_mgr.get_key(self.tx_key_id)
    
    results = []
    for tx in transactions:
        encrypted = self.sdk.encrypt_aes_gcm(
            json.dumps(tx),
            key
        )
        results.append(encrypted)
    
    return results
```

## Common Issues and Solutions

### Issue: Key not found

```python
# Solution: Check if key is active
key = self.key_mgr.get_key(key_id)
if key is None:
    # Key is deactivated, generate new one
    key_id = self.key_mgr.generate_key()
    key = self.key_mgr.get_key(key_id)
```

### Issue: Authentication failure

```python
# Solution: Check tag is present for GCM
if encrypted.tag is None:
    raise ValueError("GCM mode requires authentication tag")

# Verify during decryption
try:
    decrypted = self.sdk.decrypt_aes_gcm(
        ciphertext, key, iv, tag
    )
except InvalidTag:
    # Data was tampered with
    logger.error("Data integrity check failed")
```

### Issue: Password validation errors

```python
# Solution: Check specific validation errors
is_valid, errors = self.pwd_mgr.validate_password("password")
for error in errors:
    if "uppercase" in error:
        # Handle uppercase requirement
        pass
    elif "length" in error:
        # Handle length requirement
        pass
```

## Next Steps

1. **Review Documentation**: See `docs/ENCRYPTION_SDK.md` for detailed API reference
2. **Run Examples**: See `examples/encryption_sdk_examples.py` for working examples
3. **Run Tests**: Execute `pytest tests/test_encryption_sdk.py` to validate
4. **Integrate Components**: Follow the integration patterns above
5. **Configure Policies**: Set up security policies for your environment

## Support & Questions

- **Full Documentation**: `docs/ENCRYPTION_SDK.md`
- **API Reference**: Docstrings in `src/sdk/` files
- **Working Examples**: `examples/encryption_sdk_examples.py`
- **Test Examples**: `tests/test_encryption_sdk.py`

---

**Successfully integrated the Banking Encryption SDK! 🎉**
