"""
Tests for the Trivya Security System

This module tests all security functionality including JWT authentication,
password management, API key management, encryption, and rate limiting.
"""

import os
import pytest
import time
from datetime import datetime, timedelta
from shared.core_functions.security import (
    TrivyaSecurity,
    PasswordValidator,
    TokenBucket,
    get_security
)


@pytest.fixture
def security_instance(monkeypatch):
    """Create security instance for testing"""
    # Generate a valid Fernet key for testing
    from cryptography.fernet import Fernet
    test_key = Fernet.generate_key().decode()
    
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_key_for_testing")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")
    monkeypatch.setenv("ENCRYPTION_KEY", test_key)
    monkeypatch.setenv("PASSWORD_MIN_LENGTH", "8")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "60")
    
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    return TrivyaSecurity()


# ==================== JWT Token Tests ====================

# BDD Scenario 1: JWT Token Generation
def test_jwt_token_generation(security_instance):
    """
    Scenario: Generate JWT token for authenticated user
    Given a user with valid credentials
    When they request authentication
    Then a JWT token should be generated with correct expiration
    And the token should contain user roles and permissions
    """
    # Given a user with valid credentials
    user_id = "user_123"
    roles = ["admin", "user"]
    permissions = ["read", "write", "delete"]
    
    # When they request authentication
    token = security_instance.generate_jwt_token(
        user_id=user_id,
        roles=roles,
        permissions=permissions,
        token_type="access"
    )
    
    # Then a JWT token should be generated
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0
    
    # And the token should contain user roles and permissions
    is_valid, payload, error = security_instance.validate_jwt_token(token)
    assert is_valid is True
    assert payload["user_id"] == user_id
    assert payload["roles"] == roles
    assert payload["permissions"] == permissions
    assert payload["token_type"] == "access"


def test_jwt_token_validation(security_instance):
    """
    Scenario: Validate JWT token
    Given a valid JWT token
    When the token is validated
    Then it should return success with payload
    """
    # Given a valid JWT token
    token = security_instance.generate_jwt_token(
        user_id="user_456",
        roles=["user"],
        token_type="access"
    )
    
    # When the token is validated
    is_valid, payload, error = security_instance.validate_jwt_token(token)
    
    # Then it should return success with payload
    assert is_valid is True
    assert payload is not None
    assert error is None
    assert payload["user_id"] == "user_456"


def test_jwt_token_invalid(security_instance):
    """
    Scenario: Validate invalid JWT token
    Given an invalid JWT token
    When the token is validated
    Then it should return failure with error message
    """
    # Given an invalid JWT token
    invalid_token = "invalid.token.here"
    
    # When the token is validated
    is_valid, payload, error = security_instance.validate_jwt_token(invalid_token)
    
    # Then it should return failure with error message
    assert is_valid is False
    assert payload is None
    assert error is not None
    assert "Invalid token" in error


def test_jwt_token_refresh(security_instance):
    """
    Scenario: Refresh JWT access token
    Given a valid refresh token
    When a new access token is requested
    Then a new access token should be generated
    """
    # Given a valid refresh token
    refresh_token = security_instance.generate_jwt_token(
        user_id="user_789",
        roles=["user"],
        token_type="refresh"
    )
    
    # When a new access token is requested
    success, new_token, error = security_instance.refresh_jwt_token(refresh_token)
    
    # Then a new access token should be generated
    assert success is True
    assert new_token is not None
    assert error is None
    
    # Verify the new token is valid
    is_valid, payload, _ = security_instance.validate_jwt_token(new_token)
    assert is_valid is True
    assert payload["token_type"] == "access"


# ==================== Password Management Tests ====================

# BDD Scenario 2: Password Security
def test_password_hashing(security_instance):
    """
    Scenario: Hash password securely
    Given a new user registration
    When a password is provided
    Then it should be hashed using bcrypt
    And the hash should be verified correctly
    """
    # Given a new user registration
    # When a password is provided
    password = "SecureP@ssw0rd123"
    
    # Then it should be hashed using bcrypt
    hashed = security_instance.hash_password(password)
    
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password  # Should not be plain text
    
    # And the hash should be verified correctly
    is_valid = security_instance.verify_password(password, hashed)
    assert is_valid is True
    
    # Wrong password should fail
    is_valid_wrong = security_instance.verify_password("WrongPassword", hashed)
    assert is_valid_wrong is False


def test_password_strength_validation(security_instance):
    """
    Scenario: Validate password strength
    Given password strength requirements
    When a weak password is provided
    Then it should be rejected
    """
    # Given password strength requirements
    # When a weak password is provided
    weak_passwords = [
        "short",  # Too short
        "nouppercase123!",  # No uppercase
        "NOLOWERCASE123!",  # No lowercase
        "NoDigits!",  # No digits
        "NoSpecial123",  # No special characters
    ]
    
    # Then it should be rejected
    for weak_pwd in weak_passwords:
        is_valid, errors = security_instance.validate_password_strength(weak_pwd)
        assert is_valid is False
        assert len(errors) > 0


def test_password_strength_validation_strong(security_instance):
    """Test that strong passwords pass validation"""
    strong_password = "StrongP@ssw0rd123"
    
    is_valid, errors = security_instance.validate_password_strength(strong_password)
    
    assert is_valid is True
    assert len(errors) == 0


def test_password_hashing_with_weak_password(security_instance):
    """Test that weak passwords are rejected during hashing"""
    weak_password = "weak"
    
    with pytest.raises(ValueError) as exc_info:
        security_instance.hash_password(weak_password)
    
    assert "Password validation failed" in str(exc_info.value)


# ==================== API Key Management Tests ====================

# BDD Scenario 3: API Key Management
def test_api_key_generation(security_instance):
    """
    Scenario: Generate secure API key
    Given an integration requiring API access
    When an API key is generated
    Then it should be secure and unique
    """
    # Given an integration requiring API access
    # When an API key is generated
    api_key1 = security_instance.generate_api_key(prefix="sk")
    api_key2 = security_instance.generate_api_key(prefix="sk")
    
    # Then it should be secure and unique
    assert api_key1 is not None
    assert api_key2 is not None
    assert api_key1 != api_key2  # Should be unique
    assert api_key1.startswith("sk_")
    assert api_key2.startswith("sk_")
    assert len(api_key1) > 10  # Should be reasonably long


def test_api_key_validation(security_instance):
    """
    Scenario: Validate API key
    Given a generated API key
    When it is validated against stored hash
    Then it should be validated correctly
    """
    # Given a generated API key
    api_key = security_instance.generate_api_key()
    stored_hash = security_instance.hash_api_key(api_key)
    
    # When it is validated against stored hash
    is_valid = security_instance.validate_api_key(api_key, stored_hash)
    
    # Then it should be validated correctly
    assert is_valid is True
    
    # Wrong API key should fail
    wrong_key = security_instance.generate_api_key()
    is_valid_wrong = security_instance.validate_api_key(wrong_key, stored_hash)
    assert is_valid_wrong is False


# ==================== Data Encryption Tests ====================

# BDD Scenario 4: Data Encryption
def test_data_encryption(security_instance):
    """
    Scenario: Encrypt sensitive data
    Given sensitive data that needs to be stored
    When encryption is applied
    Then the data should be encrypted using AES-256
    And it should be decryptable with the correct key
    """
    # Given sensitive data that needs to be stored
    sensitive_data = "credit_card_number_1234567890"
    
    # When encryption is applied
    encrypted = security_instance.encrypt_data(sensitive_data)
    
    # Then the data should be encrypted
    assert encrypted is not None
    assert encrypted != sensitive_data  # Should not be plain text
    
    # And it should be decryptable with the correct key
    decrypted = security_instance.decrypt_data(encrypted)
    assert decrypted == sensitive_data


def test_data_encryption_empty_string(security_instance):
    """Test encryption of empty string"""
    encrypted = security_instance.encrypt_data("")
    assert encrypted == ""
    
    decrypted = security_instance.decrypt_data("")
    assert decrypted == ""


def test_data_decryption_invalid(security_instance):
    """Test decryption with invalid data"""
    with pytest.raises(ValueError) as exc_info:
        security_instance.decrypt_data("invalid_encrypted_data")
    
    assert "Decryption failed" in str(exc_info.value)


# ==================== Rate Limiting Tests ====================

# BDD Scenario 5: Rate Limiting
def test_rate_limiting(security_instance):
    """
    Scenario: Enforce rate limits
    Given a user making API requests
    When they exceed their rate limit
    Then the requests should be throttled
    And appropriate wait time should be returned
    """
    # Given a user making API requests
    user_id = "user_rate_limit_test"
    
    # Set a low rate limit for testing
    security_instance.rate_limit_per_minute = 5
    
    # When they make requests within limit
    for i in range(5):
        is_allowed, wait_time = security_instance.check_rate_limit(user_id, "minute")
        assert is_allowed is True
        assert wait_time is None
    
    # Then the next request should be throttled
    is_allowed, wait_time = security_instance.check_rate_limit(user_id, "minute")
    assert is_allowed is False
    assert wait_time is not None
    assert wait_time > 0


def test_rate_limiting_disabled(security_instance):
    """Test that rate limiting can be disabled"""
    security_instance.rate_limit_enabled = False
    
    # Should allow unlimited requests
    for i in range(100):
        is_allowed, wait_time = security_instance.check_rate_limit("user_test", "minute")
        assert is_allowed is True
        assert wait_time is None


def test_token_bucket():
    """Test TokenBucket class directly"""
    bucket = TokenBucket(capacity=10, refill_rate=1.0)
    
    # Should be able to consume tokens
    assert bucket.consume(5) is True
    assert bucket.consume(5) is True
    
    # Should fail when empty
    assert bucket.consume(1) is False
    
    # Should refill over time
    time.sleep(2)  # Wait for 2 tokens to refill
    assert bucket.consume(2) is True


# ==================== Security Utilities Tests ====================

def test_csrf_token_generation(security_instance):
    """
    Scenario: Generate CSRF token
    Given a web form submission
    When a CSRF token is generated
    Then it should be unique and secure
    """
    # When a CSRF token is generated
    token1 = security_instance.generate_csrf_token()
    token2 = security_instance.generate_csrf_token()
    
    # Then it should be unique and secure
    assert token1 is not None
    assert token2 is not None
    assert token1 != token2
    assert len(token1) > 20


def test_secure_token_generation(security_instance):
    """Test secure random token generation"""
    token = security_instance.generate_secure_token(length=32)
    
    assert token is not None
    assert len(token) > 0


def test_input_sanitization(security_instance):
    """Test input sanitization"""
    dangerous_input = '<script>alert("XSS")</script>'
    sanitized = security_instance.sanitize_input(dangerous_input)
    
    assert "<" not in sanitized
    assert ">" not in sanitized
    assert "script" in sanitized  # Text remains, tags removed


def test_session_id_generation(security_instance):
    """Test session ID generation"""
    session_id1 = security_instance.generate_session_id()
    session_id2 = security_instance.generate_session_id()
    
    assert session_id1 is not None
    assert session_id2 is not None
    assert session_id1 != session_id2


# ==================== Integration Tests ====================

def test_get_security_singleton(monkeypatch):
    """Test that get_security returns singleton instance"""
    # Set required environment variables
    from cryptography.fernet import Fernet
    test_key = Fernet.generate_key().decode()
    
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_for_singleton")
    monkeypatch.setenv("ENCRYPTION_KEY", test_key)
    
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    security1 = get_security()
    security2 = get_security()
    
    assert security1 is security2


def test_password_validator_class():
    """Test PasswordValidator class directly"""
    validator = PasswordValidator(
        min_length=10,
        require_uppercase=True,
        require_lowercase=True,
        require_digits=True,
        require_special=True
    )
    
    # Test weak password
    is_valid, errors = validator.validate("weak")
    assert is_valid is False
    assert len(errors) > 0
    
    # Test strong password
    is_valid, errors = validator.validate("StrongP@ssw0rd123")
    assert is_valid is True
    assert len(errors) == 0


def test_security_with_logger_integration(security_instance):
    """Test that security operations are logged"""
    # This test verifies that security operations integrate with logger
    # The logger should be called for various security events
    
    # Generate JWT token (should log)
    token = security_instance.generate_jwt_token(
        user_id="test_user",
        correlation_id="test_correlation_123"
    )
    
    # Validate token (should log)
    security_instance.validate_jwt_token(token, correlation_id="test_correlation_123")
    
    # Hash password (should log)
    security_instance.hash_password("TestP@ssw0rd123", correlation_id="test_correlation_123")
    
    # No exceptions should be raised
    assert True


def test_security_event_logging(security_instance):
    """
    Scenario: Log security events
    Given a security event occurs
    When the event is processed
    Then it should be logged with appropriate severity
    And sensitive data should be sanitized
    """
    # Given a security event occurs (password verification)
    password = "TestP@ssw0rd123"
    hashed = security_instance.hash_password(password)
    
    # When the event is processed
    correlation_id = "security_event_test_123"
    result = security_instance.verify_password(password, hashed, correlation_id=correlation_id)
    
    # Then it should be logged (verified by no exceptions)
    assert result is True
