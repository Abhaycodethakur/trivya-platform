"""
Integration Tests for Logger + Security Modules

This module tests the integration between the logger and security systems,
ensuring security operations are properly logged.
"""

import os
import pytest
import logging
from pathlib import Path
from shared.core_functions.logger import TrivyaLogger, get_logger
from shared.core_functions.security import TrivyaSecurity


@pytest.fixture
def temp_log_dir(tmp_path):
    """Create temporary log directory"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return log_dir


@pytest.fixture
def logger_instance(temp_log_dir, monkeypatch):
    """Create logger instance for testing"""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.setenv("LOG_OUTPUT", "file")
    monkeypatch.setenv("LOG_FILE_PATH", str(temp_log_dir / "security_test.log"))
    
    # Reset singleton
    import shared.core_functions.logger as logger_module
    logger_module._logger_instance = None
    
    return TrivyaLogger()


@pytest.fixture
def security_with_logger(logger_instance, monkeypatch):
    """Create security instance with logger"""
    from cryptography.fernet import Fernet
    test_key = Fernet.generate_key().decode()
    
    monkeypatch.setenv("JWT_SECRET_KEY", "test_secret_for_logger_integration")
    monkeypatch.setenv("ENCRYPTION_KEY", test_key)
    
    # Reset singleton
    import shared.core_functions.security as security_module
    security_module._security_instance = None
    
    return TrivyaSecurity()


# BDD Scenario 1: Security Operations Are Logged
def test_security_operations_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Security operations are logged
    Given a security instance with logger
    When security operations are performed
    Then operations should be logged
    """
    # When JWT token is generated
    token = security_with_logger.generate_jwt_token(
        user_id="test_user",
        correlation_id="test_correlation_123"
    )
    
    # Then operation should be logged
    log_file = temp_log_dir / "security_test.log"
    assert log_file.exists()
    
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "jwt_token_generated" in log_content
        assert "test_user" in log_content


# BDD Scenario 2: Password Operations Are Logged
def test_password_operations_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Password operations are logged
    Given a security instance
    When password is hashed and verified
    Then operations should be logged
    """
    # When password is hashed
    password = "SecureP@ssw0rd123"
    hashed = security_with_logger.hash_password(password, correlation_id="pwd_hash_123")
    
    # And password is verified
    security_with_logger.verify_password(password, hashed, correlation_id="pwd_verify_123")
    
    # Then operations should be logged
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "password_hashed" in log_content
        assert "password_verified" in log_content
        assert "pwd_hash_123" in log_content
        assert "pwd_verify_123" in log_content


# BDD Scenario 3: Encryption Operations Are Logged
def test_encryption_operations_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Encryption operations are logged
    Given a security instance
    When data is encrypted and decrypted
    Then operations should be logged
    """
    # When data is encrypted
    data = "sensitive_information"
    encrypted = security_with_logger.encrypt_data(data, correlation_id="encrypt_123")
    
    # And data is decrypted
    decrypted = security_with_logger.decrypt_data(encrypted, correlation_id="decrypt_123")
    
    # Then operations should be logged
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "data_encrypted" in log_content
        assert "data_decrypted" in log_content
        assert "encrypt_123" in log_content
        assert "decrypt_123" in log_content


# BDD Scenario 4: Security Errors Are Logged
def test_security_errors_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Security errors are logged
    Given a security instance
    When security errors occur
    Then errors should be logged with details
    """
    # When invalid token is validated
    invalid_token = "invalid.token.here"
    is_valid, payload, error = security_with_logger.validate_jwt_token(
        invalid_token,
        correlation_id="error_test_123"
    )
    
    # Then error should be logged
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "validation_status" in log_content
        assert "failed" in log_content
        assert "error_test_123" in log_content


# BDD Scenario 5: Correlation IDs Are Used
def test_correlation_ids_used(security_with_logger, temp_log_dir):
    """
    Scenario: Security operations use correlation IDs
    Given a correlation ID
    When multiple security operations are performed
    Then all operations should use the same correlation ID
    """
    # Given a correlation ID
    correlation_id = "multi_op_correlation_456"
    
    # When multiple operations are performed
    token = security_with_logger.generate_jwt_token(
        user_id="test_user",
        correlation_id=correlation_id
    )
    
    security_with_logger.validate_jwt_token(token, correlation_id=correlation_id)
    
    api_key = security_with_logger.generate_api_key(correlation_id=correlation_id)
    
    # Then all should use same correlation ID
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        # Count occurrences of correlation ID
        count = log_content.count(correlation_id)
        assert count >= 3  # At least 3 operations logged


# BDD Scenario 6: Rate Limiting Is Logged
def test_rate_limiting_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Rate limiting checks are logged
    Given a security instance
    When rate limit is checked
    Then check should be logged
    """
    # When rate limit is checked
    security_with_logger.check_rate_limit(
        identifier="user_123",
        limit_type="minute",
        correlation_id="rate_limit_test"
    )
    
    # Then check should be logged
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "rate_limit_checked" in log_content
        assert "user_123" in log_content
        assert "rate_limit_test" in log_content


# BDD Scenario 7: API Key Operations Are Logged
def test_api_key_operations_logged(security_with_logger, temp_log_dir):
    """
    Scenario: API key operations are logged
    Given a security instance
    When API keys are generated and validated
    Then operations should be logged
    """
    # When API key is generated
    api_key = security_with_logger.generate_api_key(
        prefix="test",
        correlation_id="api_gen_123"
    )
    
    # And API key is validated
    stored_hash = security_with_logger.hash_api_key(api_key)
    security_with_logger.validate_api_key(
        api_key,
        stored_hash,
        correlation_id="api_val_123"
    )
    
    # Then operations should be logged
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "api_key_generated" in log_content
        assert "api_key_validated" in log_content
        assert "api_gen_123" in log_content
        assert "api_val_123" in log_content


# BDD Scenario 8: Security Utilities Are Logged
def test_security_utilities_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Security utility operations are logged
    Given a security instance
    When security utilities are used
    Then operations should be logged
    """
    # When CSRF token is generated
    csrf_token = security_with_logger.generate_csrf_token(correlation_id="csrf_123")
    
    # And session ID is generated
    session_id = security_with_logger.generate_session_id(correlation_id="session_123")
    
    # Then operations should be logged
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "csrf_token_generated" in log_content
        assert "session_id_generated" in log_content
        assert "csrf_123" in log_content
        assert "session_123" in log_content


# BDD Scenario 9: Sensitive Data Not in Logs
def test_sensitive_data_not_logged(security_with_logger, temp_log_dir):
    """
    Scenario: Sensitive data is not logged
    Given a security instance
    When operations with sensitive data are performed
    Then sensitive data should not appear in logs
    """
    # When password is hashed
    password = "MySecretP@ssw0rd123"
    hashed = security_with_logger.hash_password(password)
    
    # And data is encrypted
    sensitive_data = "credit_card_1234567890"
    encrypted = security_with_logger.encrypt_data(sensitive_data)
    
    # Then sensitive data should not be in logs
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert password not in log_content
        assert sensitive_data not in log_content


# BDD Scenario 10: Logger Integration with Security Errors
def test_logger_integration_security_errors(security_with_logger, temp_log_dir):
    """
    Scenario: Security errors are properly logged with context
    Given a security instance
    When security operations fail
    Then errors should be logged with full context
    """
    # When decryption fails
    try:
        security_with_logger.decrypt_data(
            "invalid_encrypted_data",
            correlation_id="decrypt_error_123"
        )
    except ValueError:
        pass  # Expected error
    
    # Then error should be logged with context
    log_file = temp_log_dir / "security_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "data_decryption" in log_content
        assert "decrypt_error_123" in log_content
