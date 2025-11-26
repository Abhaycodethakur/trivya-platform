"""
Integration Tests for Config and Logger Systems

This module tests the integration between the configuration and logging systems,
ensuring they work together seamlessly.
"""

import os
import pytest
import tempfile
from pathlib import Path
from shared.core_functions.config import Config, LoggingConfig
from shared.core_functions.logger import TrivyaLogger, get_logger


class TestConfigLoggerIntegration:
    """Test integration between config and logger"""
    
    def test_logger_uses_config_settings(self, monkeypatch):
        """Test that logger properly uses configuration from Config"""
        # Set environment variables for logging config
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        monkeypatch.setenv("LOG_FORMAT", "text")
        monkeypatch.setenv("LOG_OUTPUT", "console")
        monkeypatch.setenv("LOG_CORRELATION_TRACKING", "false")
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        
        # Create config and logger
        config = Config()
        logger = TrivyaLogger(config)
        
        # Verify logger uses config settings
        assert config.logging_config.LOG_LEVEL == "WARNING"
        assert config.logging_config.LOG_FORMAT == "text"
        assert config.logging_config.LOG_CORRELATION_TRACKING is False
    
    def test_logging_config_validation(self, monkeypatch):
        """Test that LoggingConfig validates input correctly"""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("LOG_FORMAT", "json")
        monkeypatch.setenv("LOG_OUTPUT", "both")
        
        log_config = LoggingConfig()
        
        assert log_config.LOG_LEVEL == "DEBUG"
        assert log_config.LOG_FORMAT == "json"
        assert log_config.LOG_OUTPUT == "both"
    
    def test_invalid_log_level_raises_error(self, monkeypatch):
        """Test that invalid log level raises validation error"""
        monkeypatch.setenv("LOG_LEVEL", "INVALID_LEVEL")
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            LoggingConfig()
    
    def test_invalid_log_format_raises_error(self, monkeypatch):
        """Test that invalid log format raises validation error"""
        monkeypatch.setenv("LOG_FORMAT", "xml")
        
        with pytest.raises(Exception):  # Pydantic ValidationError
            LoggingConfig()
    
    def test_logger_with_config_integration(self, monkeypatch, tmp_path):
        """Test full integration: Config -> Logger -> Logging"""
        # Setup environment
        log_file = tmp_path / "integration_test.log"
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "json")
        monkeypatch.setenv("LOG_OUTPUT", "file")
        monkeypatch.setenv("LOG_FILE_PATH", str(log_file))
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        
        # Create config and logger
        config = Config()
        logger = TrivyaLogger(config)
        
        # Log something
        logger.log_agent_action(
            agent_id="test_agent",
            action="integration_test",
            test_data="integration"
        )
        
        # Verify log file was created
        assert log_file.exists()
        
        # Verify log content
        with open(log_file, 'r') as f:
            log_content = f.read()
            assert "test_agent" in log_content
            assert "integration_test" in log_content
    
    def test_logger_defaults_without_config(self):
        """Test that logger works with default settings when no config provided"""
        logger = TrivyaLogger()
        
        # Should use default settings
        component_logger = logger.get_logger("test_component")
        assert component_logger is not None
    
    def test_config_logging_defaults(self):
        """Test that LoggingConfig has sensible defaults"""
        log_config = LoggingConfig()
        
        assert log_config.LOG_LEVEL == "INFO"
        assert log_config.LOG_FORMAT == "json"
        assert log_config.LOG_OUTPUT == "console"
        assert log_config.LOG_CORRELATION_TRACKING is True
        assert log_config.LOG_PERFORMANCE_MONITORING is True
        assert log_config.LOG_SANITIZE_SENSITIVE_DATA is True
    
    def test_logger_respects_config_changes(self, monkeypatch):
        """Test that logger can be reconfigured"""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        
        # Create initial config and logger
        config = Config()
        logger = TrivyaLogger(config)
        
        # Change environment and recreate
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        config2 = Config()
        logger2 = TrivyaLogger(config2)
        
        # Verify new logger uses new config
        assert config2.logging_config.LOG_LEVEL == "ERROR"
    
    def test_integration_with_feature_flags(self, monkeypatch, tmp_path):
        """Test integration with feature flags"""
        # Setup feature flags
        flags_dir = tmp_path / "feature_flags"
        flags_dir.mkdir()
        
        import json
        with open(flags_dir / "test_flags.json", "w") as f:
            json.dump({"enhanced_logging": True, "debug_mode": False}, f)
        
        monkeypatch.setenv("FEATURE_FLAGS_DIR", str(flags_dir))
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        
        # Create config
        config = Config()
        
        # Get feature flags
        flags = config.get_feature_flags('test')
        
        # Verify flags loaded
        assert flags.get('enhanced_logging') is True
        assert flags.get('debug_mode') is False
        
        # Create logger with config
        logger = TrivyaLogger(config)
        
        # If enhanced logging is enabled, performance monitoring should work
        if flags.get('enhanced_logging'):
            logger.log_performance(
                component="test",
                metric="test_metric",
                value=1.23
            )
    
    def test_logger_sanitization_with_config(self, monkeypatch):
        """Test that logger sanitization respects config settings"""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        monkeypatch.setenv("LOG_SANITIZE_SENSITIVE_DATA", "true")
        
        config = Config()
        logger = TrivyaLogger(config)
        
        # Verify sanitization is enabled
        assert config.logging_config.LOG_SANITIZE_SENSITIVE_DATA is True
        
        # Test sanitization
        sensitive_data = {
            "user": "john",
            "password": "secret123",
            "api_key": "key_abc"
        }
        
        sanitized = logger.sanitize_log_data(sensitive_data)
        
        assert sanitized["user"] == "john"
        assert sanitized["password"] == "***REDACTED***"
        assert sanitized["api_key"] == "***REDACTED***"
    
    def test_correlation_tracking_config(self, monkeypatch):
        """Test correlation tracking configuration"""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        monkeypatch.setenv("LOG_CORRELATION_TRACKING", "true")
        
        config = Config()
        logger = TrivyaLogger(config)
        
        # Verify correlation tracking is enabled
        assert config.logging_config.LOG_CORRELATION_TRACKING is True
        
        # Create correlation ID
        correlation_id = logger.create_correlation_id()
        assert correlation_id.startswith("req_")
    
    def test_performance_monitoring_config(self, monkeypatch):
        """Test performance monitoring configuration"""
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
        monkeypatch.setenv("LOG_PERFORMANCE_MONITORING", "true")
        
        config = Config()
        logger = TrivyaLogger(config)
        
        # Verify performance monitoring is enabled
        assert config.logging_config.LOG_PERFORMANCE_MONITORING is True
        
        # Log performance metric
        logger.log_performance(
            component="test_component",
            metric="response_time",
            value=0.123
        )
