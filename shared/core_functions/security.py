"""
Centralized Security System for Trivya Platform

This module provides comprehensive security features including authentication,
authorization, encryption, and security utilities for the Trivya platform.
"""

import os
import secrets
import hashlib
import hmac
import time
import uuid
import re
from typing import Dict, Any, Optional, Tuple, List, Union
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes

# Import config and logger
try:
    from shared.core_functions.config import Config
    from shared.core_functions.logger import TrivyaLogger, get_logger
except ImportError:
    Config = None
    TrivyaLogger = None
    get_logger = None


class PasswordValidator:
    """Validate password strength and requirements"""
    
    def __init__(self, 
                 min_length: int = 8,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_digits: bool = True,
                 require_special: bool = True):
        """
        Initialize password validator
        
        Args:
            min_length: Minimum password length
            require_uppercase: Require at least one uppercase letter
            require_lowercase: Require at least one lowercase letter
            require_digits: Require at least one digit
            require_special: Require at least one special character
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
    
    def validate(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against requirements
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []
        
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return (len(errors) == 0, errors)


class TokenBucket:
    """Token bucket algorithm for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Try to consume tokens from bucket
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on time elapsed"""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Get time to wait until tokens are available
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Seconds to wait
        """
        self._refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class TrivyaSecurity:
    """Main security class for Trivya platform"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize security system with configuration
        
        Args:
            config: Configuration object (optional)
        """
        self.config = config
        self.logger = get_logger(config) if get_logger else None
        
        # Load security settings from config or environment
        self._load_security_config()
        
        # Initialize components
        self._init_encryption()
        self._init_password_validation()
        self._init_rate_limiting()
    
    def _load_security_config(self):
        """Load security configuration from config or environment"""
        # JWT settings
        self.jwt_secret = os.getenv("JWT_SECRET_KEY")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.jwt_refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Check for required JWT secret
        if not self.jwt_secret:
            if self.logger:
                self.logger.log_error(
                    component="security_system",
                    error=Exception("JWT_SECRET_KEY not configured"),
                    severity="critical"
                )
            raise ValueError("JWT_SECRET_KEY must be configured for security")
        
        # Encryption key
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
    
    def _init_encryption(self):
        """Initialize encryption system"""
        if not self.encryption_key:
            # Generate a new key if not provided
            self.encryption_key = Fernet.generate_key().decode()
            if self.logger:
                self.logger.log_warning(
                    component="security_system",
                    message="Generated new encryption key. Set ENCRYPTION_KEY in production for persistence."
                )
        
        # Ensure key is in bytes for Fernet
        if isinstance(self.encryption_key, str):
            key_bytes = self.encryption_key.encode()
        else:
            key_bytes = self.encryption_key
            
        self.fernet = Fernet(key_bytes)
    
    def _init_password_validation(self):
        """Initialize password validation settings"""
        self.password_validator = PasswordValidator(
            min_length=int(os.getenv("PASSWORD_MIN_LENGTH", "8")),
            require_uppercase=os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
            require_lowercase=os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
            require_digits=os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true",
            require_special=os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
        )
    
    def _init_rate_limiting(self):
        """Initialize rate limiting settings"""
        self.rate_limit_enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        self.rate_limit_per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
        
        # Rate limit buckets (in-memory, use Redis in production)
        self._rate_limit_buckets: Dict[str, TokenBucket] = {}
    
    # ==================== JWT Token Management ====================
    
    def generate_jwt_token(self, 
                          user_id: str, 
                          roles: Optional[List[str]] = None,
                          permissions: Optional[List[str]] = None,
                          token_type: str = "access",
                          correlation_id: Optional[str] = None) -> str:
        """
        Generate JWT token for user
        
        Args:
            user_id: User identifier
            roles: User roles
            permissions: User permissions
            token_type: Type of token ('access' or 'refresh')
            correlation_id: Correlation ID for tracking
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        
        if token_type == "access":
            expires_delta = timedelta(minutes=self.jwt_access_token_expire_minutes)
        else:  # refresh
            expires_delta = timedelta(days=self.jwt_refresh_token_expire_days)
        
        payload = {
            "user_id": user_id,
            "roles": roles or [],
            "permissions": permissions or [],
            "token_type": token_type,
            "iat": now,
            "exp": now + expires_delta,
            "jti": str(uuid.uuid4())  # JWT ID for token tracking
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Log token generation
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="jwt_token_generated",
                correlation_id=correlation_id,
                user_id=user_id,
                token_type=token_type,
                expires_at=str(now + expires_delta)
            )
        
        return token
    
    def validate_jwt_token(self, token: str, correlation_id: Optional[str] = None) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Validate JWT token
        
        Args:
            token: JWT token to validate
            correlation_id: Correlation ID for tracking
            
        Returns:
            Tuple of (is_valid, payload, error_message)
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Log successful validation
            if self.logger:
                self.logger.log_agent_action(
                    agent_id="security_system",
                    action="jwt_token_validated",
                    correlation_id=correlation_id,
                    user_id=payload.get("user_id"),
                    token_type=payload.get("token_type")
                )
            
            return (True, payload, None)
        
        except jwt.ExpiredSignatureError:
            error_msg = "Token has expired"
            if self.logger:
                self.logger.log_error(
                    component="security_system",
                    error=Exception(error_msg),
                    correlation_id=correlation_id,
                    validation_status="failed",
                    reason="expired"
                )
            return (False, None, error_msg)
        
        except jwt.InvalidTokenError as e:
            error_msg = f"Invalid token: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    component="security_system",
                    error=e,
                    correlation_id=correlation_id,
                    validation_status="failed",
                    reason="invalid"
                )
            return (False, None, error_msg)
    
    def refresh_jwt_token(self, refresh_token: str, correlation_id: Optional[str] = None) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Refresh JWT access token using refresh token
        
        Args:
            refresh_token: Refresh token
            correlation_id: Correlation ID for tracking
            
        Returns:
            Tuple of (success, new_access_token, error_message)
        """
        is_valid, payload, error = self.validate_jwt_token(refresh_token, correlation_id)
        
        if not is_valid:
            return (False, None, error)
        
        if payload.get("token_type") != "refresh":
            return (False, None, "Invalid token type for refresh")
        
        # Generate new access token
        new_token = self.generate_jwt_token(
            user_id=payload["user_id"],
            roles=payload.get("roles"),
            permissions=payload.get("permissions"),
            token_type="access",
            correlation_id=correlation_id
        )
        
        return (True, new_token, None)
    
    # ==================== Password Management ====================
    
    def hash_password(self, password: str, correlation_id: Optional[str] = None) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            correlation_id: Correlation ID for tracking
            
        Returns:
            Hashed password
        """
        # Validate password strength first
        is_valid, errors = self.password_validator.validate(password)
        if not is_valid:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Log password hashing (without the password itself)
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="password_hashed",
                correlation_id=correlation_id
            )
        
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str, correlation_id: Optional[str] = None) -> bool:
        """
        Verify password against hash
        
        Args:
            password: Plain text password
            hashed_password: Hashed password to compare
            correlation_id: Correlation ID for tracking
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            result = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
            
            # Log verification attempt
            if self.logger:
                self.logger.log_agent_action(
                    agent_id="security_system",
                    action="password_verified",
                    correlation_id=correlation_id,
                    verification_result="success" if result else "failed"
                )
            
            return result
        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    component="security_system",
                    error=e,
                    correlation_id=correlation_id,
                    operation="password_verification"
                )
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list of error messages)
        """
        return self.password_validator.validate(password)
    
    # ==================== API Key Management ====================
    
    def generate_api_key(self, prefix: str = "sk", length: int = 32, correlation_id: Optional[str] = None) -> str:
        """
        Generate secure API key
        
        Args:
            prefix: Key prefix (e.g., 'sk' for secret key)
            length: Length of random part
            correlation_id: Correlation ID for tracking
            
        Returns:
            API key string
        """
        random_part = secrets.token_urlsafe(length)
        api_key = f"{prefix}_{random_part}"
        
        # Log API key generation
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="api_key_generated",
                correlation_id=correlation_id,
                key_prefix=prefix
            )
        
        return api_key
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash API key for storage
        
        Args:
            api_key: API key to hash
            
        Returns:
            Hashed API key
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str, stored_hash: str, correlation_id: Optional[str] = None) -> bool:
        """
        Validate API key against stored hash
        
        Args:
            api_key: API key to validate
            stored_hash: Stored hash to compare
            correlation_id: Correlation ID for tracking
            
        Returns:
            True if valid, False otherwise
        """
        computed_hash = self.hash_api_key(api_key)
        is_valid = hmac.compare_digest(computed_hash, stored_hash)
        
        # Log validation attempt
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="api_key_validated",
                correlation_id=correlation_id,
                validation_result="success" if is_valid else "failed"
            )
        
        return is_valid
    
    # ==================== Data Encryption ====================
    
    def encrypt_data(self, data: str, correlation_id: Optional[str] = None) -> str:
        """
        Encrypt sensitive data using AES-256
        
        Args:
            data: Data to encrypt
            correlation_id: Correlation ID for tracking
            
        Returns:
            Encrypted data (base64 encoded)
        """
        if not data:
            return ""
        
        encrypted = self.fernet.encrypt(data.encode())
        
        # Log encryption (without the data)
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="data_encrypted",
                correlation_id=correlation_id
            )
        
        return encrypted.decode()
    
    def decrypt_data(self, encrypted_data: str, correlation_id: Optional[str] = None) -> str:
        """
        Decrypt encrypted data
        
        Args:
            encrypted_data: Encrypted data to decrypt
            correlation_id: Correlation ID for tracking
            
        Returns:
            Decrypted data
        """
        if not encrypted_data:
            return ""
        
        try:
            decrypted = self.fernet.decrypt(encrypted_data.encode())
            
            # Log decryption (without the data)
            if self.logger:
                self.logger.log_agent_action(
                    agent_id="security_system",
                    action="data_decrypted",
                    correlation_id=correlation_id
                )
            
            return decrypted.decode()
        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    component="security_system",
                    error=e,
                    correlation_id=correlation_id,
                    operation="data_decryption"
                )
            raise ValueError("Decryption failed: Invalid key or corrupted data")
    
    # ==================== Rate Limiting ====================
    
    def check_rate_limit(self, identifier: str, limit_type: str = "minute", correlation_id: Optional[str] = None) -> Tuple[bool, Optional[float]]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Unique identifier (user_id, IP, etc.)
            limit_type: Type of limit ('minute' or 'hour')
            correlation_id: Correlation ID for tracking
            
        Returns:
            Tuple of (is_allowed, wait_time_seconds)
        """
        if not self.rate_limit_enabled:
            return (True, None)
        
        # Get or create token bucket
        bucket_key = f"{identifier}:{limit_type}"
        
        if bucket_key not in self._rate_limit_buckets:
            if limit_type == "minute":
                capacity = self.rate_limit_per_minute
                refill_rate = capacity / 60.0  # Tokens per second
            else:  # hour
                capacity = self.rate_limit_per_hour
                refill_rate = capacity / 3600.0  # Tokens per second
            
            self._rate_limit_buckets[bucket_key] = TokenBucket(capacity, refill_rate)
        
        bucket = self._rate_limit_buckets[bucket_key]
        is_allowed = bucket.consume()
        wait_time = None if is_allowed else bucket.get_wait_time()
        
        # Log rate limit check
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="rate_limit_checked",
                correlation_id=correlation_id,
                identifier=identifier,
                limit_type=limit_type,
                result="allowed" if is_allowed else "throttled",
                wait_time=wait_time
            )
        
        return (is_allowed, wait_time)
    
    # ==================== Security Utilities ====================
    
    def generate_csrf_token(self, correlation_id: Optional[str] = None) -> str:
        """
        Generate CSRF token
        
        Args:
            correlation_id: Correlation ID for tracking
            
        Returns:
            CSRF token
        """
        token = secrets.token_urlsafe(32)
        
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="csrf_token_generated",
                correlation_id=correlation_id
            )
        
        return token
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate secure random token
        
        Args:
            length: Length of token
            
        Returns:
            Secure random token
        """
        return secrets.token_urlsafe(length)
    
    def sanitize_input(self, input_str: str) -> str:
        """
        Sanitize user input to prevent injection attacks
        
        Args:
            input_str: Input string to sanitize
            
        Returns:
            Sanitized string
        """
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_str)
        return sanitized.strip()
    
    def generate_session_id(self, correlation_id: Optional[str] = None) -> str:
        """
        Generate secure session ID
        
        Args:
            correlation_id: Correlation ID for tracking
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        
        if self.logger:
            self.logger.log_agent_action(
                agent_id="security_system",
                action="session_id_generated",
                correlation_id=correlation_id
            )
        
        return session_id


# Singleton instance
_security_instance: Optional[TrivyaSecurity] = None


def get_security(config: Optional[Config] = None) -> TrivyaSecurity:
    """
    Get singleton security instance
    
    Args:
        config: Configuration object (optional)
        
    Returns:
        TrivyaSecurity instance
    """
    global _security_instance
    
    if _security_instance is None:
        _security_instance = TrivyaSecurity(config)
    
    return _security_instance


# Export public API
__all__ = [
    'TrivyaSecurity',
    'PasswordValidator',
    'TokenBucket',
    'get_security',
]
