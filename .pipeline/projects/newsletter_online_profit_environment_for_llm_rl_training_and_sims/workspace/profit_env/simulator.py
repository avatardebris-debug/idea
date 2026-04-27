"""Simulation logic for the Newsletter Online Profit Environment."""

import numpy as np
from typing import Dict, Any, Tuple

from .config import SimConfig
from .state import NewsletterState, SimulationHistory


class NewsletterSimulator:
    """Newsletter simulation engine.
    
    Simulates the weekly operations of a newsletter business including
    subscriber growth, churn, revenue generation, and costs.
    """
    
    def __init__(self, config: SimConfig):
        """Initialize the simulator.
        
        Args:
            config: Simulation configuration
        """
        self.config = config
        self.state = NewsletterState()
        self.history = SimulationHistory()
        self._rng = np.random.default_rng()
    
    def reset(self) -> NewsletterState:
        """Reset the simulation to initial state.
        
        Returns:
            Initial state
        """
        self.state.reset()
        self.state.subscribers = self.config.subscriber_count
        self.state.engagement_score = self.config.engagement
        self.state.seasonal_factor = self.config.seasonal
        self.state.competitor_pressure = self._calculate_competitor_pressure()
        self.history = SimulationHistory()
        return self.state
    
    def step(self, action: np.ndarray) -> Tuple[NewsletterState, Dict[str, Any]]:
        """Execute one simulation step.
        
        Args:
            action: Action array [marketing, content, pricing, retention]
            
        Returns:
            Tuple of (state, info)
        """
        # Clamp action values to [0, 1]
        action = np.clip(action, 0.0, 1.0)
        
        # Extract action components
        marketing_effort = action[0]
        content_quality = action[1]
        pricing_strategy = action[2]
        retention_effort = action[3]
        
        # Calculate metrics
        self._calculate_revenue(marketing_effort, content_quality, pricing_strategy)
        self._calculate_costs(content_quality)
        self._calculate_subscriber_changes(marketing_effort, retention_effort)
        self._update_state_metrics()
        
        # Update state
        self.state.week += 1
        
        # Record state
        record = self._create_record()
        self.history.add_record(record)
        
        # Calculate reward
        reward = self._calculate_reward()
        
        # Check termination
        terminated = self.state.week >= self.config.max_steps
        
        info = {
            'revenue': self.state.revenue,
            'costs': self.state.costs,
            'profit': self.state.profit,
            'subscribers': self.state.subscribers,
            'churned': self._calculate_churned(),
            'acquired': self._calculate_acquired(),
        }
        
        return self.state, info
    
    def _calculate_competitor_pressure(self) -> float:
        """Calculate competitor pressure based on configuration."""
        # More competitors = higher pressure
        base_pressure = min(self.config.competitors / 10.0, 1.0)
        # Saturation increases pressure
        return base_pressure * (1 + self.config.saturation)
    
    def _calculate_revenue(self, marketing_effort: float, 
                          content_quality: float, pricing_strategy: float) -> None:
        """Calculate weekly revenue.
        
        Args:
            marketing_effort: Marketing effort level (0-1)
            content_quality: Content quality level (0-1)
            pricing_strategy: Pricing strategy level (0-1)
        """
        # Base revenue from ARPU
        base_revenue = self.state.subscribers * self.config.arpu
        
        # Adjust for pricing strategy
        price_multiplier = 1.0 + (pricing_strategy * 0.5)
        
        # Ad revenue
        ad_revenue = self.state.subscribers * self.config.ad_rate * marketing_effort
        
        # Sponsor revenue
        sponsor_multiplier = self.config.sponsor_fill * content_quality
        sponsor_revenue = self.state.subscribers * self.config.sponsor_rate * sponsor_multiplier
        
        # Apply seasonal factor
        seasonal_multiplier = self.config.seasonal
        
        self.state.ad_revenue = ad_revenue
        self.state.sponsor_revenue = sponsor_revenue
        self.state.revenue = (base_revenue * price_multiplier + 
                             ad_revenue + sponsor_revenue) * seasonal_multiplier
    
    def _calculate_costs(self, content_quality: float) -> None:
        """Calculate weekly costs.
        
        Args:
            content_quality: Content quality level (0-1)
        """
        # Base costs
        base_costs = self.config.content_cost + self.config.operational_cost
        
        # Content quality increases costs
        quality_multiplier = 1.0 + (content_quality * 0.5)
        
        # Marketing costs (CPC * clicks)
        marketing_cost = self.config.cpc * self.state.subscribers * 0.1
        
        self.state.costs = (base_costs * quality_multiplier + marketing_cost)
    
    def _calculate_subscriber_changes(self, marketing_effort: float,
                                     retention_effort: float) -> None:
        """Calculate subscriber changes.
        
        Args:
            marketing_effort: Marketing effort level (0-1)
            retention_effort: Retention effort level (0-1)
        """
        # Calculate churn
        base_churn_rate = self.config.churn
        churn_rate = base_churn_rate * (1 - retention_effort * 0.5)
        churned = int(self.state.subscribers * churn_rate)
        
        # Calculate acquisition
        base_growth_rate = self.config.growth
        acquisition_rate = base_growth_rate * (1 + marketing_effort)
        
        # Market saturation effect
        saturation_factor = 1.0 - self.config.saturation
        acquisition_rate *= saturation_factor
        
        # Seasonal effect
        seasonal_factor = self.config.seasonal
        
        acquired = int(self.state.subscribers * acquisition_rate * seasonal_factor)
        
        # Update subscriber count
        self.state.subscribers = max(0, self.state.subscribers - churned + acquired)
    
    def _update_state_metrics(self) -> None:
        """Update state metrics."""
        # Calculate profit
        self.state.profit = self.state.revenue - self.state.costs
        
        # Apply tax
        self.state.profit *= (1 - self.config.tax)
        
        # Update cumulative profit
        self.state.cumulative_profit += self.state.profit
        
        # Update engagement score
        self.state.engagement_score = self.config.engagement
    
    def _calculate_reward(self) -> float:
        """Calculate reward for the step.
        
        Returns:
            Reward value
        """
        # Primary reward: profit
        reward = self.state.profit
        
        # Bonus for subscriber growth
        if self.state.subscribers > self.config.subscriber_count:
            growth_bonus = self.state.subscribers * 0.01
            reward += growth_bonus
        
        # Penalty for low engagement
        if self.state.engagement_score < 0.5:
            penalty = (0.5 - self.state.engagement_score) * 10
            reward -= penalty
        
        return reward
    
    def _calculate_churned(self) -> int:
        """Calculate number of churned subscribers."""
        churn_rate = self.config.churn * (1 - self.config.retention)
        return int(self.state.subscribers * churn_rate)
    
    def _calculate_acquired(self) -> int:
        """Calculate number of acquired subscribers."""
        acquisition_rate = self.config.growth * (1 + self.config.growth)
        return int(self.state.subscribers * acquisition_rate)
    
    def _create_record(self) -> Dict[str, Any]:
        """Create a record for the current week."""
        return {
            'week': self.state.week,
            'subscribers': self.state.subscribers,
            'revenue': self.state.revenue,
            'sponsor_revenue': self.state.sponsor_revenue,
            'ad_revenue': self.state.ad_revenue,
            'costs': self.state.costs,
            'profit': self.state.profit,
            'cumulative_profit': self.state.cumulative_profit,
            'engagement_score': self.state.engagement_score,
            'churn_rate': self.state.churn_rate,
            'acquisition_rate': self.state.acquisition_rate,
        }
    
    def run(self, action_generator=None) -> SimulationHistory:
        """Run full simulation.
        
        Args:
            action_generator: Optional function that generates actions
            
        Returns:
            Simulation history
        """
        self.reset()
        
        while self.state.week < self.config.max_steps:
            if action_generator:
                action = action_generator(self.state)
            else:
                # Default: no action (neutral)
                action = np.array([0.5, 0.5, 0.5, 0.5])
            
            self.step(action)
        
        return self.history
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics.
        
        Returns:
            Dictionary with aggregated statistics
        """
        return self.history.get_statistics()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert simulation to dictionary."""
        return {
            'config': self.config.to_dict(),
            'state': self.state.to_dict(),
            'history': self.history.to_dict(),
        }
