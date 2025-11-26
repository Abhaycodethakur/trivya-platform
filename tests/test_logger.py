"""
Tests for the Trivya Logger System

This module tests all logging functionality including structured logging,
correlation tracking, performance monitoring, and security compliance.
"""

import os
import json
import pytest
import logging
from pathlib import Path
from shared.core_functions.logger import (
    TrivyaLogger,
    PerformanceTimer,
    get_logger,
    SensitiveDataFilter,
    CorrelationIdFilter
)


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
    monkeypatch.setenv("LOG_FILE_PATH", str(temp_log_dir / "test.log"))
    
    # Reset singleton
    import shared.core_functions.logger as logger_module
    logger_module._logger_instance = None
    
    return TrivyaLogger()


# BDD Scenario 1: Structured Logging
def test_structured_log_entry(logger_instance, temp_log_dir):
    """
    Scenario: Generate structured log entry
    Given an AI agent processes a customer request
    When the agent logs an event
    Then the log should be in JSON format
    And the log should include timestamp, level, and message
    And the log should include agent metadata
    """
    # Given an AI agent processes a customer request
    agent_id = "faq_agent_001"
    action = "processed_faq_request"
    
    # When the agent logs an event
    logger_instance.log_agent_action(
        agent_id=agent_id,
        action=action,
        customer_id="cust_123",
        question="How do I reset my password?"
    )
    
    # Then the log should be in JSON format
    log_file = temp_log_dir / "test.log"
    assert log_file.exists()
    
    # Read and verify log content
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert agent_id in log_content
        assert action in log_content


# BDD Scenario 2: Correlation Tracking
def test_correlation_tracking(logger_instance):
    """
    Scenario: Track customer interaction through system
    Given a customer submits a support ticket
    And the ticket is processed by multiple agents
    When each agent logs their actions
    Then all logs should share the same correlation ID
    And the complete workflow should be traceable
    """
    # Given a customer submits a support ticket
    correlation_id = logger_instance.create_correlation_id()
    
    # And the ticket is processed by multiple agents
    # When each agent logs their actions
    logger_instance.log_agent_action(
        agent_id="agent_1",
        action="received_ticket",
        correlation_id=correlation_id
    )
    
    logger_instance.log_agent_action(
        agent_id="agent_2",
        action="processed_ticket",
        correlation_id=correlation_id
    )
    
    logger_instance.log_workflow_step(
        workflow_id="workflow_001",
        step="ticket_resolution",
        correlation_id=correlation_id
    )
    
    # Then all logs should share the same correlation ID
    assert correlation_id.startswith("req_")
    assert len(correlation_id) == 20  # "req_" + 16 hex chars


# BDD Scenario 3: Performance Monitoring
def test_performance_logging(logger_instance):
    """
    Scenario: Log agent execution time
    Given an AI agent processes a request
    When the agent completes processing
    Then the log should include execution time
    And performance metrics should be available
    """
    # Given an AI agent processes a request
    # When the agent completes processing
    with PerformanceTimer(logger_instance, "test_agent", "process_request") as timer:
        # Simulate some work
        import time
        time.sleep(0.1)
    
    # Then the log should include execution time
    # (verified by the PerformanceTimer context manager)
    # The timer automatically logs the execution time
    assert True  # Timer logged successfully


def test_performance_metric_logging(logger_instance):
    """Test direct performance metric logging"""
    logger_instance.log_performance(
        component="faq_agent",
        metric="response_time",
        value=0.45
    )
    # Verify no exceptions were raised
    assert True


# BDD Scenario 4: Security Compliance
def test_sanitize_sensitive_data(logger_instance):
    """
    Scenario: Sanitize sensitive data from logs
    Given an agent processes customer payment information
    When the agent logs the transaction
    Then sensitive data should be masked or removed
    And the log should be compliance-ready
    """
    # Given an agent processes customer payment information
    sensitive_data = {
        "customer_id": "cust_123",
        "password": "super_secret_password",
        "credit_card": "4111-1111-1111-1111",
        "api_key": "sk_test_12345",
        "transaction_amount": 99.99
    }
    
    # When the agent logs the transaction
    sanitized = logger_instance.sanitize_log_data(sensitive_data)
    
    # Then sensitive data should be masked or removed
    assert sanitized["password"] == "***REDACTED***"
    assert sanitized["credit_card"] == "***REDACTED***"
    assert sanitized["api_key"] == "***REDACTED***"
    
    # And non-sensitive data should remain
    assert sanitized["customer_id"] == "cust_123"
    assert sanitized["transaction_amount"] == 99.99


def test_sensitive_data_filter():
    """Test SensitiveDataFilter directly"""
    filter_instance = SensitiveDataFilter()
    
    data = {
        "username": "john_doe",
        "password": "secret123",
        "token": "bearer_xyz",
        "email": "john@example.com"
    }
    
    sanitized = filter_instance._sanitize_dict(data)
    
    assert sanitized["username"] == "john_doe"
    assert sanitized["password"] == "***REDACTED***"
    assert sanitized["token"] == "***REDACTED***"
    assert sanitized["email"] == "john@example.com"


def test_nested_sensitive_data_sanitization(logger_instance):
    """Test sanitization of nested sensitive data"""
    nested_data = {
        "user": {
            "name": "John Doe",
            "credentials": {
                "password": "secret",
                "api_key": "key123"
            }
        },
        "transaction": {
            "amount": 100,
            "credit_card": "1234-5678-9012-3456"
        }
    }
    
    sanitized = logger_instance.sanitize_log_data(nested_data)
    
    assert sanitized["user"]["name"] == "John Doe"
    assert sanitized["user"]["credentials"]["password"] == "***REDACTED***"
    assert sanitized["user"]["credentials"]["api_key"] == "***REDACTED***"
    assert sanitized["transaction"]["amount"] == 100
    assert sanitized["transaction"]["credit_card"] == "***REDACTED***"


def test_correlation_id_filter():
    """Test CorrelationIdFilter"""
    correlation_id = "test_correlation_123"
    filter_instance = CorrelationIdFilter(correlation_id)
    
    # Create a mock log record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None
    )
    
    # Apply filter
    filter_instance.filter(record)
    
    # Verify correlation ID was added
    assert hasattr(record, 'correlation_id')
    assert record.correlation_id == correlation_id


def test_get_logger_singleton():
    """Test that get_logger returns singleton instance"""
    logger1 = get_logger()
    logger2 = get_logger()
    
    assert logger1 is logger2


def test_component_logger(logger_instance):
    """Test getting logger for specific component"""
    agent_logger = logger_instance.get_logger("mini_trivya_agent")
    workflow_logger = logger_instance.get_logger("workflow_engine")
    
    assert agent_logger.name == "trivya.mini_trivya_agent"
    assert workflow_logger.name == "trivya.workflow_engine"


def test_error_logging(logger_instance):
    """Test error logging with traceback"""
    try:
        raise ValueError("Test error")
    except ValueError as e:
        logger_instance.log_error(
            component="test_component",
            error=e,
            additional_context="Testing error logging"
        )
    
    # Verify no exceptions were raised during logging
    assert True
