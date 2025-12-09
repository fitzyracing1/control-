# Encryption API Documentation

Complete REST API reference for the Banking Encryption SDK.

## Overview

The Encryption API provides REST endpoints for:
- **Encryption/Decryption** - AES-256-GCM and CBC modes
- **Key Management** - Generation, rotation, listing
- **Password Management** - Hashing, verification, validation, strength checking

**Base URL**: `/api/encryption`

## Authentication

Currently, no authentication is required. Add authentication/authorization as needed for production.

## Response Format

All endpoints return JSON responses with the following structure:

```json
{
  "success": true,
  "data": {}
}
```

Errors return HTTP status codes with error details in the response.

---

## Encryption Endpoints

### POST /encrypt

Encrypt plaintext data using AES-256-GCM or AES-256-CBC.

**Request:**
```json
{
  "plaintext": "Data to encrypt",
  "key": "optional_hex_encoded_key",
  "algorithm": "AES-256-GCM"
}
```

**Parameters:**
- `plaintext` (string, required): Data to encrypt
- `key` (string, optional): Hex-encoded 32-byte key. Generated if not provided
- `algorithm` (string): "AES-256-GCM" (default) or "AES-256-CBC"

**Response:**
```json
{
  "success": true,
  "algorithm": "AES-256-GCM",
  "ciphertext": "hex_encoded_ciphertext",
  "iv": "hex_encoded_initialization_vector",
  "tag": "hex_encoded_authentication_tag",
  "key": "hex_encoded_key_if_generated"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/encrypt \
  -H "Content-Type: application/json" \
  -d '{
    "plaintext": "Sensitive data",
    "algorithm": "AES-256-GCM"
  }'
```

### POST /decrypt

Decrypt ciphertext using AES-256-GCM or AES-256-CBC.

**Request:**
```json
{
  "ciphertext": "hex_encoded_ciphertext",
  "key": "hex_encoded_key",
  "iv": "hex_encoded_iv",
  "tag": "hex_encoded_tag",
  "algorithm": "AES-256-GCM"
}
```

**Parameters:**
- `ciphertext` (string, required): Hex-encoded encrypted data
- `key` (string, required): Hex-encoded encryption key
- `iv` (string, required): Hex-encoded initialization vector
- `tag` (string): Required for GCM, optional for CBC
- `algorithm` (string): "AES-256-GCM" (default) or "AES-256-CBC"

**Response:**
```json
{
  "success": true,
  "plaintext": "Original plaintext",
  "verified": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/decrypt \
  -H "Content-Type: application/json" \
  -d '{
    "ciphertext": "...",
    "key": "...",
    "iv": "...",
    "tag": "..."
  }'
```

---

## Key Management Endpoints

### POST /keys/generate

Generate a new encryption key with rotation policy.

**Request:**
```json
{
  "key_size": 32,
  "rotation_policy": "MONTHLY",
  "tags": {
    "app": "banking",
    "env": "production"
  }
}
```

**Parameters:**
- `key_size` (integer, default: 32): Key size in bytes (32 = AES-256)
- `rotation_policy` (string): "DAILY", "WEEKLY", "MONTHLY", "YEARLY", or "NEVER"
- `tags` (object, optional): Key tags for organization

**Response:**
```json
{
  "success": true,
  "key_id": "generated_key_id",
  "algorithm": "AES-256",
  "key_size": 32,
  "rotation_policy": "monthly",
  "tags": {
    "app": "banking",
    "env": "production"
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/keys/generate \
  -H "Content-Type: application/json" \
  -d '{
    "key_size": 32,
    "rotation_policy": "MONTHLY",
    "tags": {"service": "payments"}
  }'
```

### GET /keys

List all active encryption keys.

**Response:**
```json
{
  "success": true,
  "active_keys": ["key_id_1", "key_id_2", "key_id_3"],
  "count": 3
}
```

**Example:**
```bash
curl http://localhost:8000/api/encryption/keys
```

### GET /keys/{key_id}

Get status and metadata for a specific key.

**Parameters:**
- `key_id` (string, path): Key identifier

**Response:**
```json
{
  "success": true,
  "key_id": "key_id",
  "active": true,
  "algorithm": "AES-256",
  "key_size": 32,
  "created_at": "2025-12-09T16:30:00",
  "next_rotation": "2026-01-09T16:30:00",
  "tags": {
    "app": "banking"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/api/encryption/keys/abc123def456
```

### POST /keys/rotate

Rotate a key by generating a new one with the same policy.

**Request:**
```json
{
  "key_id": "key_to_rotate",
  "new_key_size": 32
}
```

**Parameters:**
- `key_id` (string, required): Key ID to rotate
- `new_key_size` (integer, optional): New key size (defaults to current)

**Response:**
```json
{
  "success": true,
  "old_key_id": "previous_key_id",
  "new_key_id": "new_key_id",
  "message": "Key rotated successfully..."
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/keys/rotate \
  -H "Content-Type: application/json" \
  -d '{
    "key_id": "abc123def456"
  }'
```

---

## Password Management Endpoints

### POST /password/hash

Hash a password using PBKDF2-SHA256.

**Request:**
```json
{
  "password": "UserPassword123!"
}
```

**Parameters:**
- `password` (string, required): Password to hash

**Response:**
```json
{
  "success": true,
  "hashed": "hex_encoded_hash",
  "salt": "hex_encoded_salt"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/password/hash \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MyPassword123!"
  }'
```

### POST /password/verify

Verify a password against its hash.

**Request:**
```json
{
  "password": "UserPassword123!",
  "hashed": "hex_encoded_hash",
  "salt": "hex_encoded_salt"
}
```

**Parameters:**
- `password` (string, required): Password to verify
- `hashed` (string, required): Hex-encoded hashed password
- `salt` (string, required): Hex-encoded salt

**Response:**
```json
{
  "success": true,
  "valid": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/password/verify \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MyPassword123!",
    "hashed": "...",
    "salt": "..."
  }'
```

### POST /password/validate

Validate a password against a security policy.

**Request:**
```json
{
  "password": "TestPassword123!",
  "min_length": 12,
  "require_uppercase": true,
  "require_lowercase": true,
  "require_digits": true,
  "require_special": true
}
```

**Parameters:**
- `password` (string, required): Password to validate
- `min_length` (integer, default: 12): Minimum length
- `require_uppercase` (boolean, default: true)
- `require_lowercase` (boolean, default: true)
- `require_digits` (boolean, default: true)
- `require_special` (boolean, default: true)

**Response:**
```json
{
  "success": true,
  "valid": true,
  "errors": []
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/password/validate \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MyPassword123!",
    "min_length": 12
  }'
```

### POST /password/strength

Check password strength (1-5 level assessment).

**Request:**
```json
{
  "password": "TestPassword123!"
}
```

**Parameters:**
- `password` (string, required): Password to check

**Response:**
```json
{
  "success": true,
  "strength": "strong",
  "score": 4
}
```

**Strength Levels:**
- `weak` (score: 1)
- `fair` (score: 2)
- `good` (score: 3)
- `strong` (score: 4)
- `very_strong` (score: 5)

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/password/strength \
  -H "Content-Type: application/json" \
  -d '{
    "password": "MySecurePassword123!"
  }'
```

### POST /password/generate

Generate a secure random password.

**Request:**
```json
{
  "length": 16,
  "include_special": true
}
```

**Parameters:**
- `length` (integer, default: 16): Password length (8-128 characters)
- `include_special` (boolean, default: true): Include special characters

**Response:**
```json
{
  "success": true,
  "password": "GeneratedPassword123!",
  "strength": "very_strong"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/encryption/password/generate \
  -H "Content-Type: application/json" \
  -d '{
    "length": 20,
    "include_special": true
  }'
```

---

## Health Check

### GET /health

Health check endpoint for the encryption API.

**Response:**
```json
{
  "status": "healthy",
  "service": "encryption-api",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:8000/api/encryption/health
```

---

## Error Handling

Errors are returned with appropriate HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 404 | Not Found (key/resource doesn't exist) |
| 500 | Internal Server Error |

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Example Error:**
```bash
curl -X POST http://localhost:8000/api/encryption/decrypt \
  -H "Content-Type: application/json" \
  -d '{
    "ciphertext": "invalid"
  }'

# Response:
{
  "detail": "Decryption failed: invalid literal for int() with base 16: 'invalid'"
}
```

---

## Code Examples

### Python - Using Requests

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/encryption"

# Encrypt data
response = requests.post(f"{BASE_URL}/encrypt", json={
    "plaintext": "Secret message"
})
encrypted = response.json()

# Decrypt data
response = requests.post(f"{BASE_URL}/decrypt", json={
    "ciphertext": encrypted["ciphertext"],
    "key": encrypted["key"],
    "iv": encrypted["iv"],
    "tag": encrypted["tag"]
})
print(response.json()["plaintext"])

# Hash password
response = requests.post(f"{BASE_URL}/password/hash", json={
    "password": "MyPassword123!"
})
hashed = response.json()

# Verify password
response = requests.post(f"{BASE_URL}/password/verify", json={
    "password": "MyPassword123!",
    "hashed": hashed["hashed"],
    "salt": hashed["salt"]
})
print(f"Valid: {response.json()['valid']}")
```

### JavaScript - Using Fetch

```javascript
const BASE_URL = "http://localhost:8000/api/encryption";

// Encrypt data
const encryptResponse = await fetch(`${BASE_URL}/encrypt`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ plaintext: "Secret message" })
});
const encrypted = await encryptResponse.json();

// Decrypt data
const decryptResponse = await fetch(`${BASE_URL}/decrypt`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    ciphertext: encrypted.ciphertext,
    key: encrypted.key,
    iv: encrypted.iv,
    tag: encrypted.tag
  })
});
const decrypted = await decryptResponse.json();
console.log(decrypted.plaintext);

// Hash password
const hashResponse = await fetch(`${BASE_URL}/password/hash`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ password: "MyPassword123!" })
});
const hashed = await hashResponse.json();
```

### cURL - Command Line

```bash
# Encrypt
curl -X POST http://localhost:8000/api/encryption/encrypt \
  -H "Content-Type: application/json" \
  -d '{"plaintext": "Secret"}' | jq .

# Generate key
curl -X POST http://localhost:8000/api/encryption/keys/generate \
  -H "Content-Type: application/json" \
  -d '{"rotation_policy": "MONTHLY"}' | jq .

# Hash password
curl -X POST http://localhost:8000/api/encryption/password/hash \
  -H "Content-Type: application/json" \
  -d '{"password": "MyPassword123!"}' | jq .

# Check password strength
curl -X POST http://localhost:8000/api/encryption/password/strength \
  -H "Content-Type: application/json" \
  -d '{"password": "MyPassword123!"}' | jq .
```

---

## Rate Limiting

Currently, no rate limiting is implemented. Add rate limiting middleware as needed for production.

## CORS

CORS is enabled for all origins. Configure allowed origins in production.

## Version

API Version: 1.0.0

---

## Support

For issues or questions:
1. Check the endpoint documentation above
2. Review error messages returned by the API
3. Check SDK documentation in `docs/ENCRYPTION_SDK.md`
4. Review test cases in `tests/test_encryption_api.py`
