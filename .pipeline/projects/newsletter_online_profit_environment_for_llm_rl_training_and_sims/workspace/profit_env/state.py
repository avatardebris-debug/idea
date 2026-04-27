"""State management for the Newsletter Online Profit Environment."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class NewsletterState:
    """State of the newsletter simulation.
    
    Attributes:
        week: Current week number
        subscribers: Current number of subscribers
        cumulative_profit: Total profit accumulated
        revenue: Current week's revenue
        sponsor_revenue: Current week's sponsor revenue
        ad_revenue: Current week's ad revenue
        costs: Current week's costs
        profit: Current week's profit
        engagement_score: Current engagement score (0-1)
        churn_rate: Current churn rate (0-1)
        acquisition_rate: Current acquisition rate (0-1)
        seasonal_factor: Current seasonal factor
        competitor_pressure: Current competitor pressure
    """
    week: int = 0
    subscribers: int = 1000
    cumulative_profit: float = 0.0
    revenue: float = 0.0
    sponsor_revenue: float = 0.0
    ad_revenue: float = 0.0
    costs: float = 0.0
    profit: float = 0.0
    engagement_score: float = 0.75
    churn_rate: float = 0.05
    acquisition_rate: float = 0.1
    seasonal_factor: float = 1.0
    competitor_pressure: float = 0.5
    
    def reset(self) -> None:
        """Reset state to initial values."""
        self.week = 0
        self.subscribers = 1000
        self.cumulative_profit = 0.0
        self.revenue = 0.0
        self.sponsor_revenue = 0.0
        self.ad_revenue = 0.0
        self.costs = 0.0
        self.profit = 0.0
        self.engagement_score = 0.75
        self.churn_rate = 0.05
        self.acquisition_rate = 0.1
        self.seasonal_factor = 1.0
        self.competitor_pressure = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            'week': self.week,
            'subscribers': self.subscribers,
            'cumulative_profit': self.cumulative_profit,
            'revenue': self.revenue,
            'sponsor_revenue': self.sponsor_revenue,
            'ad_revenue': self.ad_revenue,
            'costs': self.costs,
            'profit': self.profit,
            'engagement_score': self.engagement_score,
            'churn_rate': self.churn_rate,
            'acquisition_rate': self.acquisition_rate,
            'seasonal_factor': self.seasonal_factor,
            'competitor_pressure': self.competitor_pressure,
        }


@dataclass
class SimulationHistory:
    """History of simulation weeks.
    
    Attributes:
        records: List of weekly records
    """
    records: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_record(self, record: Dict[str, Any]) -> None:
        """Add a weekly record to history."""
        self.records.append(record)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Calculate statistics from history.
        
        Returns:
            Dictionary containing aggregated statistics
        """
        if not self.records:
            return {
                'total_weeks': 0,
                'final_subscribers': 0,
                'total_revenue': 0.0,
                'total_profit': 0.0,
                'average_weekly_profit': 0.0,
                'average_subscribers': 0,
                'peak_subscribers': 0,
                'lowest_subscribers': 0,
            }
        
        total_revenue = sum(r.get('revenue', 0) for r in self.records)
        total_profit = sum(r.get('profit', 0) for r in self.records)
        subscribers_list = [r.get('subscribers', 0) for r in self.records]
        
        return {
            'total_weeks': len(self.records),
            'final_subscribers': self.records[-1].get('subscribers', 0),
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'average_weekly_profit': total_profit / len(self.records),
            'average_subscribers': sum(subscribers_list) / len(subscribers_list),
            'peak_subscribers': max(subscribers_list),
            'lowest_subscribers': min(subscribers_list),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert history to dictionary."""
        return {
            'records': self.records,
            'statistics': self.get_statistics(),
        }
