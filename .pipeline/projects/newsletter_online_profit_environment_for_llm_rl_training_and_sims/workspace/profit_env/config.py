"""Configuration module for the Newsletter Online Profit Environment."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimConfig:
    """Configuration for the newsletter simulation.
    
    Attributes:
        subscriber_count: Initial number of subscribers
        cpc: Cost per click for advertising
        retention: Subscriber retention rate (0-1)
        arpu: Average revenue per user per week
        ad_rate: Revenue rate from ads per subscriber
        sponsor_rate: Revenue rate from sponsors per subscriber
        content_cost: Weekly content creation cost
        operational_cost: Weekly operational cost
        growth: Organic growth rate (0-1)
        churn: Churn rate (0-1)
        seasonal: Seasonal factor (0-2, where 1 is normal)
        competitors: Number of competing newsletters
        saturation: Market saturation factor (0-1)
        conversion: Conversion rate from ad clicks
        engagement: Engagement score (0-1)
        sponsor_fill: Sponsor fill rate (0-1)
        refund: Refund rate (0-1)
        tax: Tax rate (0-1)
        discount: Discount rate for early subscribers (0-1)
        max_steps: Maximum simulation steps (weeks)
    """
    subscriber_count: int = 1000
    cpc: float = 2.50
    retention: float = 0.95
    arpu: float = 5.00
    ad_rate: float = 0.50
    sponsor_rate: float = 100.00
    content_cost: float = 500.00
    operational_cost: float = 300.00
    growth: float = 0.1
    churn: float = 0.05
    seasonal: float = 1.0
    competitors: int = 5
    saturation: float = 0.3
    conversion: float = 0.02
    engagement: float = 0.75
    sponsor_fill: float = 0.8
    refund: float = 0.01
    tax: float = 0.25
    discount: float = 0.1
    max_steps: int = 52
    
    def __post_init__(self):
        """Validate configuration values."""
        if not 0 <= self.retention <= 1:
            raise ValueError("retention must be between 0 and 1")
        if not 0 <= self.churn <= 1:
            raise ValueError("churn must be between 0 and 1")
        if not 0 <= self.seasonal <= 2:
            raise ValueError("seasonal must be between 0 and 2")
        if not 0 <= self.saturation <= 1:
            raise ValueError("saturation must be between 0 and 1")
        if not 0 <= self.conversion <= 1:
            raise ValueError("conversion must be between 0 and 1")
        if not 0 <= self.engagement <= 1:
            raise ValueError("engagement must be between 0 and 1")
        if not 0 <= self.sponsor_fill <= 1:
            raise ValueError("sponsor_fill must be between 0 and 1")
        if not 0 <= self.refund <= 1:
            raise ValueError("refund must be between 0 and 1")
        if not 0 <= self.tax <= 1:
            raise ValueError("tax must be between 0 and 1")
        if not 0 <= self.discount <= 1:
            raise ValueError("discount must be between 0 and 1")
        if self.max_steps <= 0:
            raise ValueError("max_steps must be positive")
    
    @classmethod
    def default(cls) -> 'SimConfig':
        """Create a default configuration."""
        return cls()
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SimConfig':
        """Create a configuration from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            'subscriber_count': self.subscriber_count,
            'cpc': self.cpc,
            'retention': self.retention,
            'arpu': self.arpu,
            'ad_rate': self.ad_rate,
            'sponsor_rate': self.sponsor_rate,
            'content_cost': self.content_cost,
            'operational_cost': self.operational_cost,
            'growth': self.growth,
            'churn': self.churn,
            'seasonal': self.seasonal,
            'competitors': self.competitors,
            'saturation': self.saturation,
            'conversion': self.conversion,
            'engagement': self.engagement,
            'sponsor_fill': self.sponsor_fill,
            'refund': self.refund,
            'tax': self.tax,
            'discount': self.discount,
            'max_steps': self.max_steps,
        }
