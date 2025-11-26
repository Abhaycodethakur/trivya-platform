"""
Example Usage of Trivya Logger System

This file demonstrates how to use the centralized logging system
in various scenarios across the Trivya platform.
"""

import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.core_functions.logger import TrivyaLogger, PerformanceTimer, get_logger
from shared.core_functions.config import Config


# Example 1: Basic Logger Setup
def example_basic_setup():
    """Example: Initialize and use basic logger"""
    print("\n=== Example 1: Basic Logger Setup ===")
    
    # Get logger instance (singleton)
    logger = get_logger()
    
    # Get component-specific logger
    agent_logger = logger.get_logger("faq_agent")
    
    # Log a simple message
    agent_logger.info("FAQ Agent initialized successfully")
    
    print("✓ Basic logging setup complete")


# Example 2: Agent Action Logging with Correlation
def example_agent_logging():
    """Example: Log AI agent actions with correlation tracking"""
    print("\n=== Example 2: Agent Action Logging ===")
    
    logger = get_logger()
    
    # Create correlation ID for tracking this request
    correlation_id = logger.create_correlation_id()
    print(f"Generated correlation ID: {correlation_id}")
    
    # Log agent action with context
    logger.log_agent_action(
        agent_id="faq_agent_001",
        action="processed_faq_request",
        correlation_id=correlation_id,
        customer_id="cust_12345",
        question="How do I reset my password?",
        response_time=0.45,
        confidence_score=0.95
    )
    
    print("✓ Agent action logged with correlation ID")


# Example 3: Workflow Tracking
def example_workflow_tracking():
    """Example: Track multi-step workflow execution"""
    print("\n=== Example 3: Workflow Tracking ===")
    
    logger = get_logger()
    correlation_id = logger.create_correlation_id()
    
    # Log each step of the workflow with same correlation ID
    logger.log_workflow_step(
        workflow_id="ticket_resolution_001",
        step="ticket_received",
        correlation_id=correlation_id,
        ticket_id="TKT-12345",
        priority="high"
    )
    
    logger.log_workflow_step(
        workflow_id="ticket_resolution_001",
        step="agent_assigned",
        correlation_id=correlation_id,
        agent_id="agent_003"
    )
    
    logger.log_workflow_step(
        workflow_id="ticket_resolution_001",
        step="ticket_resolved",
        correlation_id=correlation_id,
        resolution_time=120.5
    )
    
    print("✓ Workflow tracked across multiple steps")


# Example 4: Performance Monitoring
def example_performance_monitoring():
    """Example: Monitor and log performance metrics"""
    print("\n=== Example 4: Performance Monitoring ===")
    
    logger = get_logger()
    correlation_id = logger.create_correlation_id()
    
    # Method 1: Using PerformanceTimer context manager
    with PerformanceTimer(logger, "database", "query_execution", correlation_id):
        # Simulate database query
        import time
        time.sleep(0.1)
    
    # Method 2: Manual performance logging
    logger.log_performance(
        component="api_endpoint",
        metric="response_time",
        value=0.234,
        correlation_id=correlation_id,
        endpoint="/api/v1/tickets",
        method="GET"
    )
    
    print("✓ Performance metrics logged")


# Example 5: Secure Logging (Sensitive Data Sanitization)
def example_secure_logging():
    """Example: Log data while protecting sensitive information"""
    print("\n=== Example 5: Secure Logging ===")
    
    logger = get_logger()
    
    # This data contains sensitive information
    user_data = {
        "user_id": "user_123",
        "email": "john@example.com",
        "password": "super_secret_123",  # Will be redacted
        "api_key": "sk_live_abc123",     # Will be redacted
        "preferences": {
            "theme": "dark",
            "notifications": True
        }
    }
    
    # Log with automatic sanitization
    logger.log_agent_action(
        agent_id="auth_agent",
        action="user_login",
        **user_data
    )
    
    print("✓ Sensitive data automatically sanitized in logs")


# Example 6: Error Logging
def example_error_logging():
    """Example: Log errors with full context"""
    print("\n=== Example 6: Error Logging ===")
    
    logger = get_logger()
    correlation_id = logger.create_correlation_id()
    
    try:
        # Simulate an error
        result = 10 / 0
    except Exception as e:
        logger.log_error(
            component="calculation_service",
            error=e,
            correlation_id=correlation_id,
            operation="divide",
            input_values={"numerator": 10, "denominator": 0}
        )
    
    print("✓ Error logged with traceback and context")


# Example 7: Integration with Config
def example_config_integration():
    """Example: Use logger with configuration system"""
    print("\n=== Example 7: Config Integration ===")
    
    try:
        # Initialize with config (requires DATABASE_URL env var)
        import os
        os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/trivya")
        
        config = Config()
        logger = TrivyaLogger(config)
        
        # Logger will use settings from config
        component_logger = logger.get_logger("configured_component")
        component_logger.info("Logger initialized with configuration")
        
        print("✓ Logger integrated with configuration system")
    except Exception as e:
        print(f"✓ Config integration example (skipped - missing config: {e})")


# Example 8: Multi-Component Logging
def example_multi_component():
    """Example: Use different loggers for different components"""
    print("\n=== Example 8: Multi-Component Logging ===")
    
    logger = get_logger()
    correlation_id = logger.create_correlation_id()
    
    # Different components can have their own loggers
    faq_logger = logger.get_logger("faq_agent")
    billing_logger = logger.get_logger("billing_agent")
    workflow_logger = logger.get_logger("workflow_engine")
    
    # Each logs with the same correlation ID
    faq_logger.info(f"FAQ query processed - {correlation_id}")
    billing_logger.info(f"Billing check completed - {correlation_id}")
    workflow_logger.info(f"Workflow step executed - {correlation_id}")
    
    print("✓ Multiple components logged with shared correlation")


if __name__ == "__main__":
    print("=" * 60)
    print("Trivya Logger System - Usage Examples")
    print("=" * 60)
    
    # Run all examples
    example_basic_setup()
    example_agent_logging()
    example_workflow_tracking()
    example_performance_monitoring()
    example_secure_logging()
    example_error_logging()
    example_config_integration()
    example_multi_component()
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)
