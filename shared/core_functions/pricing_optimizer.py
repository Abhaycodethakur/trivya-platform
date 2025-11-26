"""
Pricing Optimizer Module for Trivya Platform

This module provides an anti-arbitrage engine that calculates real-time cost comparisons,
prevents inefficient tier stacking, and analyzes ROI.
"""

import os
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

try:
    from shared.core_functions.config import Config
    from shared.core_functions.logger import get_logger, TrivyaLogger
except ImportError:
    Config = None
    get_logger = None
    TrivyaLogger = None

class PricingOptimizer:
    """
    Anti-arbitrage engine for calculating costs and optimizing tier configurations.
    """
    
    # Default pricing rules (fallback if config is missing)
    DEFAULT_PRICING = {
        "variants": {
            "mini": {"base_cost": 1000, "calls": 2, "tickets": 200},
            "standard": {"base_cost": 2500, "calls": 3, "tickets": 300},
            "high": {"base_cost": 4000, "calls": 5, "tickets": 500}
        },
        "overage": {
            "ticket_cost": 0.10,
            "call_slot_cost": 75
        },
        "manager": {
            "hourly_rate": 50
        }
    }

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the Pricing Optimizer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = get_logger(config) if get_logger else None
        
        # Load pricing rules from config or use defaults
        self._load_pricing_rules()
        
        if self.logger:
            self.logger.log_agent_action(
                agent_id="system",
                action="pricing_optimizer_initialized",
                details={"config_loaded": config is not None}
            )

    def _load_pricing_rules(self):
        """Load pricing rules from config or defaults"""
        import copy
        self.pricing_rules = copy.deepcopy(self.DEFAULT_PRICING)
        
        if self.config:
            # Override variant costs
            if self.config.env.get("PRICING_MINI_COST"):
                self.pricing_rules["variants"]["mini"]["base_cost"] = int(self.config.env.get("PRICING_MINI_COST"))
            if self.config.env.get("PRICING_STANDARD_COST"):
                self.pricing_rules["variants"]["standard"]["base_cost"] = int(self.config.env.get("PRICING_STANDARD_COST"))
            if self.config.env.get("PRICING_HIGH_COST"):
                self.pricing_rules["variants"]["high"]["base_cost"] = int(self.config.env.get("PRICING_HIGH_COST"))
                
            # Override overage costs
            if self.config.env.get("PRICING_TICKET_OVERAGE_COST"):
                self.pricing_rules["overage"]["ticket_cost"] = float(self.config.env.get("PRICING_TICKET_OVERAGE_COST"))
                
            # Override manager rate
            if self.config.env.get("PRICING_MANAGER_HOURLY_RATE"):
                self.pricing_rules["manager"]["hourly_rate"] = int(self.config.env.get("PRICING_MANAGER_HOURLY_RATE"))

    def compare_tier_costs(self, variant_counts: Dict[str, int], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate total base cost for a given combination of variants.
        
        Args:
            variant_counts: Dictionary of variant types and their counts
            correlation_id: Optional correlation ID for tracking
                           
        Returns:
            Dictionary with cost breakdown
        """
        total_cost = 0
        breakdown = {}
        total_capacity = {"calls": 0, "tickets": 0}
        
        if not correlation_id and self.logger:
            correlation_id = self.logger.create_correlation_id()
        
        for variant, count in variant_counts.items():
            variant_lower = variant.lower()
            if variant_lower not in self.pricing_rules["variants"]:
                if self.logger:
                    self.logger.log_error(
                        component="pricing_optimizer",
                        error=ValueError(f"Unknown variant: {variant}"),
                        correlation_id=correlation_id
                    )
                continue
                
            rules = self.pricing_rules["variants"][variant_lower]
            variant_cost = rules["base_cost"] * count
            total_cost += variant_cost
            
            breakdown[variant_lower] = {
                "count": count,
                "unit_cost": rules["base_cost"],
                "total_cost": variant_cost
            }
            
            total_capacity["calls"] += rules["calls"] * count
            total_capacity["tickets"] += rules["tickets"] * count
            
        result = {
            "total_monthly_cost": total_cost,
            "breakdown": breakdown,
            "total_capacity": total_capacity
        }
        
        if self.logger:
            self.logger.log_performance(
                component="pricing_optimizer",
                metric="tier_comparison_calculated",
                value=total_cost,
                correlation_id=correlation_id,
                details=result
            )
            
        return result

    def calculate_usage_cost(self, usage_data: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate costs based on actual usage, including overages.
        
        Args:
            usage_data: Dictionary containing usage metrics
            correlation_id: Optional correlation ID for tracking
                       
        Returns:
            Dictionary with usage cost breakdown
        """
        if not correlation_id and self.logger:
            correlation_id = self.logger.create_correlation_id()
        
        tickets_used = usage_data.get("tickets_per_day", 0)
        calls_used = usage_data.get("concurrent_calls", 0)
        current_plan = usage_data.get("current_plan", {})
        
        # Calculate base capacity
        plan_analysis = self.compare_tier_costs(current_plan)
        capacity = plan_analysis["total_capacity"]
        base_cost = plan_analysis["total_monthly_cost"]
        
        # Calculate overages
        ticket_overage = max(0, tickets_used - capacity["tickets"])
        call_overage = max(0, calls_used - capacity["calls"])
        
        # Calculate overage costs
        # Assuming 30 days for monthly ticket overage calculation
        monthly_ticket_overage_cost = ticket_overage * 30 * self.pricing_rules["overage"]["ticket_cost"]
        monthly_call_overage_cost = call_overage * self.pricing_rules["overage"]["call_slot_cost"]
        
        total_overage_cost = monthly_ticket_overage_cost + monthly_call_overage_cost
        total_estimated_cost = base_cost + total_overage_cost
        
        result = {
            "base_cost": base_cost,
            "overage_costs": {
                "tickets": {
                    "overage_count_daily": ticket_overage,
                    "cost_monthly": monthly_ticket_overage_cost
                },
                "calls": {
                    "overage_count": call_overage,
                    "cost_monthly": monthly_call_overage_cost
                },
                "total": total_overage_cost
            },
            "total_estimated_monthly_cost": total_estimated_cost
        }
        
        if self.logger:
            self.logger.log_performance(
                component="pricing_optimizer",
                metric="usage_cost_calculated",
                value=total_estimated_cost,
                correlation_id=correlation_id,
                details={"tickets_used": tickets_used, "calls_used": calls_used}
            )
            
        return result

    def calculate_manager_time_cost(self, escalations_per_day: int, review_time_minutes: int = 5) -> Dict[str, Any]:
        """
        Calculate the monetary cost of manager time spent reviewing escalations.
        
        Args:
            escalations_per_day: Number of tickets escalated to human review
            review_time_minutes: Average time in minutes to review one escalation
            
        Returns:
            Dictionary with time and cost analysis
        """
        minutes_per_day = escalations_per_day * review_time_minutes
        hours_per_day = minutes_per_day / 60
        hours_per_month = hours_per_day * 22  # Assuming 22 working days
        
        hourly_rate = self.pricing_rules["manager"]["hourly_rate"]
        monthly_cost = hours_per_month * hourly_rate
        
        return {
            "escalations_per_day": escalations_per_day,
            "review_time_minutes": review_time_minutes,
            "hours_per_month": round(hours_per_month, 2),
            "monthly_cost": round(monthly_cost, 2),
            "hourly_rate": hourly_rate
        }

    def detect_inefficient_stacking(self, variant_counts: Dict[str, int], usage_data: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect if the current combination of variants is cost-inefficient.
        
        Args:
            variant_counts: Current tier configuration
            usage_data: Usage metrics
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            Dictionary with efficiency analysis and recommendations
        """
        current_analysis = self.compare_tier_costs(variant_counts, correlation_id)
        current_cost = current_analysis["total_monthly_cost"]
        
        recommendations = []
        inefficiencies = []
        
        # Check for Mini stacking (Arbitrage Detection)
        mini_count = variant_counts.get("mini", 0)
        
        # Scenario 1: 3+ Minis ($3000+) vs 1 Trivya High ($4000) or 1 Standard ($2500)
        # Actually, 3 Minis = $3000. 1 Standard = $2500.
        # If you have 3 Minis, you are paying $500 more than Standard for same calls (6 vs 3? No wait)
        # 3 Minis: $3000, 6 calls, 600 tickets
        # 1 Standard: $2500, 3 calls, 300 tickets
        # 1 High: $4000, 5 calls, 500 tickets
        
        # Let's look for clear arbitrage where you pay MORE for LESS or SIMILAR
        
        # Example: 2 Minis ($2000) vs 1 Standard ($2500)
        # 2 Minis: 4 calls, 400 tickets. 1 Standard: 3 calls, 300 tickets.
        # 2 Minis is actually BETTER value than 1 Standard if you just look at raw numbers.
        # BUT, Standard might have features Mini doesn't (not modeled here yet).
        
        # Let's check for the specific example in the prompt:
        # "Compare 2x Mini ($1,000/mo each) vs 1x Trivya ($2,500/mo)"
        # "Compare 3x Mini ($1,000/mo each) vs 1x Trivya High ($4,000/mo)"
        
        # Anti-arbitrage logic often means preventing users from stacking cheaper plans 
        # to get more capacity than a higher tier for less money.
        # OR, it means detecting when they are paying too much.
        # The prompt says "prevent inefficient tier stacking" and "Detect inefficient tier combinations".
        # This usually implies the USER is being inefficient.
        
        # Case: Stacking Minis to avoid buying High
        # If user needs 500 tickets.
        # 3 Minis: $3000, 600 tickets.
        # 1 High: $4000, 500 tickets.
        # Here, stacking Minis is cheaper for the user. This might be "arbitrage" against the platform.
        # However, the prompt asks to "return recommendations for optimal configuration".
        # Usually optimal for the CLIENT.
        
        # Let's look at the prompt example:
        # "If client has 2 Mini agents ($2,000/mo) + 100 escalations/day... recommend 1 Trivya"
        # This implies we need to factor in Manager Cost (Escalations).
        # Higher tiers presumably have better AI, leading to fewer escalations.
        # Let's assume:
        # Mini: 20% escalation rate
        # Standard: 10% escalation rate
        # High: 5% escalation rate
        
        # We need to infer total tickets from usage_data if not provided
        tickets_per_day = usage_data.get("tickets_per_day", 0)
        
        # Calculate escalation costs for current setup
        # We'll assume the current setup has an average escalation rate based on the lowest tier present?
        # Or just use the provided "escalations_per_day" in usage_data if available.
        # If not, we estimate.
        
        # Let's define assumed performance:
        escalation_rates = {"mini": 0.20, "standard": 0.10, "high": 0.05}
        
        # Estimate current blended escalation rate
        total_units = sum(variant_counts.values())
        if total_units == 0:
            return {"status": "no_active_plans"}
            
        # Weighted average of escalation rates
        weighted_rate_sum = 0
        for v, count in variant_counts.items():
            weighted_rate_sum += escalation_rates.get(v.lower(), 0.20) * count
        current_avg_rate = weighted_rate_sum / total_units
        
        estimated_escalations = tickets_per_day * current_avg_rate
        manager_cost = self.calculate_manager_time_cost(estimated_escalations)["monthly_cost"]
        
        total_current_cost_with_manager = current_cost + manager_cost
        
        # Now compare against single-tier consolidations
        alternatives = ["standard", "high"]
        best_option = None
        min_total_cost = total_current_cost_with_manager
        
        for tier in alternatives:
            # How many of this tier needed to cover tickets?
            tier_capacity = self.pricing_rules["variants"][tier]["tickets"]
            count_needed = (tickets_per_day // tier_capacity) + (1 if tickets_per_day % tier_capacity > 0 else 0)
            count_needed = max(1, count_needed) # At least 1
            
            tier_base_cost = self.pricing_rules["variants"][tier]["base_cost"] * count_needed
            tier_rate = escalation_rates[tier]
            tier_escalations = tickets_per_day * tier_rate
            tier_manager_cost = self.calculate_manager_time_cost(tier_escalations)["monthly_cost"]
            
            tier_total_cost = tier_base_cost + tier_manager_cost
            
            if tier_total_cost < min_total_cost:
                min_total_cost = tier_total_cost
                best_option = {
                    "tier": tier,
                    "count": count_needed,
                    "savings": total_current_cost_with_manager - tier_total_cost,
                    "reason": f"Switching to {count_needed}x {tier.title()} reduces escalation costs significantly."
                }
        
        if best_option:
            recommendations.append(best_option)
            inefficiencies.append(f"Current configuration has high hidden costs due to escalations (${manager_cost:.2f}/mo).")

        return {
            "is_efficient": len(recommendations) == 0,
            "current_monthly_total": total_current_cost_with_manager,
            "hidden_costs": manager_cost,
            "inefficiencies": inefficiencies,
            "recommendations": recommendations
        }

    def generate_cost_analysis(self, current_config: Dict[str, int], usage_data: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a detailed cost analysis report.
        
        Args:
            current_config: Current variant counts
            usage_data: Usage metrics
            correlation_id: Optional correlation ID for tracking
            
        Returns:
            Dictionary with full analysis
        """
        if not correlation_id and self.logger:
            correlation_id = self.logger.create_correlation_id()
        
        # 1. Base Costs
        tier_analysis = self.compare_tier_costs(current_config, correlation_id)
        
        # 2. Usage & Overage
        usage_input = usage_data.copy()
        usage_input["current_plan"] = current_config
        usage_analysis = self.calculate_usage_cost(usage_input, correlation_id)
        
        # 3. Efficiency & Manager Costs
        efficiency_analysis = self.detect_inefficient_stacking(current_config, usage_data, correlation_id)
        
        # 4. ROI Analysis (vs Human Agents)
        # Assumption: Human agent costs $3500/mo and handles ~40 tickets/day?
        # Let's use the prompt's implied human cost of $3500/mo.
        tickets_per_day = usage_data.get("tickets_per_day", 0)
        human_capacity_per_day = 40 # Estimate
        humans_needed = (tickets_per_day // human_capacity_per_day) + 1
        human_cost_monthly = humans_needed * 3500
        
        total_ai_cost = efficiency_analysis["current_monthly_total"] # Includes manager time
        savings = human_cost_monthly - total_ai_cost
        roi_percent = (savings / total_ai_cost) * 100 if total_ai_cost > 0 else 0
        
        analysis = {
            "timestamp": datetime.utcnow().isoformat(),
            "configuration": current_config,
            "usage_metrics": usage_data,
            "cost_breakdown": {
                "platform_fees": tier_analysis["total_monthly_cost"],
                "overage_fees": usage_analysis["overage_costs"]["total"],
                "manager_review_costs": efficiency_analysis["hidden_costs"],
                "total_monthly_spend": total_ai_cost
            },
            "efficiency_report": {
                "is_optimized": efficiency_analysis["is_efficient"],
                "recommendations": efficiency_analysis["recommendations"]
            },
            "roi_analysis": {
                "equivalent_human_cost": human_cost_monthly,
                "monthly_savings": savings,
                "roi_percentage": round(roi_percent, 2)
            }
        }
        
        if self.logger:
            self.logger.log_agent_action(
                agent_id="system",
                action="cost_analysis_generated",
                correlation_id=correlation_id,
                details={"savings": savings, "roi": roi_percent}
            )
            
        return analysis

    def recommend_optimal_config(self, usage_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend the optimal configuration based purely on usage needs.
        
        Args:
            usage_data: Usage metrics
            
        Returns:
            Dictionary with recommended configuration
        """
        # Start with a baseline config (e.g., 1 Mini) and optimize
        # This is a simplified version; could be more complex search
        
        # Check efficiency of starting with 1 Mini
        baseline = {"mini": 1}
        analysis = self.detect_inefficient_stacking(baseline, usage_data)
        
        if analysis["recommendations"]:
            # If recommendation exists, take the best one
            rec = analysis["recommendations"][0]
            return {
                "recommended_variant": rec["tier"],
                "count": rec["count"],
                "reason": rec["reason"]
            }
        else:
            return {
                "recommended_variant": "mini",
                "count": 1,
                "reason": "Baseline configuration is sufficient and most cost-effective."
            }


# Singleton instance
_pricing_optimizer_instance: Optional[PricingOptimizer] = None

def get_pricing_optimizer(config: Optional[Config] = None) -> PricingOptimizer:
    """Get singleton pricing optimizer instance"""
    global _pricing_optimizer_instance
    if _pricing_optimizer_instance is None:
        _pricing_optimizer_instance = PricingOptimizer(config)
    return _pricing_optimizer_instance
