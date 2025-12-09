"""Password management utilities for the Encryption SDK."""

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional
import re

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import secrets


class PasswordStrength(Enum):
    """Password strength levels."""
    WEAK = "weak"
    FAIR = "fair"
    GOOD = "good"
    STRONG = "strong"
    VERY_STRONG = "very_strong"


@dataclass
class PasswordPolicy:
    """Password security policy."""
    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special: bool = True
    special_characters: str = "!@#$%^&*()-_=+[]{}|;:,.<>?"
    max_age_days: Optional[int] = None  # None = no expiration
    min_entropy_bits: float = 50.0


class PasswordManager:
    """
    Manages password security with hashing, validation, and strength checking.
    
    Provides:
    - Secure password hashing with PBKDF2
    - Password validation against policies
    - Strength checking
    - Entropy calculation
    """
    
    def __init__(self, policy: Optional[PasswordPolicy] = None):
        """
        Initialize password manager.
        
        Args:
            policy: Password policy (uses defaults if not provided)
        """
        self.policy = policy or PasswordPolicy()
        self.backend = default_backend()
    
    def hash_password(
        self,
        password: str,
        salt: Optional[bytes] = None,
    ) -> Tuple[bytes, bytes]:
        """
        Hash a password using PBKDF2-SHA256.
        
        Args:
            password: Password to hash
            salt: Salt for hashing (generated if not provided)
            
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend,
        )
        
        hashed = kdf.derive(password.encode())
        return hashed, salt
    
    def verify_password(
        self,
        password: str,
        hashed: bytes,
        salt: bytes,
    ) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Password to verify
            hashed: Hashed password
            salt: Salt used for hashing
            
        Returns:
            True if password matches, False otherwise
        """
        new_hashed, _ = self.hash_password(password, salt)
        return new_hashed == hashed
    
    def validate_password(self, password: str) -> Tuple[bool, list]:
        """
        Validate password against policy.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        if len(password) < self.policy.min_length:
            errors.append(
                f"Password must be at least {self.policy.min_length} characters long"
            )
        
        if self.policy.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.policy.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.policy.require_digits and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        if self.policy.require_special:
            special_pattern = f"[{re.escape(self.policy.special_characters)}]"
            if not re.search(special_pattern, password):
                errors.append("Password must contain at least one special character")
        
        entropy = self._calculate_entropy(password)
        if entropy < self.policy.min_entropy_bits:
            errors.append(
                f"Password entropy ({entropy:.1f} bits) is below minimum "
                f"({self.policy.min_entropy_bits:.1f} bits)"
            )
        
        return len(errors) == 0, errors
    
    def check_strength(self, password: str) -> PasswordStrength:
        """
        Check password strength.
        
        Args:
            password: Password to check
            
        Returns:
            PasswordStrength enum value
        """
        score = 0
        
        # Length scoring
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety scoring
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(f"[{re.escape(self.policy.special_characters)}]", password):
            score += 1
        
        # Entropy scoring
        entropy = self._calculate_entropy(password)
        if entropy >= 50:
            score += 1
        
        # Map score to strength
        if score <= 2:
            return PasswordStrength.WEAK
        elif score <= 4:
            return PasswordStrength.FAIR
        elif score <= 6:
            return PasswordStrength.GOOD
        elif score <= 7:
            return PasswordStrength.STRONG
        else:
            return PasswordStrength.VERY_STRONG
    
    def _calculate_entropy(self, password: str) -> float:
        """
        Calculate Shannon entropy of a password.
        
        Args:
            password: Password to analyze
            
        Returns:
            Entropy in bits
        """
        import math
        
        # Estimate alphabet size
        alphabet_size = 0
        if re.search(r"[a-z]", password):
            alphabet_size += 26
        if re.search(r"[A-Z]", password):
            alphabet_size += 26
        if re.search(r"\d", password):
            alphabet_size += 10
        if re.search(f"[{re.escape(self.policy.special_characters)}]", password):
            alphabet_size += len(self.policy.special_characters)
        
        if alphabet_size == 0:
            return 0.0
        
        entropy = len(password) * math.log2(alphabet_size)
        return entropy
    
    def generate_password(
        self,
        length: Optional[int] = None,
        include_special: bool = True,
    ) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Password length (defaults to policy.min_length)
            include_special: Whether to include special characters
            
        Returns:
            Generated password
        """
        import random
        import string
        
        length = length or self.policy.min_length
        
        # Build character pool
        chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
        if include_special:
            chars += self.policy.special_characters
        
        # Generate password with guaranteed character types
        password_chars = [
            random.choice(string.ascii_lowercase),
            random.choice(string.ascii_uppercase),
            random.choice(string.digits),
        ]
        
        if include_special:
            password_chars.append(random.choice(self.policy.special_characters))
        
        # Fill remaining length with random characters
        remaining = length - len(password_chars)
        password_chars.extend(random.choice(chars) for _ in range(remaining))
        
        # Shuffle to avoid predictable positions
        random.shuffle(password_chars)
        
        return "".join(password_chars)
