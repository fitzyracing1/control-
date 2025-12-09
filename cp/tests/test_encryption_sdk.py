"""Unit tests for Encryption SDK."""

import pytest
from datetime import datetime, timedelta

from src.sdk import (
    EncryptionSDK,
    AESCipher,
    AESConfig,
    AESMode,
    KeyManager,
    KeyRotationPolicy,
    PasswordManager,
    PasswordPolicy,
    PasswordStrength,
    CipherConfig,
    KeyDerivationConfig,
)


class TestEncryptionSDK:
    """Test EncryptionSDK core functionality."""
    
    def test_initialization(self):
        """Test SDK initialization with default config."""
        sdk = EncryptionSDK()
        assert sdk.cipher_config is not None
        assert sdk.kdf_config is not None
    
    def test_generate_key(self):
        """Test key generation."""
        sdk = EncryptionSDK()
        key = sdk.generate_key()
        assert len(key) == 32  # 256 bits
        assert isinstance(key, bytes)
    
    def test_generate_key_custom_size(self):
        """Test key generation with custom size."""
        sdk = EncryptionSDK()
        key = sdk.generate_key(size=16)
        assert len(key) == 16
    
    def test_generate_iv(self):
        """Test IV generation."""
        sdk = EncryptionSDK()
        iv = sdk.generate_iv()
        assert len(iv) == 16
        assert isinstance(iv, bytes)
    
    def test_generate_salt(self):
        """Test salt generation."""
        sdk = EncryptionSDK()
        salt = sdk.generate_salt()
        assert len(salt) == 16
        assert isinstance(salt, bytes)
    
    def test_derive_key(self):
        """Test key derivation from password."""
        sdk = EncryptionSDK()
        password = "TestPassword123"
        
        derived_key, salt = sdk.derive_key(password)
        assert len(derived_key) == 32
        assert len(salt) == 16
        assert isinstance(derived_key, bytes)
        assert isinstance(salt, bytes)
    
    def test_derive_key_with_salt(self):
        """Test key derivation with provided salt."""
        sdk = EncryptionSDK()
        password = "TestPassword123"
        salt = sdk.generate_salt()
        
        derived_key1, returned_salt = sdk.derive_key(password, salt)
        derived_key2, _ = sdk.derive_key(password, salt)
        
        assert derived_key1 == derived_key2
        assert returned_salt == salt
    
    def test_encrypt_aes_gcm(self):
        """Test AES-256-GCM encryption."""
        sdk = EncryptionSDK()
        plaintext = "Sensitive data"
        key = sdk.generate_key()
        
        result = sdk.encrypt_aes_gcm(plaintext, key)
        
        assert result.ciphertext != plaintext.encode()
        assert len(result.iv) == 16
        assert len(result.tag) == 16
        assert result.algorithm == "AES-256-GCM"
    
    def test_decrypt_aes_gcm(self):
        """Test AES-256-GCM decryption."""
        sdk = EncryptionSDK()
        plaintext = "Sensitive data"
        key = sdk.generate_key()
        
        encrypted = sdk.encrypt_aes_gcm(plaintext, key)
        decrypted = sdk.decrypt_aes_gcm(
            encrypted.ciphertext,
            key,
            encrypted.iv,
            encrypted.tag,
        )
        
        assert decrypted.plaintext == plaintext
        assert decrypted.verified is True
    
    def test_encrypt_decrypt_aes_gcm_roundtrip(self):
        """Test full GCM encrypt-decrypt cycle."""
        sdk = EncryptionSDK()
        plaintexts = [
            "Short",
            "A longer piece of text with special chars: !@#$%",
            "Unicode: 你好世界 🔐",
            "Financial data: $1000.50",
        ]
        
        for plaintext in plaintexts:
            key = sdk.generate_key()
            encrypted = sdk.encrypt_aes_gcm(plaintext, key)
            decrypted = sdk.decrypt_aes_gcm(
                encrypted.ciphertext,
                key,
                encrypted.iv,
                encrypted.tag,
            )
            assert decrypted.plaintext == plaintext
    
    def test_encrypt_aes_gcm_invalid_key_size(self):
        """Test encryption with invalid key size."""
        sdk = EncryptionSDK()
        plaintext = "Data"
        invalid_key = b"short"
        
        with pytest.raises(ValueError):
            sdk.encrypt_aes_gcm(plaintext, invalid_key)
    
    def test_encrypt_aes_cbc(self):
        """Test AES-256-CBC encryption."""
        sdk = EncryptionSDK()
        plaintext = "Sensitive data"
        key = sdk.generate_key()
        
        result = sdk.encrypt_aes_cbc(plaintext, key)
        
        assert result.ciphertext != plaintext.encode()
        assert len(result.iv) == 16
        assert result.algorithm == "AES-256-CBC"
        assert result.tag is None  # CBC doesn't use tags
    
    def test_decrypt_aes_cbc(self):
        """Test AES-256-CBC decryption."""
        sdk = EncryptionSDK()
        plaintext = "Sensitive data"
        key = sdk.generate_key()
        
        encrypted = sdk.encrypt_aes_cbc(plaintext, key)
        decrypted = sdk.decrypt_aes_cbc(
            encrypted.ciphertext,
            key,
            encrypted.iv,
        )
        
        assert decrypted.plaintext == plaintext
    
    def test_hash_password(self):
        """Test password hashing."""
        sdk = EncryptionSDK()
        password = "MySecurePassword123!"
        
        hashed, salt = sdk.hash_password(password)
        
        assert len(hashed) == 32
        assert len(salt) == 16
        assert hashed != password.encode()
    
    def test_verify_password(self):
        """Test password verification."""
        sdk = EncryptionSDK()
        password = "MySecurePassword123!"
        
        hashed, salt = sdk.hash_password(password)
        
        assert sdk.verify_password(password, hashed, salt) is True
        assert sdk.verify_password("WrongPassword", hashed, salt) is False


class TestAESCipher:
    """Test AES Cipher wrapper."""
    
    def test_gcm_mode_encryption(self):
        """Test AES cipher in GCM mode."""
        config = AESConfig(mode=AESMode.GCM)
        cipher = AESCipher(config)
        sdk = EncryptionSDK()
        key = sdk.generate_key()
        
        plaintext = "Test data"
        result = cipher.encrypt(plaintext, key)
        
        assert result.tag is not None
        assert result.algorithm == "AES-256-GCM"
    
    def test_gcm_mode_decryption(self):
        """Test AES cipher GCM decryption."""
        config = AESConfig(mode=AESMode.GCM)
        cipher = AESCipher(config)
        sdk = EncryptionSDK()
        key = sdk.generate_key()
        
        plaintext = "Test data"
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        
        assert decrypted.plaintext == plaintext
        assert decrypted.verified is True
    
    def test_cbc_mode_encryption(self):
        """Test AES cipher in CBC mode."""
        config = AESConfig(mode=AESMode.CBC)
        cipher = AESCipher(config)
        sdk = EncryptionSDK()
        key = sdk.generate_key()
        
        plaintext = "Test data"
        result = cipher.encrypt(plaintext, key)
        
        assert result.tag is None
        assert result.algorithm == "AES-256-CBC"
    
    def test_cbc_mode_decryption(self):
        """Test AES cipher CBC decryption."""
        config = AESConfig(mode=AESMode.CBC)
        cipher = AESCipher(config)
        sdk = EncryptionSDK()
        key = sdk.generate_key()
        
        plaintext = "Test data"
        encrypted = cipher.encrypt(plaintext, key)
        decrypted = cipher.decrypt(encrypted, key)
        
        assert decrypted.plaintext == plaintext


class TestKeyManager:
    """Test Key Manager functionality."""
    
    def test_generate_key(self):
        """Test key generation and storage."""
        manager = KeyManager()
        key_id = manager.generate_key()
        
        assert key_id is not None
        assert len(key_id) == 32  # hex token
        assert manager.get_key(key_id) is not None
    
    def test_get_metadata(self):
        """Test retrieving key metadata."""
        manager = KeyManager()
        key_id = manager.generate_key(tags={"app": "payments"})
        metadata = manager.get_metadata(key_id)
        
        assert metadata is not None
        assert metadata.key_id == key_id
        assert metadata.algorithm == "AES-256"
        assert metadata.key_size == 32
        assert metadata.active is True
        assert metadata.tags["app"] == "payments"
    
    def test_rotate_key(self):
        """Test key rotation."""
        manager = KeyManager()
        old_key_id = manager.generate_key(
            rotation_policy=KeyRotationPolicy.MONTHLY
        )
        old_key = manager.get_key(old_key_id)
        
        new_key_id = manager.rotate_key(old_key_id)
        new_key = manager.get_key(new_key_id)
        old_key_after = manager.get_key(old_key_id)
        
        assert new_key_id != old_key_id
        assert new_key is not None
        assert old_key_after is None  # Old key deactivated
        assert old_key != new_key
    
    def test_deactivate_key(self):
        """Test key deactivation."""
        manager = KeyManager()
        key_id = manager.generate_key()
        
        manager.deactivate_key(key_id)
        
        assert manager.get_key(key_id) is None
    
    def test_list_active_keys(self):
        """Test listing active keys."""
        manager = KeyManager()
        key_id_1 = manager.generate_key()
        key_id_2 = manager.generate_key()
        key_id_3 = manager.generate_key()
        
        manager.deactivate_key(key_id_2)
        
        active = manager.list_active_keys()
        
        assert key_id_1 in active
        assert key_id_2 not in active
        assert key_id_3 in active
        assert len(active) == 2
    
    def test_list_keys_by_tag(self):
        """Test finding keys by tag."""
        manager = KeyManager()
        payment_key = manager.generate_key(tags={"type": "payment"})
        user_key = manager.generate_key(tags={"type": "user"})
        
        payment_keys = manager.list_keys_by_tag("type", "payment")
        user_keys = manager.list_keys_by_tag("type", "user")
        
        assert payment_key in payment_keys
        assert user_key not in payment_keys
        assert user_key in user_keys
        assert payment_key not in user_keys
    
    def test_check_rotation_needed(self):
        """Test rotation status checking."""
        manager = KeyManager()
        
        # Create key with near-expiration
        key_id = manager.generate_key(rotation_policy=KeyRotationPolicy.DAILY)
        metadata = manager.get_metadata(key_id)
        
        # Artificially set rotation time to past
        metadata.next_rotation = datetime.utcnow() - timedelta(hours=1)
        
        needs_rotation = manager.check_rotation_needed()
        
        assert key_id in needs_rotation
    
    def test_export_metadata(self):
        """Test metadata export."""
        manager = KeyManager()
        key_id = manager.generate_key(tags={"app": "banking"})
        
        exported = manager.export_metadata()
        
        assert key_id in exported
        assert exported[key_id]["algorithm"] == "AES-256"
        assert exported[key_id]["tags"]["app"] == "banking"


class TestPasswordManager:
    """Test Password Manager functionality."""
    
    def test_hash_password(self):
        """Test password hashing."""
        manager = PasswordManager()
        password = "MySecurePassword123!"
        
        hashed, salt = manager.hash_password(password)
        
        assert len(hashed) == 32
        assert len(salt) == 16
    
    def test_verify_password(self):
        """Test password verification."""
        manager = PasswordManager()
        password = "MySecurePassword123!"
        
        hashed, salt = manager.hash_password(password)
        
        assert manager.verify_password(password, hashed, salt) is True
        assert manager.verify_password("WrongPassword", hashed, salt) is False
    
    def test_validate_password_success(self):
        """Test password validation - success case."""
        policy = PasswordPolicy(min_length=12)
        manager = PasswordManager(policy)
        
        is_valid, errors = manager.validate_password("ValidPassword123!")
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_password_too_short(self):
        """Test password validation - too short."""
        policy = PasswordPolicy(min_length=12)
        manager = PasswordManager(policy)
        
        is_valid, errors = manager.validate_password("Short1!")
        
        assert is_valid is False
        assert any("at least 12" in err for err in errors)
    
    def test_validate_password_no_uppercase(self):
        """Test password validation - no uppercase."""
        policy = PasswordPolicy(
            min_length=8,
            require_uppercase=True,
        )
        manager = PasswordManager(policy)
        
        is_valid, errors = manager.validate_password("lowercase123!")
        
        assert is_valid is False
        assert any("uppercase" in err.lower() for err in errors)
    
    def test_validate_password_no_special(self):
        """Test password validation - no special character."""
        policy = PasswordPolicy(
            min_length=8,
            require_special=True,
        )
        manager = PasswordManager(policy)
        
        is_valid, errors = manager.validate_password("Password123")
        
        assert is_valid is False
        assert any("special" in err.lower() for err in errors)
    
    def test_check_strength_weak(self):
        """Test password strength - weak."""
        manager = PasswordManager()
        strength = manager.check_strength("weak")
        
        assert strength == PasswordStrength.WEAK
    
    def test_check_strength_strong(self):
        """Test password strength - strong."""
        manager = PasswordManager()
        strength = manager.check_strength("MySecurePassword123!")
        
        assert strength in [PasswordStrength.STRONG, PasswordStrength.VERY_STRONG]
    
    def test_check_strength_very_strong(self):
        """Test password strength - very strong."""
        manager = PasswordManager()
        strength = manager.check_strength("VeryStr0ng!P@ssw0rd#WithM@nyChars2024")
        
        assert strength == PasswordStrength.VERY_STRONG
    
    def test_generate_password(self):
        """Test password generation."""
        manager = PasswordManager()
        password = manager.generate_password(length=16)
        
        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in manager.policy.special_characters for c in password)
    
    def test_generate_password_without_special(self):
        """Test password generation without special characters."""
        manager = PasswordManager()
        password = manager.generate_password(
            length=12,
            include_special=False,
        )
        
        assert len(password) == 12
        assert not any(
            c in manager.policy.special_characters for c in password
        )


class TestEncryptionResult:
    """Test EncryptionResult data class."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        from src.sdk import EncryptionResult
        
        result = EncryptionResult(
            ciphertext=b"encrypted_data",
            iv=b"initialization",
            tag=b"authentication",
            algorithm="AES-256-GCM",
        )
        
        result_dict = result.to_dict()
        
        assert "ciphertext" in result_dict
        assert "iv" in result_dict
        assert "tag" in result_dict
        assert "algorithm" in result_dict
        assert isinstance(result_dict["ciphertext"], str)  # hex encoded


class TestConfiguration:
    """Test configuration classes."""
    
    def test_cipher_config_defaults(self):
        """Test cipher configuration defaults."""
        config = CipherConfig()
        
        assert config.key_size == 32
        assert config.iv_size == 16
        assert config.tag_size == 128
    
    def test_kdf_config_defaults(self):
        """Test KDF configuration defaults."""
        config = KeyDerivationConfig()
        
        assert config.iterations == 100000
        assert config.salt_length == 16
        assert config.derived_key_length == 32
    
    def test_password_policy_defaults(self):
        """Test password policy defaults."""
        policy = PasswordPolicy()
        
        assert policy.min_length == 12
        assert policy.require_uppercase is True
        assert policy.require_lowercase is True
        assert policy.require_digits is True
        assert policy.require_special is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
