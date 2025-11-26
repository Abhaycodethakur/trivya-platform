"""
Integration Tests for Config + Logger + Security Modules

This module tests the full integration of all three core modules,
ensuring they work together seamlessly.
"""

import os
import pytest
import json
from pathlib import Path
from shared.core_functions.config import Config
from shared.core_functions.logger import TrivyaLogger, get_logger
from shared.core_functions.security import TrivyaSecurity, get_security


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing"""
    log_dir = tmp_path / "logs"
    flags_dir = tmp_path / "feature_flags"
    log_dir.mkdir()
    flags_dir.mkdir()
    
    return {
        "log_dir": log_dir,
        "flags_dir": flags_dir,
        "root": tmp_path
    }


@pytest.fixture
def integrated_system(temp_dirs, monkeypatch):
    """Create fully integrated system with all three modules"""
    from cryptography.fernet import Fernet
    test_key = Fernet.generate_key().decode()
    
    # Set all environment variables
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.setenv("LOG_OUTPUT", "file")
    monkeypatch.setenv("LOG_FILE_PATH", str(temp_dirs["log_dir"] / "integrated.log"))
    monkeypatch.setenv("JWT_SECRET_KEY", "integrated_test_secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("ENCRYPTION_KEY", test_key)
    monkeypatch.setenv("PASSWORD_MIN_LENGTH", "8")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("FEATURE_FLAGS_DIR", str(temp_dirs["flags_dir"]))
    
    # Reset singletons
    import shared.core_functions.logger as logger_module
    import shared.core_functions.security as security_module
    logger_module._logger_instance = None
    security_module._security_instance = None
    
    # Create instances
    config = Config()
    logger = TrivyaLogger(config)
    security = TrivyaSecurity(config)
    
    return {
        "config": config,
        "logger": logger,
        "security": security,
        "temp_dirs": temp_dirs
    }


# BDD Scenario 1: Full System Integration
def test_full_system_integration(integrated_system):
    """
    Scenario: All three modules work together
    Given config, logger, and security are initialized
    When operations are performed
    Then all modules should work together correctly
    """
    config = integrated_system["config"]
    logger = integrated_system["logger"]
    security = integrated_system["security"]
    
    # Verify all modules are initialized
    assert config is not None
    assert logger is not None
    assert security is not None
    
    # Verify security uses config
    assert security.config is config
    
    # Verify logger is available to security
    assert security.logger is not None


# BDD Scenario 2: Configuration Flows Through System
def test_configuration_flow(integrated_system):
    """
    Scenario: Configuration flows from config to other modules
    Given a config with specific settings
    When logger and security use config
    Then settings should flow correctly
    """
    config = integrated_system["config"]
    logger = integrated_system["logger"]
    security = integrated_system["security"]
    
    # Configuration should flow to logger
    assert logger.config is config
    assert logger.config.logging_config.LOG_LEVEL == "DEBUG"
    
    # Configuration should flow to security
    assert security.config is config
    assert security.jwt_secret == "integrated_test_secret"


# BDD Scenario 3: Logging Across Integrated System
def test_logging_across_system(integrated_system):
    """
    Scenario: Logging works across all modules
    Given an integrated system
    When operations are performed across modules
    Then all operations should be logged
    """
    security = integrated_system["security"]
    temp_dirs = integrated_system["temp_dirs"]
    correlation_id = "integrated_test_123"
    
    # Perform security operation with correlation ID
    token = security.generate_jwt_token(
        user_id="integrated_user",
        correlation_id=correlation_id
    )
    
    # Verify operation was logged
    log_file = temp_dirs["log_dir"] / "integrated.log"
    assert log_file.exists()
    
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "jwt_token_generated" in log_content
        assert correlation_id in log_content
        assert "integrated_user" in log_content


# BDD Scenario 4: Correlation IDs Across Modules
def test_correlation_ids_across_modules(integrated_system):
    """
    Scenario: Correlation IDs work across all modules
    Given an integrated system
    When correlation ID is used
    Then it should be tracked across all modules
    """
    logger = integrated_system["logger"]
    security = integrated_system["security"]
    temp_dirs = integrated_system["temp_dirs"]
    
    # Create correlation ID from logger
    correlation_id = logger.create_correlation_id()
    
    # Use in security operations
    token = security.generate_jwt_token(
        user_id="correlated_user",
        correlation_id=correlation_id
    )
    
    security.validate_jwt_token(token, correlation_id=correlation_id)
    
    # Verify correlation ID is in logs
    log_file = temp_dirs["log_dir"] / "integrated.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        # Should appear multiple times
        count = log_content.count(correlation_id)
        assert count >= 2


# BDD Scenario 5: Error Handling Across System
def test_error_handling_across_system(integrated_system):
    """
    Scenario: Error handling works across integrated system
    Given an integrated system
    When errors occur
    Then they should be handled and logged correctly
    """
    security = integrated_system["security"]
    temp_dirs = integrated_system["temp_dirs"]
    correlation_id = "error_test_456"
    
    # Cause an error
    invalid_token = "invalid.token.value"
    is_valid, payload, error = security.validate_jwt_token(
        invalid_token,
        correlation_id=correlation_id
    )
    
    # Error should be returned
    assert is_valid is False
    assert error is not None
    
    # Error should be logged
    log_file = temp_dirs["log_dir"] / "integrated.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "failed" in log_content
        assert correlation_id in log_content


# BDD Scenario 6: Feature Flags Integration
def test_feature_flags_integration(integrated_system):
    """
    Scenario: Feature flags work across system
    Given config with feature flags
    When flags are checked
    Then they should be available to all modules
    """
    config = integrated_system["config"]
    temp_dirs = integrated_system["temp_dirs"]
    
    # Create feature flags
    flags = {
        "enhanced_security": True,
        "debug_logging": True,
        "rate_limiting": True
    }
    
    flags_file = temp_dirs["flags_dir"] / "test_flags.json"
    with open(flags_file, 'w') as f:
        json.dump(flags, f)
    
    # Load flags
    loaded_flags = config.get_feature_flags("test")
    
    # Flags should be available
    assert loaded_flags.get("enhanced_security") is True
    assert loaded_flags.get("debug_logging") is True


# BDD Scenario 7: Encryption Integration
def test_encryption_integration(integrated_system):
    """
    Scenario: Encryption works across config and security
    Given config and security with same encryption key
    When data is encrypted
    Then both modules can encrypt/decrypt
    """
    config = integrated_system["config"]
    security = integrated_system["security"]
    
    # Test data
    sensitive_data = "user_password_secret"
    
    # Config encrypts
    config_encrypted = config.encrypt_value(sensitive_data)
    config_decrypted = config.decrypt_value(config_encrypted)
    
    # Security encrypts
    security_encrypted = security.encrypt_data(sensitive_data)
    security_decrypted = security.decrypt_data(security_encrypted)
    
    # Both should work
    assert config_decrypted == sensitive_data
    assert security_decrypted == sensitive_data


# BDD Scenario 8: Complete Workflow Integration
def test_complete_workflow_integration(integrated_system):
    """
    Scenario: Complete workflow using all modules
    Given an integrated system
    When a complete user workflow is executed
    Then all modules should work together seamlessly
    """
    config = integrated_system["config"]
    logger = integrated_system["logger"]
    security = integrated_system["security"]
    temp_dirs = integrated_system["temp_dirs"]
    
    # Step 1: Create correlation ID
    correlation_id = logger.create_correlation_id()
    
    # Step 2: User registration - hash password
    password = "UserP@ssw0rd123"
    hashed_password = security.hash_password(password, correlation_id=correlation_id)
    
    # Step 3: User login - verify password
    is_valid = security.verify_password(password, hashed_password, correlation_id=correlation_id)
    assert is_valid is True
    
    # Step 4: Generate JWT token
    token = security.generate_jwt_token(
        user_id="workflow_user",
        roles=["user"],
        permissions=["read", "write"],
        correlation_id=correlation_id
    )
    
    # Step 5: Validate token
    is_valid, payload, error = security.validate_jwt_token(token, correlation_id=correlation_id)
    assert is_valid is True
    
    # Step 6: Check rate limit
    is_allowed, wait_time = security.check_rate_limit(
        identifier="workflow_user",
        correlation_id=correlation_id
    )
    assert is_allowed is True
    
    # Verify entire workflow was logged
    log_file = temp_dirs["log_dir"] / "integrated.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "password_hashed" in log_content
        assert "password_verified" in log_content
        assert "jwt_token_generated" in log_content
        assert "jwt_token_validated" in log_content
        assert "rate_limit_checked" in log_content
        # All with same correlation ID
        count = log_content.count(correlation_id)
        assert count >= 5


# BDD Scenario 9: Singleton Pattern Integration
def test_singleton_pattern_integration(integrated_system):
    """
    Scenario: Singleton pattern works across modules
    Given an integrated system
    When get functions are called
    Then same instances should be returned
    """
    config = integrated_system["config"]
    
    # Get instances multiple times
    logger1 = get_logger(config)
    logger2 = get_logger(config)
    
    security1 = get_security(config)
    security2 = get_security(config)
    
    # Should be same instances
    assert logger1 is logger2
    assert security1 is security2


# BDD Scenario 10: Production-Ready Integration
def test_production_ready_integration(integrated_system, monkeypatch):
    """
    Scenario: System works in production configuration
    Given production environment settings
    When system is configured
    Then all modules should work correctly
    """
    config = integrated_system["config"]
    
    # Set production environment
    monkeypatch.setenv("ENVIRONMENT", "production")
    
    # Reload config
    prod_config = Config()
    
    # Verify production mode
    assert prod_config.is_production() is True
    
    # System should still work
    assert prod_config is not None
