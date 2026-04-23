"""Configuration for the newsletter profit simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimConfig:
    """Configuration for the newsletter profit simulator.

    Attributes:
        initial_subscribers: Starting number of subscribers
        initial_revenue: Starting monthly revenue in dollars
        growth_rate: Monthly subscriber growth rate (0.0 to 1.0)
        churn_rate: Monthly subscriber churn rate (0.0 to 1.0)
        revenue_per_subscriber: Monthly revenue per subscriber in dollars
        content_cost: Monthly content creation cost in dollars
        marketing_cost: Monthly marketing cost in dollars
        platform_fee: Platform fee percentage (0.0 to 1.0)
        max_months: Maximum simulation months
        seed: Random seed for reproducibility
    """

    initial_subscribers: int = 1000
    initial_revenue: float = 5000.0
    growth_rate: float = 0.05
    churn_rate: float = 0.02
    revenue_per_subscriber: float = 5.0
    content_cost: float = 1000.0
    marketing_cost: float = 500.0
    platform_fee: float = 0.05
    max_months: int = 12
    seed: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not 0.0 <= self.growth_rate <= 1.0:
            raise ValueError("growth_rate must be between 0.0 and 1.0")
        if not 0.0 <= self.churn_rate <= 1.0:
            raise ValueError("churn_rate must be between 0.0 and 1.0")
        if not 0.0 <= self.platform_fee <= 1.0:
            raise ValueError("platform_fee must be between 0.0 and 1.0")
        if self.max_months <= 0:
            raise ValueError("max_months must be positive")
        if self.initial_subscribers < 0:
            raise ValueError("initial_subscribers must be non-negative")
        if self.initial_revenue < 0:
            raise ValueError("initial_revenue must be non-negative")
        if self.revenue_per_subscriber < 0:
            raise ValueError("revenue_per_subscriber must be non-negative")
        if self.content_cost < 0:
            raise ValueError("content_cost must be non-negative")
        if self.marketing_cost < 0:
            raise ValueError("marketing_cost must be non-negative")

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "initial_subscribers": self.initial_subscribers,
            "initial_revenue": self.initial_revenue,
            "growth_rate": self.growth_rate,
            "churn_rate": self.churn_rate,
            "revenue_per_subscriber": self.revenue_per_subscriber,
            "content_cost": self.content_cost,
            "marketing_cost": self.marketing_cost,
            "platform_fee": self.platform_fee,
            "max_months": self.max_months,
            "seed": self.seed,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SimConfig:
        """Create configuration from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
