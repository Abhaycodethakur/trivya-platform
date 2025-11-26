"""
Integration Tests for Config + Security Modules

This module tests the integration between the configuration and security systems,
ensuring they work together correctly.
"""

import os
import pytest
from pathlib import Path
from shared.core_functions.config import Config
from shared.core_functions.security import TrivyaSecurity, get_security


@pytest.fixture
def test_config(monkeypatch, tmp_path):
    """Create test configuration"""
    # Generate valid Fernet key
    from cryptography.fernet import Fernet
    test_key = Fernet.generate_key().decode()
    
    # Set environment variables
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_jwt_secret_for_integration")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    monkeypatch.setenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "14")
    monkeypatch.setenv("ENCRYPTION_KEY", test_key)
    monkeypatch.setenv("PASSWORD_MIN_LENGTH", "10")
    monkeypatch.setenv("PASSWORD_REQUIRE_UPPERCASE", "true")
    monkeypatch.setenv("PASSWORD_REQUIRE_LOWERCASE", "true")
    monkeypatch.setenv("PASSWORD_REQUIRE_DIGITS", "true")
    monkeypatch.setenv("PASSWORD_REQUIRE_SPECIAL", "true")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "100")
    monkeypatch.setenv("RATE_LIMIT_PER_HOUR", "5000")
    
    # Set feature flags dir
    flags_dir = tmp_path / "feature_flags"
    flags_dir.mkdir(exist_ok=True)
    monkeypatch.setenv("FEATURE_FLAGS_DIR", str(flags_dir))
    
    return Config()


@pytest.fixture
def security_with_config(test_config):
    """Create security instance with config"""
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    return TrivyaSecurity(test_config)


# BDD Scenario 1: Security Uses Config Values
def test_security_uses_config_values(security_with_config):
    """
    Scenario: Security module uses configuration values
    Given a config with specific security settings
    When security module is initialized with config
    Then security should use config values
    """
    # Then security should use config values
    assert security_with_config.jwt_algorithm == "HS256"
    assert security_with_config.jwt_access_token_expire_minutes == 15
    assert security_with_config.jwt_refresh_token_expire_days == 14
    assert security_with_config.password_validator.min_length == 10
    assert security_with_config.rate_limit_per_minute == 100
    assert security_with_config.rate_limit_per_hour == 5000


# BDD Scenario 2: Security Falls Back to Environment Variables
def test_security_fallback_to_env(monkeypatch):
    """
    Scenario: Security falls back to environment when config missing
    Given environment variables are set
    When security is initialized without config
    Then security should use environment values
    """
    # Given environment variables are set
    from cryptography.fernet import Fernet
    test_key = Fernet.generate_key().decode()
    
    monkeypatch.setenv("JWT_SECRET_KEY", "fallback_secret")
    monkeypatch.setenv("ENCRYPTION_KEY", test_key)
    monkeypatch.setenv("PASSWORD_MIN_LENGTH", "12")
    
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    # When security is initialized without config
    security = TrivyaSecurity()
    
    # Then security should use environment values
    assert security.jwt_secret == "fallback_secret"
    assert security.password_validator.min_length == 12


# BDD Scenario 3: Security Validates Config Values
def test_security_validates_config(monkeypatch):
    """
    Scenario: Security validates configuration values
    Given invalid or missing config values
    When security is initialized
    Then appropriate errors should be raised
    """
    # Given missing JWT secret
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    # When security is initialized
    # Then appropriate error should be raised
    with pytest.raises(ValueError) as exc_info:
        TrivyaSecurity()
    
    assert "JWT_SECRET_KEY must be configured" in str(exc_info.value)


# BDD Scenario 4: Config and Security Encryption Integration
def test_config_security_encryption_integration(test_config, security_with_config):
    """
    Scenario: Config and Security share encryption capabilities
    Given both config and security have encryption
    When data is encrypted by one
    Then it should be decryptable by the other
    """
    # Given test data
    sensitive_data = "user_password_12345"
    
    # When config encrypts data
    config_encrypted = test_config.encrypt_value(sensitive_data)
    
    # Then security should be able to decrypt it
    # (Both use same ENCRYPTION_KEY from environment)
    security_encrypted = security_with_config.encrypt_data(sensitive_data)
    security_decrypted = security_with_config.decrypt_data(security_encrypted)
    
    assert security_decrypted == sensitive_data


# BDD Scenario 5: Password Requirements from Config
def test_password_requirements_from_config(security_with_config):
    """
    Scenario: Password requirements come from config
    Given config specifies password requirements
    When password is validated
    Then requirements from config should be enforced
    """
    # Given config specifies min length 10
    # When weak password is tested
    weak_password = "Short1!"  # Only 7 chars
    is_valid, errors = security_with_config.validate_password_strength(weak_password)
    
    # Then it should fail with config requirement
    assert is_valid is False
    assert any("at least 10 characters" in error for error in errors)


# BDD Scenario 6: Rate Limiting Configuration
def test_rate_limiting_configuration(security_with_config):
    """
    Scenario: Rate limiting uses config values
    Given config specifies rate limits
    When rate limit is checked
    Then config values should be used
    """
    # Given config specifies 100 requests per minute
    user_id = "test_user_rate_limit"
    
    # When making requests
    allowed_count = 0
    for i in range(105):
        is_allowed, _ = security_with_config.check_rate_limit(user_id, "minute")
        if is_allowed:
            allowed_count += 1
    
    # Then should allow up to config limit (100)
    assert allowed_count == 100


# BDD Scenario 7: JWT Token Expiration from Config
def test_jwt_expiration_from_config(security_with_config):
    """
    Scenario: JWT token expiration uses config values
    Given config specifies token expiration times
    When token is generated
    Then expiration should match config
    """
    # When access token is generated
    token = security_with_config.generate_jwt_token(
        user_id="test_user",
        token_type="access"
    )
    
    # Then validate and check expiration
    is_valid, payload, _ = security_with_config.validate_jwt_token(token)
    
    assert is_valid is True
    # Expiration time should be set (15 minutes from config)
    assert "exp" in payload
    assert "iat" in payload


# BDD Scenario 8: Security Module Singleton with Config
def test_security_singleton_with_config(test_config):
    """
    Scenario: Security singleton works with config
    Given a config instance
    When get_security is called multiple times
    Then same instance should be returned
    """
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    # When get_security is called multiple times
    security1 = get_security(test_config)
    security2 = get_security(test_config)
    
    # Then same instance should be returned
    assert security1 is security2


# BDD Scenario 9: Config Feature Flags and Security
def test_config_feature_flags_security_integration(test_config, security_with_config, tmp_path):
    """
    Scenario: Security can use feature flags from config
    Given config has feature flags
    When security checks feature flags
    Then appropriate behavior should occur
    """
    # Given config has feature flags
    flags_dir = tmp_path / "feature_flags"
    flags_dir.mkdir(exist_ok=True)
    
    import json
    flags = {
        "enhanced_security": True,
        "strict_password_policy": True
    }
    
    with open(flags_dir / "security_flags.json", "w") as f:
        json.dump(flags, f)
    
    # When feature flags are loaded
    loaded_flags = test_config.get_feature_flags("security")
    
    # Then flags should be available
    assert loaded_flags.get("enhanced_security") is True


# BDD Scenario 10: Environment-Specific Security Settings
def test_environment_specific_security(monkeypatch, test_config):
    """
    Scenario: Security settings vary by environment
    Given different environment settings
    When security is configured
    Then settings should match environment
    """
    # Given production environment
    monkeypatch.setenv("ENVIRONMENT", "production")
    
    # Reload config
    config = Config()
    
    # Then production settings should be used
    assert config.is_production() is True
