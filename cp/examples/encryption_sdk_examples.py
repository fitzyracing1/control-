"""
Examples of using the Banking Encryption SDK.

This file demonstrates common use cases for the encryption SDK in banking applications.
"""

from src.sdk import (
    EncryptionSDK,
    AESCipher,
    AESConfig,
    AESMode,
    KeyManager,
    KeyRotationPolicy,
    PasswordManager,
    PasswordPolicy,
)


def example_1_basic_encryption():
    """Example 1: Basic encryption and decryption."""
    print("\n=== Example 1: Basic Encryption ===")
    
    # Initialize SDK
    sdk = EncryptionSDK()
    
    # Generate encryption key
    key = sdk.generate_key()
    print(f"Generated key (hex): {key.hex()[:32]}...")
    
    # Encrypt sensitive data
    plaintext = "Account number: 1234567890"
    encrypted_result = sdk.encrypt_aes_gcm(plaintext, key)
    print(f"Plaintext: {plaintext}")
    print(f"Ciphertext (hex): {encrypted_result.ciphertext.hex()[:32]}...")
    
    # Decrypt
    decrypted_result = sdk.decrypt_aes_gcm(
        encrypted_result.ciphertext,
        key,
        encrypted_result.iv,
        encrypted_result.tag,
    )
    print(f"Decrypted: {decrypted_result.plaintext}")


def example_2_password_management():
    """Example 2: Password hashing and validation."""
    print("\n=== Example 2: Password Management ===")
    
    # Create password manager with strict policy
    policy = PasswordPolicy(
        min_length=16,
        require_uppercase=True,
        require_lowercase=True,
        require_digits=True,
        require_special=True,
    )
    pwd_manager = PasswordManager(policy)
    
    # Test password
    test_password = "WeakPass"
    print(f"\nPassword: {test_password}")
    
    # Validate against policy
    is_valid, errors = pwd_manager.validate_password(test_password)
    print(f"Valid: {is_valid}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
    
    # Check strength
    strength = pwd_manager.check_strength(test_password)
    print(f"Strength: {strength.value}")
    
    # Now test a strong password
    strong_password = "MySecurePassword123!"
    print(f"\nPassword: {strong_password}")
    
    is_valid, errors = pwd_manager.validate_password(strong_password)
    print(f"Valid: {is_valid}")
    
    strength = pwd_manager.check_strength(strong_password)
    print(f"Strength: {strength.value}")
    
    # Hash the strong password
    hashed, salt = pwd_manager.hash_password(strong_password)
    print(f"Hashed (hex): {hashed.hex()[:32]}...")
    print(f"Salt (hex): {salt.hex()}")
    
    # Verify password
    is_correct = pwd_manager.verify_password(strong_password, hashed, salt)
    print(f"Password verification: {is_correct}")


def example_3_key_management():
    """Example 3: Key management with rotation policies."""
    print("\n=== Example 3: Key Management ===")
    
    key_manager = KeyManager()
    
    # Generate keys with different rotation policies
    print("\nGenerating keys with different rotation policies:")
    
    payment_key_id = key_manager.generate_key(
        key_size=32,
        rotation_policy=KeyRotationPolicy.MONTHLY,
        tags={"service": "payments", "env": "production"},
    )
    print(f"Payment key ID: {payment_key_id}")
    
    user_key_id = key_manager.generate_key(
        key_size=32,
        rotation_policy=KeyRotationPolicy.WEEKLY,
        tags={"service": "users", "env": "production"},
    )
    print(f"User key ID: {user_key_id}")
    
    backup_key_id = key_manager.generate_key(
        key_size=32,
        rotation_policy=KeyRotationPolicy.NEVER,
        tags={"service": "backup", "env": "production"},
    )
    print(f"Backup key ID: {backup_key_id}")
    
    # List active keys
    active_keys = key_manager.list_active_keys()
    print(f"\nActive keys: {len(active_keys)}")
    
    # Find keys by tag
    payment_keys = key_manager.list_keys_by_tag("service", "payments")
    print(f"Payment service keys: {len(payment_keys)}")
    
    # Get key metadata
    metadata = key_manager.get_metadata(payment_key_id)
    print(f"\nPayment key metadata:")
    print(f"  Algorithm: {metadata.algorithm}")
    print(f"  Rotation policy: {metadata.rotation_policy.value}")
    print(f"  Created: {metadata.created_at.isoformat()}")
    print(f"  Next rotation: {metadata.next_rotation.isoformat()}")
    
    # Rotate a key
    print(f"\nRotating payment key...")
    new_key_id = key_manager.rotate_key(payment_key_id)
    print(f"New key ID: {new_key_id}")
    
    # Old key is now inactive
    old_key = key_manager.get_key(payment_key_id)
    new_key = key_manager.get_key(new_key_id)
    print(f"Old key retrievable: {old_key is not None}")
    print(f"New key retrievable: {new_key is not None}")


def example_4_aes_cipher_wrapper():
    """Example 4: Using the AES cipher wrapper."""
    print("\n=== Example 4: AES Cipher Wrapper ===")
    
    sdk = EncryptionSDK()
    
    # GCM Mode (authenticated encryption)
    print("\nGCM Mode (Authenticated Encryption):")
    gcm_config = AESConfig(mode=AESMode.GCM)
    gcm_cipher = AESCipher(gcm_config)
    
    key = sdk.generate_key()
    plaintext = "Transfer $5000 to account XYZ"
    
    encrypted = gcm_cipher.encrypt(plaintext, key)
    print(f"Plaintext: {plaintext}")
    print(f"Algorithm: {encrypted.algorithm}")
    print(f"Has authentication tag: {encrypted.tag is not None}")
    
    decrypted = gcm_cipher.decrypt(encrypted, key)
    print(f"Decrypted: {decrypted.plaintext}")
    print(f"Verified: {decrypted.verified}")
    
    # CBC Mode (traditional block cipher)
    print("\nCBC Mode (Traditional Block Cipher):")
    cbc_config = AESConfig(mode=AESMode.CBC)
    cbc_cipher = AESCipher(cbc_config)
    
    encrypted = cbc_cipher.encrypt(plaintext, key)
    print(f"Algorithm: {encrypted.algorithm}")
    print(f"Has authentication tag: {encrypted.tag is not None}")
    
    decrypted = cbc_cipher.decrypt(encrypted, key)
    print(f"Decrypted: {decrypted.plaintext}")


def example_5_password_generation():
    """Example 5: Secure password generation."""
    print("\n=== Example 5: Password Generation ===")
    
    pwd_manager = PasswordManager()
    
    print("\nGenerating secure passwords of different lengths:")
    for length in [12, 16, 20]:
        password = pwd_manager.generate_password(length=length)
        strength = pwd_manager.check_strength(password)
        print(f"  {length} chars: {password} (Strength: {strength.value})")


def example_6_banking_scenario():
    """Example 6: Complete banking transaction scenario."""
    print("\n=== Example 6: Banking Transaction Scenario ===")
    
    # Setup
    sdk = EncryptionSDK()
    key_manager = KeyManager()
    pwd_manager = PasswordManager()
    
    # 1. User registration with strong password
    print("\n1. User Registration:")
    username = "john_doe"
    password = pwd_manager.generate_password(length=16)
    
    is_valid, errors = pwd_manager.validate_password(password)
    print(f"   Username: {username}")
    print(f"   Password strength: {pwd_manager.check_strength(password).value}")
    
    hashed_pwd, salt = pwd_manager.hash_password(password)
    print(f"   Password hashed: Yes")
    
    # 2. Generate encryption key for user data
    print("\n2. Key Generation:")
    user_key_id = key_manager.generate_key(
        rotation_policy=KeyRotationPolicy.MONTHLY,
        tags={"user": username, "type": "personal_data"},
    )
    print(f"   Generated key for user data: {user_key_id}")
    
    # 3. Encrypt sensitive transaction data
    print("\n3. Transaction Encryption:")
    transaction = {
        "from_account": "1234567890",
        "to_account": "0987654321",
        "amount": 5000.00,
        "currency": "USD",
    }
    import json
    transaction_json = json.dumps(transaction)
    
    user_key = key_manager.get_key(user_key_id)
    encrypted_tx = sdk.encrypt_aes_gcm(transaction_json, user_key)
    
    print(f"   Original: {transaction_json}")
    print(f"   Encrypted: {encrypted_tx.ciphertext.hex()[:32]}...")
    print(f"   Algorithm: {encrypted_tx.algorithm}")
    
    # 4. Decrypt transaction
    print("\n4. Transaction Decryption:")
    decrypted_tx = sdk.decrypt_aes_gcm(
        encrypted_tx.ciphertext,
        user_key,
        encrypted_tx.iv,
        encrypted_tx.tag,
    )
    
    tx_data = json.loads(decrypted_tx.plaintext)
    print(f"   Decrypted: {tx_data}")
    
    # 5. Key rotation
    print("\n5. Key Rotation:")
    needs_rotation = key_manager.check_rotation_needed()
    print(f"   Keys needing rotation: {len(needs_rotation)}")
    
    # Simulate rotation
    new_key_id = key_manager.rotate_key(user_key_id)
    print(f"   New key generated: {new_key_id}")
    print(f"   Old key active: {key_manager.get_key(user_key_id) is not None}")
    print(f"   New key active: {key_manager.get_key(new_key_id) is not None}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Banking Encryption SDK Examples")
    print("=" * 60)
    
    example_1_basic_encryption()
    example_2_password_management()
    example_3_key_management()
    example_4_aes_cipher_wrapper()
    example_5_password_generation()
    example_6_banking_scenario()
    
    print("\n" + "=" * 60)
    print("Examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
