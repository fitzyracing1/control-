"""Key management utilities for the Encryption SDK."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, List
import secrets
from pathlib import Path
import json


class KeyRotationPolicy(Enum):
    """Key rotation policies."""
    NEVER = "never"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class KeyMetadata:
    """Metadata for managed keys."""
    key_id: str
    created_at: datetime
    algorithm: str
    key_size: int
    rotation_policy: KeyRotationPolicy
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    active: bool = True
    tags: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "key_id": self.key_id,
            "created_at": self.created_at.isoformat(),
            "algorithm": self.algorithm,
            "key_size": self.key_size,
            "rotation_policy": self.rotation_policy.value,
            "last_rotated": self.last_rotated.isoformat() if self.last_rotated else None,
            "next_rotation": self.next_rotation.isoformat() if self.next_rotation else None,
            "active": self.active,
            "tags": self.tags,
        }


class KeyManager:
    """
    Manages cryptographic keys with rotation policies and metadata.
    
    Provides secure key generation, storage, and rotation capabilities
    for banking applications.
    """
    
    def __init__(self):
        """Initialize key manager."""
        self._keys: Dict[str, bytes] = {}
        self._metadata: Dict[str, KeyMetadata] = {}
    
    def generate_key(
        self,
        key_size: int = 32,
        rotation_policy: KeyRotationPolicy = KeyRotationPolicy.MONTHLY,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate and store a new cryptographic key.
        
        Args:
            key_size: Size of key in bytes (default 32 for AES-256)
            rotation_policy: Key rotation policy
            tags: Optional tags for key identification
            
        Returns:
            Key ID for later retrieval
        """
        key_id = secrets.token_hex(16)
        key = secrets.token_bytes(key_size)
        
        now = datetime.utcnow()
        next_rotation = self._calculate_next_rotation(now, rotation_policy)
        
        metadata = KeyMetadata(
            key_id=key_id,
            created_at=now,
            algorithm="AES-256" if key_size == 32 else f"AES-{key_size * 8}",
            key_size=key_size,
            rotation_policy=rotation_policy,
            next_rotation=next_rotation,
            tags=tags or {},
        )
        
        self._keys[key_id] = key
        self._metadata[key_id] = metadata
        
        return key_id
    
    def get_key(self, key_id: str) -> Optional[bytes]:
        """
        Retrieve a key by ID.
        
        Args:
            key_id: Key identifier
            
        Returns:
            Key bytes if found and active, None otherwise
        """
        metadata = self._metadata.get(key_id)
        if metadata and metadata.active:
            return self._keys.get(key_id)
        return None
    
    def get_metadata(self, key_id: str) -> Optional[KeyMetadata]:
        """
        Retrieve key metadata.
        
        Args:
            key_id: Key identifier
            
        Returns:
            KeyMetadata if found, None otherwise
        """
        return self._metadata.get(key_id)
    
    def rotate_key(
        self,
        key_id: str,
        new_key_size: Optional[int] = None,
    ) -> str:
        """
        Rotate a key by generating a new one with the same policy.
        
        Args:
            key_id: Key to rotate
            new_key_size: New key size (defaults to current size)
            
        Returns:
            New key ID
            
        Raises:
            ValueError: If key not found
        """
        old_metadata = self._metadata.get(key_id)
        if not old_metadata:
            raise ValueError(f"Key not found: {key_id}")
        
        # Generate new key
        new_key_size = new_key_size or old_metadata.key_size
        new_key_id = self.generate_key(
            key_size=new_key_size,
            rotation_policy=old_metadata.rotation_policy,
            tags=old_metadata.tags,
        )
        
        # Mark old key as inactive
        old_metadata.active = False
        old_metadata.last_rotated = datetime.utcnow()
        
        return new_key_id
    
    def deactivate_key(self, key_id: str) -> bool:
        """
        Deactivate a key (soft delete).
        
        Args:
            key_id: Key to deactivate
            
        Returns:
            True if successful, False if key not found
        """
        metadata = self._metadata.get(key_id)
        if metadata:
            metadata.active = False
            return True
        return False
    
    def list_active_keys(self) -> List[str]:
        """
        List all active key IDs.
        
        Returns:
            List of active key IDs
        """
        return [
            key_id
            for key_id, metadata in self._metadata.items()
            if metadata.active
        ]
    
    def list_keys_by_tag(self, tag: str, value: str) -> List[str]:
        """
        Find keys by tag.
        
        Args:
            tag: Tag name
            value: Tag value
            
        Returns:
            List of matching key IDs
        """
        return [
            key_id
            for key_id, metadata in self._metadata.items()
            if metadata.active and metadata.tags.get(tag) == value
        ]
    
    def check_rotation_needed(self) -> List[str]:
        """
        Check which keys need rotation.
        
        Returns:
            List of key IDs that need rotation
        """
        now = datetime.utcnow()
        needs_rotation = []
        
        for key_id, metadata in self._metadata.items():
            if (
                metadata.active
                and metadata.next_rotation
                and metadata.next_rotation <= now
            ):
                needs_rotation.append(key_id)
        
        return needs_rotation
    
    def _calculate_next_rotation(
        self,
        from_date: datetime,
        policy: KeyRotationPolicy,
    ) -> Optional[datetime]:
        """Calculate next rotation date based on policy."""
        if policy == KeyRotationPolicy.NEVER:
            return None
        elif policy == KeyRotationPolicy.DAILY:
            return from_date + timedelta(days=1)
        elif policy == KeyRotationPolicy.WEEKLY:
            return from_date + timedelta(weeks=1)
        elif policy == KeyRotationPolicy.MONTHLY:
            return from_date + timedelta(days=30)
        elif policy == KeyRotationPolicy.YEARLY:
            return from_date + timedelta(days=365)
        return None
    
    def export_metadata(self) -> Dict[str, Dict]:
        """
        Export all key metadata (keys are never exported).
        
        Returns:
            Dictionary of key metadata
        """
        return {
            key_id: metadata.to_dict()
            for key_id, metadata in self._metadata.items()
        }
    
    def save_metadata(self, filepath: str) -> None:
        """
        Save key metadata to a JSON file (for recovery purposes).
        
        Args:
            filepath: Path to save metadata
        """
        metadata_dict = self.export_metadata()
        with open(filepath, "w") as f:
            json.dump(metadata_dict, f, indent=2)
