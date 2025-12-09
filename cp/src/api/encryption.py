"""Encryption API endpoints for banking operations."""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json

from src.sdk import (
    EncryptionSDK,
    KeyManager,
    PasswordManager,
    PasswordPolicy,
    KeyRotationPolicy,
    EncryptionResult,
)

router = APIRouter(prefix="/api/encryption", tags=["encryption"])

# Global SDK instances
_sdk_instance = None
_key_manager_instance = None
_password_manager_instance = None


def get_sdk() -> EncryptionSDK:
    """Get or create EncryptionSDK instance."""
    global _sdk_instance
    if _sdk_instance is None:
        _sdk_instance = EncryptionSDK()
    return _sdk_instance


def get_key_manager() -> KeyManager:
    """Get or create KeyManager instance."""
    global _key_manager_instance
    if _key_manager_instance is None:
        _key_manager_instance = KeyManager()
    return _key_manager_instance


def get_password_manager() -> PasswordManager:
    """Get or create PasswordManager instance."""
    global _password_manager_instance
    if _password_manager_instance is None:
        _password_manager_instance = PasswordManager()
    return _password_manager_instance


# ============================================================================
# Request/Response Models
# ============================================================================


class EncryptRequest(BaseModel):
    """Request model for encryption."""
    plaintext: str = Field(..., description="Data to encrypt")
    key: Optional[str] = Field(None, description="Hex-encoded encryption key (generates if not provided)")
    algorithm: str = Field("AES-256-GCM", description="Encryption algorithm")


class EncryptResponse(BaseModel):
    """Response model for encryption."""
    success: bool
    algorithm: str
    ciphertext: str = Field(..., description="Hex-encoded ciphertext")
    iv: str = Field(..., description="Hex-encoded initialization vector")
    tag: Optional[str] = Field(None, description="Hex-encoded authentication tag (GCM only)")
    key: Optional[str] = Field(None, description="Generated key if not provided")


class DecryptRequest(BaseModel):
    """Request model for decryption."""
    ciphertext: str = Field(..., description="Hex-encoded ciphertext")
    key: str = Field(..., description="Hex-encoded encryption key")
    iv: str = Field(..., description="Hex-encoded initialization vector")
    tag: Optional[str] = Field(None, description="Hex-encoded authentication tag (GCM)")
    algorithm: str = Field("AES-256-GCM", description="Decryption algorithm")


class DecryptResponse(BaseModel):
    """Response model for decryption."""
    success: bool
    plaintext: str
    verified: bool = Field(..., description="Authentication verification status")


class KeyGenerateRequest(BaseModel):
    """Request model for key generation."""
    key_size: int = Field(32, description="Key size in bytes (default 32 for AES-256)")
    rotation_policy: str = Field("MONTHLY", description="Rotation policy")
    tags: Optional[Dict[str, str]] = Field(None, description="Key tags for organization")


class KeyGenerateResponse(BaseModel):
    """Response model for key generation."""
    success: bool
    key_id: str
    algorithm: str
    key_size: int
    rotation_policy: str
    tags: Optional[Dict[str, str]]


class KeyRotateRequest(BaseModel):
    """Request model for key rotation."""
    key_id: str = Field(..., description="Key ID to rotate")
    new_key_size: Optional[int] = Field(None, description="New key size (defaults to current)")


class KeyRotateResponse(BaseModel):
    """Response model for key rotation."""
    success: bool
    old_key_id: str
    new_key_id: str
    message: str


class KeyListResponse(BaseModel):
    """Response model for listing keys."""
    success: bool
    active_keys: list = Field(..., description="List of active key IDs")
    count: int


class PasswordHashRequest(BaseModel):
    """Request model for password hashing."""
    password: str = Field(..., description="Password to hash", min_length=1)


class PasswordHashResponse(BaseModel):
    """Response model for password hashing."""
    success: bool
    hashed: str = Field(..., description="Hex-encoded hashed password")
    salt: str = Field(..., description="Hex-encoded salt")


class PasswordVerifyRequest(BaseModel):
    """Request model for password verification."""
    password: str = Field(..., description="Password to verify")
    hashed: str = Field(..., description="Hex-encoded hashed password")
    salt: str = Field(..., description="Hex-encoded salt")


class PasswordVerifyResponse(BaseModel):
    """Response model for password verification."""
    success: bool
    valid: bool = Field(..., description="Whether password matches")


class PasswordValidateRequest(BaseModel):
    """Request model for password validation."""
    password: str = Field(..., description="Password to validate")
    min_length: int = Field(12, description="Minimum password length")
    require_uppercase: bool = Field(True, description="Require uppercase letters")
    require_lowercase: bool = Field(True, description="Require lowercase letters")
    require_digits: bool = Field(True, description="Require digits")
    require_special: bool = Field(True, description="Require special characters")


class PasswordValidateResponse(BaseModel):
    """Response model for password validation."""
    success: bool
    valid: bool = Field(..., description="Whether password meets policy")
    errors: list = Field(default_factory=list, description="Validation errors")


class PasswordStrengthRequest(BaseModel):
    """Request model for password strength checking."""
    password: str = Field(..., description="Password to check")


class PasswordStrengthResponse(BaseModel):
    """Response model for password strength."""
    success: bool
    strength: str = Field(..., description="Strength level (weak, fair, good, strong, very_strong)")
    score: int = Field(..., description="Strength score")


class PasswordGenerateRequest(BaseModel):
    """Request model for password generation."""
    length: int = Field(16, description="Password length", ge=8, le=128)
    include_special: bool = Field(True, description="Include special characters")


class PasswordGenerateResponse(BaseModel):
    """Response model for password generation."""
    success: bool
    password: str = Field(..., description="Generated password")
    strength: str = Field(..., description="Password strength level")


class KeyStatusResponse(BaseModel):
    """Response model for key status."""
    success: bool
    key_id: str
    active: bool
    algorithm: str
    key_size: int
    created_at: str
    next_rotation: Optional[str]
    tags: Optional[Dict[str, str]]


# ============================================================================
# Encryption Endpoints
# ============================================================================


@router.post("/encrypt", response_model=EncryptResponse)
async def encrypt_data(
    request: EncryptRequest,
    sdk: EncryptionSDK = Depends(get_sdk),
) -> EncryptResponse:
    """
    Encrypt plaintext data using AES-256-GCM or AES-256-CBC.
    
    - **plaintext**: Data to encrypt
    - **key**: Optional hex-encoded encryption key (generates if not provided)
    - **algorithm**: Encryption algorithm (AES-256-GCM or AES-256-CBC)
    """
    try:
        # Use provided key or generate new one
        if request.key:
            key = bytes.fromhex(request.key)
        else:
            key = sdk.generate_key()
        
        # Encrypt based on algorithm
        if request.algorithm == "AES-256-GCM":
            result = sdk.encrypt_aes_gcm(request.plaintext, key)
        elif request.algorithm == "AES-256-CBC":
            result = sdk.encrypt_aes_cbc(request.plaintext, key)
        else:
            raise ValueError(f"Unsupported algorithm: {request.algorithm}")
        
        return EncryptResponse(
            success=True,
            algorithm=result.algorithm,
            ciphertext=result.ciphertext.hex(),
            iv=result.iv.hex(),
            tag=result.tag.hex() if result.tag else None,
            key=key.hex() if not request.key else None,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Encryption failed: {str(e)}",
        )


@router.post("/decrypt", response_model=DecryptResponse)
async def decrypt_data(
    request: DecryptRequest,
    sdk: EncryptionSDK = Depends(get_sdk),
) -> DecryptResponse:
    """
    Decrypt ciphertext data using AES-256-GCM or AES-256-CBC.
    
    - **ciphertext**: Hex-encoded encrypted data
    - **key**: Hex-encoded encryption key
    - **iv**: Hex-encoded initialization vector
    - **tag**: Hex-encoded authentication tag (required for GCM)
    - **algorithm**: Decryption algorithm
    """
    try:
        key = bytes.fromhex(request.key)
        iv = bytes.fromhex(request.iv)
        ciphertext = bytes.fromhex(request.ciphertext)
        
        # Decrypt based on algorithm
        if request.algorithm == "AES-256-GCM":
            if not request.tag:
                raise ValueError("Tag required for GCM decryption")
            tag = bytes.fromhex(request.tag)
            result = sdk.decrypt_aes_gcm(ciphertext, key, iv, tag)
        elif request.algorithm == "AES-256-CBC":
            result = sdk.decrypt_aes_cbc(ciphertext, key, iv)
        else:
            raise ValueError(f"Unsupported algorithm: {request.algorithm}")
        
        return DecryptResponse(
            success=True,
            plaintext=result.plaintext,
            verified=result.verified,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decryption failed: {str(e)}",
        )


# ============================================================================
# Key Management Endpoints
# ============================================================================


@router.post("/keys/generate", response_model=KeyGenerateResponse)
async def generate_key(
    request: KeyGenerateRequest,
    key_manager: KeyManager = Depends(get_key_manager),
) -> KeyGenerateResponse:
    """
    Generate a new encryption key with rotation policy.
    
    - **key_size**: Size in bytes (default 32 for AES-256)
    - **rotation_policy**: DAILY, WEEKLY, MONTHLY, YEARLY, or NEVER
    - **tags**: Optional tags for key organization
    """
    try:
        # Parse rotation policy
        policy = KeyRotationPolicy[request.rotation_policy.upper()]
        
        # Generate key
        key_id = key_manager.generate_key(
            key_size=request.key_size,
            rotation_policy=policy,
            tags=request.tags,
        )
        
        metadata = key_manager.get_metadata(key_id)
        
        return KeyGenerateResponse(
            success=True,
            key_id=key_id,
            algorithm=metadata.algorithm,
            key_size=metadata.key_size,
            rotation_policy=metadata.rotation_policy.value,
            tags=metadata.tags,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Key generation failed: {str(e)}",
        )


@router.get("/keys/{key_id}", response_model=KeyStatusResponse)
async def get_key_status(
    key_id: str,
    key_manager: KeyManager = Depends(get_key_manager),
) -> KeyStatusResponse:
    """
    Get the status and metadata of a specific key.
    
    - **key_id**: Key identifier
    """
    try:
        metadata = key_manager.get_metadata(key_id)
        
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Key not found: {key_id}",
            )
        
        return KeyStatusResponse(
            success=True,
            key_id=key_id,
            active=metadata.active,
            algorithm=metadata.algorithm,
            key_size=metadata.key_size,
            created_at=metadata.created_at.isoformat(),
            next_rotation=metadata.next_rotation.isoformat() if metadata.next_rotation else None,
            tags=metadata.tags,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get key status: {str(e)}",
        )


@router.get("/keys", response_model=KeyListResponse)
async def list_active_keys(
    key_manager: KeyManager = Depends(get_key_manager),
) -> KeyListResponse:
    """
    List all active encryption keys.
    """
    try:
        active_keys = key_manager.list_active_keys()
        
        return KeyListResponse(
            success=True,
            active_keys=active_keys,
            count=len(active_keys),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to list keys: {str(e)}",
        )


@router.post("/keys/rotate", response_model=KeyRotateResponse)
async def rotate_key(
    request: KeyRotateRequest,
    key_manager: KeyManager = Depends(get_key_manager),
) -> KeyRotateResponse:
    """
    Rotate a key by generating a new one with same policy.
    
    - **key_id**: Key to rotate
    - **new_key_size**: Optional new key size (defaults to current size)
    """
    try:
        old_key = key_manager.get_metadata(request.key_id)
        
        if not old_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Key not found: {request.key_id}",
            )
        
        new_key_id = key_manager.rotate_key(
            request.key_id,
            new_key_size=request.new_key_size,
        )
        
        return KeyRotateResponse(
            success=True,
            old_key_id=request.key_id,
            new_key_id=new_key_id,
            message=f"Key rotated successfully. Old: {request.key_id}, New: {new_key_id}",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Key rotation failed: {str(e)}",
        )


# ============================================================================
# Password Management Endpoints
# ============================================================================


@router.post("/password/hash", response_model=PasswordHashResponse)
async def hash_password(
    request: PasswordHashRequest,
    password_manager: PasswordManager = Depends(get_password_manager),
) -> PasswordHashResponse:
    """
    Hash a password using PBKDF2-SHA256.
    
    - **password**: Password to hash
    """
    try:
        hashed, salt = password_manager.hash_password(request.password)
        
        return PasswordHashResponse(
            success=True,
            hashed=hashed.hex(),
            salt=salt.hex(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password hashing failed: {str(e)}",
        )


@router.post("/password/verify", response_model=PasswordVerifyResponse)
async def verify_password(
    request: PasswordVerifyRequest,
    password_manager: PasswordManager = Depends(get_password_manager),
) -> PasswordVerifyResponse:
    """
    Verify a password against its hash.
    
    - **password**: Password to verify
    - **hashed**: Hex-encoded hashed password
    - **salt**: Hex-encoded salt
    """
    try:
        hashed = bytes.fromhex(request.hashed)
        salt = bytes.fromhex(request.salt)
        
        is_valid = password_manager.verify_password(
            request.password,
            hashed,
            salt,
        )
        
        return PasswordVerifyResponse(
            success=True,
            valid=is_valid,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password verification failed: {str(e)}",
        )


@router.post("/password/validate", response_model=PasswordValidateResponse)
async def validate_password(
    request: PasswordValidateRequest,
    password_manager: PasswordManager = Depends(get_password_manager),
) -> PasswordValidateResponse:
    """
    Validate a password against policy.
    
    - **password**: Password to validate
    - **min_length**: Minimum length requirement
    - **require_uppercase**: Require uppercase letters
    - **require_lowercase**: Require lowercase letters
    - **require_digits**: Require digits
    - **require_special**: Require special characters
    """
    try:
        # Create policy from request
        policy = PasswordPolicy(
            min_length=request.min_length,
            require_uppercase=request.require_uppercase,
            require_lowercase=request.require_lowercase,
            require_digits=request.require_digits,
            require_special=request.require_special,
        )
        
        # Create manager with policy
        manager = PasswordManager(policy)
        
        # Validate
        is_valid, errors = manager.validate_password(request.password)
        
        return PasswordValidateResponse(
            success=True,
            valid=is_valid,
            errors=errors,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password validation failed: {str(e)}",
        )


@router.post("/password/strength", response_model=PasswordStrengthResponse)
async def check_password_strength(
    request: PasswordStrengthRequest,
    password_manager: PasswordManager = Depends(get_password_manager),
) -> PasswordStrengthResponse:
    """
    Check password strength (1-5 level assessment).
    
    - **password**: Password to check
    """
    try:
        strength = password_manager.check_strength(request.password)
        
        # Map strength to score
        strength_scores = {
            "weak": 1,
            "fair": 2,
            "good": 3,
            "strong": 4,
            "very_strong": 5,
        }
        
        return PasswordStrengthResponse(
            success=True,
            strength=strength.value,
            score=strength_scores[strength.value],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Strength check failed: {str(e)}",
        )


@router.post("/password/generate", response_model=PasswordGenerateResponse)
async def generate_password(
    request: PasswordGenerateRequest,
    password_manager: PasswordManager = Depends(get_password_manager),
) -> PasswordGenerateResponse:
    """
    Generate a secure random password.
    
    - **length**: Password length (8-128 characters)
    - **include_special**: Include special characters
    """
    try:
        password = password_manager.generate_password(
            length=request.length,
            include_special=request.include_special,
        )
        
        strength = password_manager.check_strength(password)
        
        return PasswordGenerateResponse(
            success=True,
            password=password,
            strength=strength.value,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password generation failed: {str(e)}",
        )


# ============================================================================
# Health Check
# ============================================================================


@router.get("/health")
async def health_check():
    """Health check endpoint for encryption API."""
    return {
        "status": "healthy",
        "service": "encryption-api",
        "version": "1.0.0",
    }
