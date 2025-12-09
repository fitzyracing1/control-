"""Tests for Encryption API endpoints."""

import pytest
from fastapi.testclient import TestClient
import json

from src.main import app

client = TestClient(app)


class TestEncryptionEndpoints:
    """Test encryption/decryption endpoints."""
    
    def test_encrypt_endpoint(self):
        """Test encryption endpoint."""
        response = client.post(
            "/api/encryption/encrypt",
            json={"plaintext": "test data"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ciphertext" in data
        assert "iv" in data
        assert "tag" in data
        assert "key" in data
    
    def test_encrypt_with_provided_key(self):
        """Test encryption with provided key."""
        # First generate a key
        response = client.post(
            "/api/encryption/encrypt",
            json={"plaintext": "test"}
        )
        key = response.json()["key"]
        
        # Use the key for encryption
        response = client.post(
            "/api/encryption/encrypt",
            json={
                "plaintext": "test data",
                "key": key
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["key"] is None  # Key not returned when provided
    
    def test_encrypt_aes_cbc(self):
        """Test CBC mode encryption."""
        response = client.post(
            "/api/encryption/encrypt",
            json={
                "plaintext": "test data",
                "algorithm": "AES-256-CBC"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["algorithm"] == "AES-256-CBC"
        assert data["tag"] is None  # CBC doesn't use tags
    
    def test_decrypt_endpoint(self):
        """Test decryption endpoint."""
        # First encrypt
        encrypt_response = client.post(
            "/api/encryption/encrypt",
            json={"plaintext": "secret message"}
        )
        encrypted = encrypt_response.json()
        
        # Then decrypt
        decrypt_response = client.post(
            "/api/encryption/decrypt",
            json={
                "ciphertext": encrypted["ciphertext"],
                "key": encrypted["key"],
                "iv": encrypted["iv"],
                "tag": encrypted["tag"],
                "algorithm": "AES-256-GCM"
            }
        )
        
        assert decrypt_response.status_code == 200
        data = decrypt_response.json()
        assert data["success"] is True
        assert data["plaintext"] == "secret message"
        assert data["verified"] is True
    
    def test_decrypt_cbc(self):
        """Test CBC decryption."""
        # Encrypt with CBC
        encrypt_response = client.post(
            "/api/encryption/encrypt",
            json={
                "plaintext": "secret data",
                "algorithm": "AES-256-CBC"
            }
        )
        encrypted = encrypt_response.json()
        
        # Decrypt
        decrypt_response = client.post(
            "/api/encryption/decrypt",
            json={
                "ciphertext": encrypted["ciphertext"],
                "key": encrypted["key"],
                "iv": encrypted["iv"],
                "algorithm": "AES-256-CBC"
            }
        )
        
        assert decrypt_response.status_code == 200
        data = decrypt_response.json()
        assert data["plaintext"] == "secret data"
    
    def test_decrypt_invalid_key(self):
        """Test decryption with invalid key."""
        # Encrypt
        encrypt_response = client.post(
            "/api/encryption/encrypt",
            json={"plaintext": "test"}
        )
        encrypted = encrypt_response.json()
        
        # Try to decrypt with wrong key
        wrong_key = "a" * 64  # 32 bytes hex
        
        decrypt_response = client.post(
            "/api/encryption/decrypt",
            json={
                "ciphertext": encrypted["ciphertext"],
                "key": wrong_key,
                "iv": encrypted["iv"],
                "tag": encrypted["tag"],
            }
        )
        
        assert decrypt_response.status_code == 400
        assert "failed" in decrypt_response.json()["detail"].lower()


class TestKeyManagementEndpoints:
    """Test key management endpoints."""
    
    def test_generate_key_endpoint(self):
        """Test key generation endpoint."""
        response = client.post(
            "/api/encryption/keys/generate",
            json={
                "key_size": 32,
                "rotation_policy": "MONTHLY"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "key_id" in data
        assert data["algorithm"] == "AES-256"
        assert data["key_size"] == 32
        assert data["rotation_policy"] == "monthly"
    
    def test_generate_key_with_tags(self):
        """Test key generation with tags."""
        response = client.post(
            "/api/encryption/keys/generate",
            json={
                "key_size": 32,
                "rotation_policy": "WEEKLY",
                "tags": {"app": "banking", "env": "production"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["tags"]["app"] == "banking"
        assert data["tags"]["env"] == "production"
    
    def test_list_keys_endpoint(self):
        """Test listing active keys."""
        # Generate a key first
        client.post(
            "/api/encryption/keys/generate",
            json={"rotation_policy": "MONTHLY"}
        )
        
        # List keys
        response = client.get("/api/encryption/keys")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["count"] >= 1
        assert isinstance(data["active_keys"], list)
    
    def test_get_key_status_endpoint(self):
        """Test getting key status."""
        # Generate a key
        gen_response = client.post(
            "/api/encryption/keys/generate",
            json={"rotation_policy": "MONTHLY"}
        )
        key_id = gen_response.json()["key_id"]
        
        # Get status
        response = client.get(f"/api/encryption/keys/{key_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["key_id"] == key_id
        assert data["active"] is True
        assert data["algorithm"] == "AES-256"
    
    def test_get_key_status_not_found(self):
        """Test getting status of non-existent key."""
        response = client.get("/api/encryption/keys/invalid_key_id")
        
        assert response.status_code == 404
    
    def test_rotate_key_endpoint(self):
        """Test key rotation endpoint."""
        # Generate a key
        gen_response = client.post(
            "/api/encryption/keys/generate",
            json={"rotation_policy": "MONTHLY"}
        )
        key_id = gen_response.json()["key_id"]
        
        # Rotate it
        response = client.post(
            "/api/encryption/keys/rotate",
            json={"key_id": key_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["old_key_id"] == key_id
        assert data["new_key_id"] != key_id


class TestPasswordEndpoints:
    """Test password management endpoints."""
    
    def test_hash_password_endpoint(self):
        """Test password hashing endpoint."""
        response = client.post(
            "/api/encryption/password/hash",
            json={"password": "MySecurePassword123!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "hashed" in data
        assert "salt" in data
    
    def test_verify_password_endpoint(self):
        """Test password verification endpoint."""
        # Hash a password
        hash_response = client.post(
            "/api/encryption/password/hash",
            json={"password": "MyPassword123!"}
        )
        hashed = hash_response.json()["hashed"]
        salt = hash_response.json()["salt"]
        
        # Verify correct password
        verify_response = client.post(
            "/api/encryption/password/verify",
            json={
                "password": "MyPassword123!",
                "hashed": hashed,
                "salt": salt
            }
        )
        
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["success"] is True
        assert data["valid"] is True
    
    def test_verify_password_wrong_password(self):
        """Test verification with wrong password."""
        # Hash a password
        hash_response = client.post(
            "/api/encryption/password/hash",
            json={"password": "MyPassword123!"}
        )
        hashed = hash_response.json()["hashed"]
        salt = hash_response.json()["salt"]
        
        # Verify wrong password
        verify_response = client.post(
            "/api/encryption/password/verify",
            json={
                "password": "WrongPassword123!",
                "hashed": hashed,
                "salt": salt
            }
        )
        
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["valid"] is False
    
    def test_validate_password_endpoint(self):
        """Test password validation endpoint."""
        response = client.post(
            "/api/encryption/password/validate",
            json={
                "password": "WeakPass",
                "min_length": 12
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["valid"] is False
        assert len(data["errors"]) > 0
    
    def test_validate_password_strong(self):
        """Test validation with strong password."""
        response = client.post(
            "/api/encryption/password/validate",
            json={
                "password": "MySecurePassword123!",
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_digits": True,
                "require_special": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["valid"] is True
        assert len(data["errors"]) == 0
    
    def test_strength_check_endpoint(self):
        """Test password strength check endpoint."""
        response = client.post(
            "/api/encryption/password/strength",
            json={"password": "MySecurePassword123!"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["strength"] in ["weak", "fair", "good", "strong", "very_strong"]
        assert isinstance(data["score"], int)
        assert 1 <= data["score"] <= 5
    
    def test_generate_password_endpoint(self):
        """Test password generation endpoint."""
        response = client.post(
            "/api/encryption/password/generate",
            json={"length": 16}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["password"]) == 16
        assert data["strength"] in ["weak", "fair", "good", "strong", "very_strong"]
    
    def test_generate_password_without_special(self):
        """Test password generation without special chars."""
        response = client.post(
            "/api/encryption/password/generate",
            json={
                "length": 12,
                "include_special": False
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["password"]) == 12


class TestEncryptionAPIHealth:
    """Test API health check."""
    
    def test_encryption_health_check(self):
        """Test encryption API health check."""
        response = client.get("/api/encryption/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "encryption-api"


class TestEncryptionAPIIntegration:
    """Integration tests for encryption API."""
    
    def test_end_to_end_encryption_flow(self):
        """Test complete encryption workflow."""
        # 1. Generate a key
        key_response = client.post(
            "/api/encryption/keys/generate",
            json={"rotation_policy": "MONTHLY"}
        )
        assert key_response.status_code == 200
        key_id = key_response.json()["key_id"]
        
        # 2. Encrypt data
        encrypt_response = client.post(
            "/api/encryption/encrypt",
            json={"plaintext": "sensitive transaction"}
        )
        assert encrypt_response.status_code == 200
        encrypted = encrypt_response.json()
        
        # 3. Decrypt data
        decrypt_response = client.post(
            "/api/encryption/decrypt",
            json={
                "ciphertext": encrypted["ciphertext"],
                "key": encrypted["key"],
                "iv": encrypted["iv"],
                "tag": encrypted["tag"],
            }
        )
        assert decrypt_response.status_code == 200
        assert decrypt_response.json()["plaintext"] == "sensitive transaction"
    
    def test_end_to_end_password_flow(self):
        """Test complete password workflow."""
        # 1. Generate a password
        gen_response = client.post(
            "/api/encryption/password/generate",
            json={"length": 16}
        )
        assert gen_response.status_code == 200
        password = gen_response.json()["password"]
        
        # 2. Hash password
        hash_response = client.post(
            "/api/encryption/password/hash",
            json={"password": password}
        )
        assert hash_response.status_code == 200
        hashed = hash_response.json()["hashed"]
        salt = hash_response.json()["salt"]
        
        # 3. Verify password
        verify_response = client.post(
            "/api/encryption/password/verify",
            json={
                "password": password,
                "hashed": hashed,
                "salt": salt
            }
        )
        assert verify_response.status_code == 200
        assert verify_response.json()["valid"] is True
    
    def test_multiple_keys_management(self):
        """Test managing multiple keys."""
        # Generate multiple keys
        key_ids = []
        for i in range(3):
            response = client.post(
                "/api/encryption/keys/generate",
                json={
                    "rotation_policy": "MONTHLY",
                    "tags": {"index": str(i)}
                }
            )
            key_ids.append(response.json()["key_id"])
        
        # List all keys
        list_response = client.get("/api/encryption/keys")
        assert list_response.status_code == 200
        assert list_response.json()["count"] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
