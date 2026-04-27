"""Observation module for the Newsletter Online Profit Environment."""

from dataclasses import dataclass, field
from typing import Dict, Any, List
import numpy as np


@dataclass
class Observation:
    """Observation from the newsletter environment.
    
    Attributes:
        subscribers: Current number of subscribers
        cumulative_profit: Total profit accumulated
        revenue: Current week's revenue
        profit: Current week's profit
        engagement_score: Current engagement score (0-1)
        churn_rate: Current churn rate (0-1)
        acquisition_rate: Current acquisition rate (0-1)
        seasonal_factor: Current seasonal factor
        competitor_pressure: Current competitor pressure
        week: Current week number
        history: Recent history of observations
    """
    subscribers: int = 0
    cumulative_profit: float = 0.0
    revenue: float = 0.0
    profit: float = 0.0
    engagement_score: float = 0.75
    churn_rate: float = 0.05
    acquisition_rate: float = 0.1
    seasonal_factor: float = 1.0
    competitor_pressure: float = 0.5
    week: int = 0
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert observation to dictionary."""
        return {
            'subscribers': self.subscribers,
            'cumulative_profit': self.cumulative_profit,
            'revenue': self.revenue,
            'profit': self.profit,
            'engagement_score': self.engagement_score,
            'churn_rate': self.churn_rate,
            'acquisition_rate': self.acquisition_rate,
            'seasonal_factor': self.seasonal_factor,
            'competitor_pressure': self.competitor_pressure,
            'week': self.week,
        }
    
    def to_array(self) -> np.ndarray:
        """Convert observation to numpy array.
        
        Returns:
            Array of observation features
        """
        return np.array([
            self.subscribers / 10000.0,  # Normalize subscribers
            self.cumulative_profit / 10000.0,  # Normalize profit
            self.revenue / 10000.0,  # Normalize revenue
            self.profit / 1000.0,  # Normalize profit
            self.engagement_score,
            self.churn_rate,
            self.acquisition_rate,
            self.seasonal_factor,
            self.competitor_pressure,
            self.week / 52.0,  # Normalize week
        ])
    
    @classmethod
    def from_state(cls, state) -> 'Observation':
        """Create observation from state.
        
        Args:
            state: NewsletterState object
            
        Returns:
            Observation object
        """
        return cls(
            subscribers=state.subscribers,
            cumulative_profit=state.cumulative_profit,
            revenue=state.revenue,
            profit=state.profit,
            engagement_score=state.engagement_score,
            churn_rate=state.churn_rate,
            acquisition_rate=state.acquisition_rate,
            seasonal_factor=state.seasonal_factor,
            competitor_pressure=state.competitor_pressure,
            week=state.week,
        )
