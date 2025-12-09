# Banking Encryption SDK - Index & Navigation Guide

Welcome to the Banking Encryption SDK documentation! This guide helps you navigate all available resources.

## 🎯 Quick Navigation

### For Beginners
1. Start with **[SDK_README.md](SDK_README.md)** - Overview and quick start
2. Review **[examples/encryption_sdk_examples.py](examples/encryption_sdk_examples.py)** - See working code
3. Run the examples to get hands-on experience

### For Integration
1. Read **[SDK_INTEGRATION_GUIDE.md](SDK_INTEGRATION_GUIDE.md)** - Step-by-step integration
2. Follow the examples in the integration guide
3. Run tests to verify everything works
4. Integrate into your application

### For Deep Dive
1. Read **[docs/ENCRYPTION_SDK.md](docs/ENCRYPTION_SDK.md)** - Complete API reference
2. Review source code in **[src/sdk/](src/sdk/)**
3. Check tests in **[tests/test_encryption_sdk.py](tests/test_encryption_sdk.py)**
4. Study advanced patterns and configurations

### For Production
1. Review **[docs/SECURITY.md](docs/SECURITY.md)** - Security best practices
2. Follow **[SDK_INTEGRATION_GUIDE.md](SDK_INTEGRATION_GUIDE.md)** - Production patterns
3. Configure policies for your environment
4. Plan key rotation and management

---

## 📚 Documentation Files

### Main Documents

| File | Purpose | Best For |
|------|---------|----------|
| **SDK_README.md** | Overview and quick start | Getting started |
| **docs/ENCRYPTION_SDK.md** | Complete API reference | Detailed learning |
| **SDK_INTEGRATION_GUIDE.md** | Integration patterns | Building with SDK |
| **CREATION_SUMMARY.md** | What was created | Understanding scope |

### Architecture & Security

| File | Purpose | Best For |
|------|---------|----------|
| **docs/ARCHITECTURE.md** | System design | Understanding design |
| **docs/SECURITY.md** | Security guidelines | Security review |
| **docs/API.md** | API endpoints | REST API reference |

---

## 💻 Source Code Structure

```
src/sdk/
├── __init__.py              # Package exports
├── encryption_sdk.py        # Core SDK class
├── aes_cipher.py           # AES encryption wrapper
├── key_manager.py          # Key lifecycle management
└── password_manager.py     # Password security
```

### Module Breakdown

#### `encryption_sdk.py` (Core)
- **EncryptionSDK**: Main class with all core operations
- Encryption (AES-GCM and AES-CBC)
- Key derivation and generation
- Password hashing and verification

#### `aes_cipher.py` (Encryption)
- **AESCipher**: Specialized AES wrapper
- GCM mode (authenticated encryption)
- CBC mode (traditional block cipher)

#### `key_manager.py` (Management)
- **KeyManager**: Enterprise key management
- Key generation and storage
- Rotation with policies
- Metadata tracking

#### `password_manager.py` (Security)
- **PasswordManager**: Password security
- Hashing and verification
- Policy validation
- Strength assessment

---

## 🧪 Testing

### Test File
- **tests/test_encryption_sdk.py** - 42 comprehensive tests

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run SDK tests only
python -m pytest tests/test_encryption_sdk.py -v

# Run specific test class
python -m pytest tests/test_encryption_sdk.py::TestEncryptionSDK -v

# Run with coverage
python -m pytest tests/ --cov=src.sdk
```

### Test Coverage

| Component | Tests | Status |
|-----------|-------|--------|
| EncryptionSDK | 11 | ✅ PASS |
| AESCipher | 4 | ✅ PASS |
| KeyManager | 8 | ✅ PASS |
| PasswordManager | 11 | ✅ PASS |
| Data Classes | 4 | ✅ PASS |
| Configuration | 3 | ✅ PASS |
| **Total** | **42** | **✅ PASS** |

---

## 📖 Examples

### Example File
- **examples/encryption_sdk_examples.py** - 6 working examples

### Examples Included

1. **Basic Encryption** (lines 17-37)
   - Key generation
   - Encryption with AES-GCM
   - Decryption and verification

2. **Password Management** (lines 40-84)
   - Password validation
   - Strength checking
   - Hash and verify

3. **Key Management** (lines 87-131)
   - Key generation
   - Rotation policies
   - Metadata tracking
   - Key rotation

4. **AES Cipher Wrapper** (lines 134-165)
   - GCM mode usage
   - CBC mode usage
   - Mode switching

5. **Password Generation** (lines 168-179)
   - Secure random generation
   - Configurable length
   - Strength checking

6. **Banking Scenario** (lines 182-254)
   - User registration
   - Transaction encryption
   - Key rotation workflow

### Running Examples

```bash
# Run all examples
python examples/encryption_sdk_examples.py

# Run with Python directly
cd /Users/joshuafitzgerald/cp
source venv/bin/activate
python -m examples.encryption_sdk_examples
```

---

## 🔍 API Quick Reference

### EncryptionSDK

```python
from src.sdk import EncryptionSDK

sdk = EncryptionSDK()

# Encryption
sdk.encrypt_aes_gcm(plaintext, key)      # Authenticated encryption
sdk.decrypt_aes_gcm(ciphertext, key, iv, tag)

sdk.encrypt_aes_cbc(plaintext, key)      # Traditional encryption
sdk.decrypt_aes_cbc(ciphertext, key, iv)

# Key/Salt Generation
sdk.generate_key(size=32)
sdk.generate_iv(size=16)
sdk.generate_salt(size=16)

# Key Derivation
sdk.derive_key(password, salt=None)

# Password Operations
sdk.hash_password(password, salt=None)
sdk.verify_password(password, hashed, salt)
```

### KeyManager

```python
from src.sdk import KeyManager, KeyRotationPolicy

mgr = KeyManager()

# Key Operations
mgr.generate_key(key_size=32, rotation_policy=KeyRotationPolicy.MONTHLY)
mgr.get_key(key_id)
mgr.get_metadata(key_id)
mgr.rotate_key(key_id)
mgr.deactivate_key(key_id)

# Key Search
mgr.list_active_keys()
mgr.list_keys_by_tag(tag, value)

# Rotation Management
mgr.check_rotation_needed()

# Export
mgr.export_metadata()
mgr.save_metadata(filepath)
```

### PasswordManager

```python
from src.sdk import PasswordManager, PasswordPolicy

pwd_mgr = PasswordManager()

# Hashing
pwd_mgr.hash_password(password, salt=None)
pwd_mgr.verify_password(password, hashed, salt)

# Validation & Strength
pwd_mgr.validate_password(password)
pwd_mgr.check_strength(password)

# Generation
pwd_mgr.generate_password(length=16, include_special=True)
```

### AESCipher

```python
from src.sdk import AESCipher, AESConfig, AESMode

config = AESConfig(mode=AESMode.GCM)
cipher = AESCipher(config)

encrypted = cipher.encrypt(plaintext, key)
decrypted = cipher.decrypt(encrypted, key)
```

---

## 🔐 Security Features

### Cryptography Standards
- ✅ AES-256 (NIST approved)
- ✅ GCM mode (authenticated encryption)
- ✅ CBC mode (traditional block cipher)
- ✅ PBKDF2-SHA256 (password hashing)
- ✅ 100,000 iterations (modern standard)

### Key Management
- ✅ Secure random generation
- ✅ Rotation policies
- ✅ Metadata tracking
- ✅ Soft deletion
- ✅ Tag-based organization

### Password Security
- ✅ Policy-based validation
- ✅ Entropy calculation
- ✅ Strength assessment
- ✅ Salt management

---

## 📋 Common Tasks

### Encrypt Data
```python
sdk = EncryptionSDK()
key = sdk.generate_key()
result = sdk.encrypt_aes_gcm("secret", key)
plaintext = sdk.decrypt_aes_gcm(result.ciphertext, key, result.iv, result.tag)
```

### Hash Password
```python
pwd_mgr = PasswordManager()
hashed, salt = pwd_mgr.hash_password("password")
is_valid = pwd_mgr.verify_password("password", hashed, salt)
```

### Manage Keys
```python
mgr = KeyManager()
key_id = mgr.generate_key()
key = mgr.get_key(key_id)
new_id = mgr.rotate_key(key_id)
```

### Validate Password
```python
pwd_mgr = PasswordManager()
is_valid, errors = pwd_mgr.validate_password("password")
if not is_valid:
    for error in errors:
        print(error)
```

### Check Strength
```python
pwd_mgr = PasswordManager()
strength = pwd_mgr.check_strength("MyPassword123!")
print(f"Strength: {strength.value}")
```

---

## 🚀 Getting Started Path

### 5-Minute Quick Start
1. Read **SDK_README.md** (sections 1-3)
2. Look at **Basic Encryption example**
3. Run the example code

### 30-Minute Deep Dive
1. Read **SDK_README.md** (full)
2. Review **docs/ENCRYPTION_SDK.md** (Core sections)
3. Run all **examples/encryption_sdk_examples.py**
4. Read some **test cases**

### Full Learning (1-2 hours)
1. Read **SDK_README.md** (full)
2. Read **docs/ENCRYPTION_SDK.md** (full)
3. Read **SDK_INTEGRATION_GUIDE.md**
4. Run and study **all examples**
5. Read and understand **all test cases**
6. Review **source code** in `src/sdk/`

### Production Integration (2-4 hours)
1. Read **SDK_INTEGRATION_GUIDE.md** (full)
2. Read **docs/SECURITY.md**
3. Review **integration examples** in guide
4. Plan your integration
5. Execute integration
6. Run tests
7. Configure for production

---

## 📊 What's Included

| Category | Items | Count |
|----------|-------|-------|
| **Source Code** | SDK modules | 5 files |
| **Tests** | Test cases | 42 tests |
| **Documentation** | Docs files | 4 files |
| **Examples** | Working examples | 6 scenarios |
| **Total Lines** | Code + Docs | ~2,600 |

---

## ✅ Validation

- ✅ **42 SDK tests** - All passing
- ✅ **100% pass rate** - No failures
- ✅ **Type hints** - Full coverage
- ✅ **Documentation** - Comprehensive
- ✅ **Examples** - Working code
- ✅ **Integration patterns** - Ready to use

---

## 🎓 Learning Resources

### Documentation (Read)
- SDK_README.md - Overview
- docs/ENCRYPTION_SDK.md - Details
- SDK_INTEGRATION_GUIDE.md - How-to

### Code (Study)
- src/sdk/*.py - Implementation
- examples/encryption_sdk_examples.py - Patterns
- tests/test_encryption_sdk.py - Usage

### Run (Execute)
- examples/encryption_sdk_examples.py - Working code
- pytest tests/test_encryption_sdk.py - Validation

---

## 🤔 Help & Troubleshooting

### I want to...

**Learn the basics**
→ Read SDK_README.md (Quick Start section)

**See working code**
→ Run examples/encryption_sdk_examples.py

**Integrate with my app**
→ Follow SDK_INTEGRATION_GUIDE.md

**Understand the API**
→ Read docs/ENCRYPTION_SDK.md

**Review security**
→ Read docs/SECURITY.md

**Verify it works**
→ Run pytest tests/test_encryption_sdk.py

**Understand the code**
→ Read source in src/sdk/ with docstrings

**Configure for production**
→ Follow Production section in SDK_INTEGRATION_GUIDE.md

---

## 📞 Support Resources

| Need | Resource |
|------|----------|
| Quick Start | SDK_README.md |
| API Details | docs/ENCRYPTION_SDK.md |
| Integration | SDK_INTEGRATION_GUIDE.md |
| Security | docs/SECURITY.md |
| Examples | examples/encryption_sdk_examples.py |
| Testing | tests/test_encryption_sdk.py |
| Code | src/sdk/*.py |

---

## 🎉 Ready to Start?

### Recommended Path

1. **Now** (5 min): Read SDK_README.md Quick Start
2. **Next** (15 min): Run examples/encryption_sdk_examples.py
3. **Then** (30 min): Read SDK_INTEGRATION_GUIDE.md
4. **Finally** (varies): Integrate into your application

---

## 📄 Document Summary

| File | Purpose | Lines | Time |
|------|---------|-------|------|
| SDK_README.md | Overview + Quick Start | 450 | 15 min |
| docs/ENCRYPTION_SDK.md | Full Reference | 400 | 30 min |
| SDK_INTEGRATION_GUIDE.md | Integration Patterns | 500 | 30 min |
| CREATION_SUMMARY.md | What Was Created | 350 | 10 min |
| examples/ | Working Code | 300 | 20 min |
| tests/ | Test Cases | 625 | 30 min |

---

**Happy encrypting! 🔐**

*Banking Encryption SDK v1.0.0*
