"""
Tests for Pricing Optimizer Module
"""

import pytest
from unittest.mock import MagicMock, patch
from shared.core_functions.pricing_optimizer import PricingOptimizer, get_pricing_optimizer
from shared.core_functions.config import Config

@pytest.fixture
def mock_config():
    """Create a mock configuration object"""
    config = MagicMock(spec=Config)
    # Mock env dictionary
    config.env = {
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
        "LOG_OUTPUT": "console"
    }
    # Mock logging_config object
    config.logging_config = MagicMock()
    config.logging_config.LOG_LEVEL = "INFO"
    config.logging_config.LOG_FORMAT = "json"
    config.logging_config.LOG_OUTPUT = "console"
    config.logging_config.LOG_FILE_PATH = "logs/test.log"
    return config

@pytest.fixture
def optimizer(mock_config):
    """Create a PricingOptimizer instance for testing"""
    # Reset singleton
    import shared.core_functions.pricing_optimizer as po
    po._pricing_optimizer_instance = None
    return PricingOptimizer(mock_config)

def test_initialization(optimizer):
    """Test that the optimizer initializes correctly"""
    assert optimizer.config is not None
    assert optimizer.pricing_rules is not None
    assert "variants" in optimizer.pricing_rules

def test_compare_tier_costs(optimizer):
    """Test base cost calculation for different tiers"""
    # Test 1 Mini
    counts = {"mini": 1}
    result = optimizer.compare_tier_costs(counts)
    assert result["total_monthly_cost"] == 1000
    assert result["total_capacity"]["calls"] == 2
    assert result["total_capacity"]["tickets"] == 200

    # Test 2 Minis vs 1 Standard
    # 2 Minis = $2000
    mini_result = optimizer.compare_tier_costs({"mini": 2})
    assert mini_result["total_monthly_cost"] == 2000
    
    # 1 Standard = $2500
    std_result = optimizer.compare_tier_costs({"standard": 1})
    assert std_result["total_monthly_cost"] == 2500

def test_calculate_usage_cost_no_overage(optimizer):
    """Test usage cost calculation without overages"""
    usage_data = {
        "tickets_per_day": 150,
        "concurrent_calls": 1,
        "current_plan": {"mini": 1}
    }
    result = optimizer.calculate_usage_cost(usage_data)
    
    assert result["base_cost"] == 1000
    assert result["overage_costs"]["total"] == 0
    assert result["total_estimated_monthly_cost"] == 1000

def test_calculate_usage_cost_with_overage(optimizer):
    """Test usage cost calculation with ticket and call overages"""
    # Mini has 200 tickets, 2 calls
    usage_data = {
        "tickets_per_day": 250,  # 50 over
        "concurrent_calls": 3,   # 1 over
        "current_plan": {"mini": 1}
    }
    result = optimizer.calculate_usage_cost(usage_data)
    
    # Ticket overage: 50 * 30 days * $0.10 = $150
    expected_ticket_cost = 50 * 30 * 0.10
    assert result["overage_costs"]["tickets"]["cost_monthly"] == expected_ticket_cost
    
    # Call overage: 1 * $75 = $75
    expected_call_cost = 75
    assert result["overage_costs"]["calls"]["cost_monthly"] == expected_call_cost
    
    expected_total = 1000 + expected_ticket_cost + expected_call_cost
    assert result["total_estimated_monthly_cost"] == expected_total

def test_calculate_manager_time_cost(optimizer):
    """Test manager time cost calculation"""
    # 10 escalations/day, 5 mins each
    # 50 mins/day -> 0.833 hrs/day
    # 0.833 * 22 days = 18.33 hrs/month
    # 18.33 * $50 = $916.66
    
    result = optimizer.calculate_manager_time_cost(10, 5)
    
    assert result["escalations_per_day"] == 10
    assert result["hourly_rate"] == 50
    # Allow for small floating point differences
    assert 910 < result["monthly_cost"] < 920

def test_detect_inefficient_stacking(optimizer):
    """Test anti-arbitrage logic"""
    # Scenario: High volume of tickets (500/day) on Mini plan
    # Mini (20% escalation) -> 100 escalations/day
    # Manager cost: 100 * 5min = 500min/day = 8.3hr/day * 22 = 183hr/mo * $50 = $9150/mo!
    # Base cost: $1000
    # Total: ~$10,150
    
    # Standard (10% escalation) -> 50 escalations/day -> ~$4575 manager cost
    # High (5% escalation) -> 25 escalations/day -> ~$2287 manager cost
    
    usage_data = {"tickets_per_day": 500}
    current_config = {"mini": 1}
    
    result = optimizer.detect_inefficient_stacking(current_config, usage_data)
    
    assert result["is_efficient"] is False
    assert len(result["recommendations"]) > 0
    assert result["hidden_costs"] > 5000  # High manager costs
    
    # Should recommend upgrading
    rec = result["recommendations"][0]
    assert rec["tier"] in ["standard", "high"]

def test_generate_cost_analysis(optimizer):
    """Test full cost analysis report"""
    usage_data = {"tickets_per_day": 200, "concurrent_calls": 2}
    current_config = {"mini": 1}
    
    analysis = optimizer.generate_cost_analysis(current_config, usage_data)
    
    assert "cost_breakdown" in analysis
    assert "roi_analysis" in analysis
    assert analysis["cost_breakdown"]["platform_fees"] == 1000
    assert analysis["roi_analysis"]["monthly_savings"] > 0  # Should save vs human

def test_singleton_pattern(mock_config):
    """Test singleton instance retrieval"""
    # Reset singleton
    import shared.core_functions.pricing_optimizer as po
    po._pricing_optimizer_instance = None
    
    opt1 = get_pricing_optimizer(mock_config)
    opt2 = get_pricing_optimizer(mock_config)
    
    assert opt1 is opt2
    assert isinstance(opt1, PricingOptimizer)

def test_invalid_variant(optimizer):
    """Test handling of invalid variant types"""
    counts = {"mega_ultra_tier": 1}
    # Should handle gracefully (log error and skip or return 0 cost for that item)
    # Our implementation logs error and continues
    result = optimizer.compare_tier_costs(counts)
    assert result["total_monthly_cost"] == 0
