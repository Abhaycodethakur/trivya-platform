"""
Integration Tests for Pricing Optimizer Module

This module tests the integration between the Pricing Optimizer, Config, and Logger modules.
"""

import pytest
import json
from pathlib import Path
from shared.core_functions.config import Config
from shared.core_functions.logger import TrivyaLogger
from shared.core_functions.pricing_optimizer import PricingOptimizer, get_pricing_optimizer

@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    return {"log_dir": log_dir}

@pytest.fixture
def integrated_components(temp_dirs, monkeypatch):
    """Create integrated components with test configuration"""
    # Set environment variables for Config
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_FORMAT", "json")
    monkeypatch.setenv("LOG_OUTPUT", "file")
    monkeypatch.setenv("LOG_FILE_PATH", str(temp_dirs["log_dir"] / "pricing_test.log"))
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost:5432/test_db")
    
    # Set Pricing Configuration
    monkeypatch.setenv("PRICING_MINI_COST", "900")      # Discounted from 1000
    monkeypatch.setenv("PRICING_STANDARD_COST", "2400") # Discounted from 2500
    monkeypatch.setenv("PRICING_TICKET_OVERAGE_COST", "0.20") # Increased from 0.10
    
    # Reset singletons
    import shared.core_functions.logger as logger_module
    import shared.core_functions.pricing_optimizer as pricing_module
    logger_module._logger_instance = None
    pricing_module._pricing_optimizer_instance = None
    
    config = Config()
    logger = TrivyaLogger(config)
    optimizer = PricingOptimizer(config)
    
    return {
        "config": config,
        "logger": logger,
        "optimizer": optimizer,
        "temp_dirs": temp_dirs
    }

# BDD Scenario 1: Config Integration
def test_pricing_optimizer_uses_config_values(integrated_components):
    """
    Scenario: Pricing optimizer uses values from config
    Given a config with custom pricing
    When pricing optimizer is initialized
    Then it should use the custom pricing values
    """
    optimizer = integrated_components["optimizer"]
    
    # Verify custom values from env vars
    assert optimizer.pricing_rules["variants"]["mini"]["base_cost"] == 900
    assert optimizer.pricing_rules["variants"]["standard"]["base_cost"] == 2400
    assert optimizer.pricing_rules["overage"]["ticket_cost"] == 0.20
    
    # Verify default remains for unset value
    assert optimizer.pricing_rules["variants"]["high"]["base_cost"] == 4000

# BDD Scenario 2: Logger Integration
def test_pricing_operations_are_logged(integrated_components):
    """
    Scenario: Pricing operations are logged
    Given an integrated system
    When pricing calculations are performed
    Then operations should be logged to the file
    """
    optimizer = integrated_components["optimizer"]
    temp_dirs = integrated_components["temp_dirs"]
    
    # Perform calculation
    optimizer.compare_tier_costs({"mini": 2})
    
    # Verify logs
    log_file = temp_dirs["log_dir"] / "pricing_test.log"
    assert log_file.exists()
    
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "tier_comparison_calculated" in log_content
        assert "pricing_optimizer" in log_content

# BDD Scenario 3: Correlation ID Tracking
def test_correlation_id_tracking(integrated_components):
    """
    Scenario: Correlation IDs flow through pricing operations
    Given a logger with a correlation ID
    When pricing operations are performed
    Then the correlation ID should appear in logs
    """
    logger = integrated_components["logger"]
    optimizer = integrated_components["optimizer"]
    temp_dirs = integrated_components["temp_dirs"]
    
    # Set correlation ID
    correlation_id = "pricing_flow_test_123"
    logger.set_correlation_id(correlation_id)
    
    # Perform operations
    optimizer.compare_tier_costs({"standard": 1}, correlation_id=correlation_id)
    optimizer.calculate_usage_cost({"tickets_per_day": 100}, correlation_id=correlation_id)
    
    # Verify logs
    log_file = temp_dirs["log_dir"] / "pricing_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        # Should appear multiple times
        assert log_content.count(correlation_id) >= 2

# BDD Scenario 4: End-to-End Workflow
def test_end_to_end_workflow(integrated_components):
    """
    Scenario: Complete pricing workflow
    Given an integrated system
    When a full cost analysis is generated
    Then all components should interact correctly
    """
    optimizer = integrated_components["optimizer"]
    temp_dirs = integrated_components["temp_dirs"]
    
    current_config = {"mini": 5} # Inefficient stacking
    usage_data = {"tickets_per_day": 1000}
    
    # Generate analysis
    analysis = optimizer.generate_cost_analysis(current_config, usage_data)
    
    # Verify analysis used config values (Mini cost $900 * 5 = $4500)
    assert analysis["cost_breakdown"]["platform_fees"] == 4500
    
    # Verify logging
    log_file = temp_dirs["log_dir"] / "pricing_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "cost_analysis_generated" in log_content
        assert "roi" in log_content

# BDD Scenario 5: Error Handling Integration
def test_error_handling_integration(integrated_components):
    """
    Scenario: Errors are logged properly
    Given an integrated system
    When an invalid operation occurs
    Then the error should be logged
    """
    optimizer = integrated_components["optimizer"]
    temp_dirs = integrated_components["temp_dirs"]
    
    # Trigger error (unknown variant)
    optimizer.compare_tier_costs({"unknown_tier": 1})
    
    # Verify error log
    log_file = temp_dirs["log_dir"] / "pricing_test.log"
    with open(log_file, 'r') as f:
        log_content = f.read()
        assert "error" in log_content
        assert "Unknown variant" in log_content

# BDD Scenario 6: Singleton Integration
def test_singleton_integration(integrated_components):
    """
    Scenario: Singleton works with config
    Given a config
    When get_pricing_optimizer is called
    Then it returns the configured instance
    """
    config = integrated_components["config"]
    
    # Get instance
    opt1 = get_pricing_optimizer(config)
    opt2 = get_pricing_optimizer(config)
    
    assert opt1 is opt2
    assert opt1.config is config
