"""State representation for the newsletter profit simulator."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class NewsletterState:
    """Represents the state of a newsletter business at a given month.

    Attributes:
        month: Current month number (0-indexed)
        subscribers: Current number of subscribers
        revenue: Current monthly revenue in dollars
        costs: Current monthly costs in dollars
        profit: Current monthly profit in dollars
        cumulative_profit: Total profit accumulated so far
        churned_subscribers: Number of subscribers lost this month
        new_subscribers: Number of new subscribers gained this month
        growth_rate: Actual growth rate this month
        churn_rate: Actual churn rate this month
        revenue_per_subscriber: Revenue per subscriber this month
        is_terminated: Whether the simulation has terminated
        termination_reason: Reason for termination if applicable
    """

    month: int = 0
    subscribers: int = 0
    revenue: float = 0.0
    costs: float = 0.0
    profit: float = 0.0
    cumulative_profit: float = 0.0
    churned_subscribers: int = 0
    new_subscribers: int = 0
    growth_rate: float = 0.0
    churn_rate: float = 0.0
    revenue_per_subscriber: float = 0.0
    is_terminated: bool = False
    termination_reason: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert state to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> NewsletterState:
        """Create state from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def __repr__(self) -> str:
        """String representation of the state."""
        return (
            f"NewsletterState(month={self.month}, subscribers={self.subscribers}, "
            f"revenue=${self.revenue:.2f}, profit=${self.profit:.2f}, "
            f"cumulative=${self.cumulative_profit:.2f})"
        )
