"""Core simulation engine for newsletter profit modeling."""

from __future__ import annotations

import random
from typing import Optional

from profit_env.config import SimConfig
from profit_env.state import NewsletterState


class NewsletterSimulator:
    """Simulates a newsletter business over time.

    The simulator models subscriber acquisition, churn, revenue, and costs
    to project the financial trajectory of a newsletter business.

    Attributes:
        config: Configuration for the simulation
        rng: Random number generator for reproducibility
        current_state: Current state of the simulation
    """

    def __init__(self, config: Optional[SimConfig] = None) -> None:
        """Initialize the simulator.

        Args:
            config: Configuration for the simulation. Uses default config if None.
        """
        self.config = config or SimConfig()
        self.rng = random.Random(self.config.seed)
        self.current_state = NewsletterState(
            month=0,
            subscribers=self.config.initial_subscribers,
            revenue=self.config.initial_revenue,
            costs=0.0,
            profit=0.0,
            cumulative_profit=0.0,
            revenue_per_subscriber=self.config.revenue_per_subscriber,
        )

    def step(self) -> NewsletterState:
        """Advance the simulation by one month.

        Returns:
            NewsletterState: The state after this month's changes.
        """
        # Calculate subscriber changes
        churned = int(self.current_state.subscribers * self.config.churn_rate)
        churned = self.rng.randint(max(0, churned - 1), churned + 1)
        churned = min(churned, self.current_state.subscribers)

        new_subs = int(self.current_state.subscribers * self.config.growth_rate)
        new_subs = self.rng.randint(max(0, new_subs - 1), new_subs + 1)

        # Apply changes
        self.current_state.subscribers -= churned
        self.current_state.subscribers += new_subs
        self.current_state.subscribers = max(0, self.current_state.subscribers)

        # Calculate financial metrics
        self.current_state.churned_subscribers = churned
        self.current_state.new_subscribers = new_subs
        self.current_state.growth_rate = new_subs / self.current_state.subscribers if self.current_state.subscribers > 0 else 0.0
        self.current_state.churn_rate = churned / self.current_state.subscribers if self.current_state.subscribers > 0 else 0.0

        # Revenue calculation
        self.current_state.revenue = self.current_state.subscribers * self.config.revenue_per_subscriber
        self.current_state.revenue_per_subscriber = self.config.revenue_per_subscriber

        # Cost calculation
        self.current_state.costs = self.config.content_cost + self.config.marketing_cost

        # Profit calculation
        self.current_state.profit = self.current_state.revenue - self.current_state.costs
        self.current_state.cumulative_profit += self.current_state.profit

        # Advance month
        self.current_state.month += 1

        # Check termination conditions
        if self.current_state.subscribers == 0:
            self.current_state.is_terminated = True
            self.current_state.termination_reason = "No subscribers remaining"
        elif self.current_state.month >= self.config.max_months:
            self.current_state.is_terminated = True
            self.current_state.termination_reason = "Maximum months reached"

        return self.current_state

    def reset(self) -> NewsletterState:
        """Reset the simulation to initial state.

        Returns:
            NewsletterState: The initial state.
        """
        self.current_state = NewsletterState(
            month=0,
            subscribers=self.config.initial_subscribers,
            revenue=self.config.initial_revenue,
            costs=0.0,
            profit=0.0,
            cumulative_profit=0.0,
            revenue_per_subscriber=self.config.revenue_per_subscriber,
        )
        return self.current_state

    def run(self) -> list[NewsletterState]:
        """Run the simulation to completion.

        Returns:
            list[NewsletterState]: History of all states.
        """
        history = [self.reset()]
        while not self.current_state.is_terminated:
            history.append(self.step())
        return history

    def get_metrics(self) -> dict:
        """Get summary metrics from the current state.

        Returns:
            dict: Summary metrics including profit, subscribers, etc.
        """
        return {
            "month": self.current_state.month,
            "subscribers": self.current_state.subscribers,
            "revenue": self.current_state.revenue,
            "costs": self.current_state.costs,
            "profit": self.current_state.profit,
            "cumulative_profit": self.current_state.cumulative_profit,
            "is_terminated": self.current_state.is_terminated,
            "termination_reason": self.current_state.termination_reason,
        }
