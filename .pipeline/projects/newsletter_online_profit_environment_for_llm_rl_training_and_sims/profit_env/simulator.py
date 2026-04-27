"""Newsletter Profit Simulator."""

from __future__ import annotations

from typing import List

from .config import SimConfig
from .state import NewsletterState


class NewsletterSimulator:
    """Simulates newsletter profit dynamics over time."""

    def __init__(self, config: SimConfig) -> None:
        """Initialize the simulator.

        Args:
            config: Simulation configuration.
        """
        self.config = config
        self.current_state = NewsletterState()
        self.history: List[NewsletterState] = []
        # Initialize with initial values
        self._initialize_state()

    def _initialize_state(self) -> None:
        """Initialize state with initial values."""
        self.current_state = NewsletterState(
            month=0,
            subscribers=self.config.initial_subscribers,
            revenue=self.config.initial_revenue,
            costs=self.config.content_cost + self.config.marketing_cost,
            profit=self.config.initial_revenue - (self.config.content_cost + self.config.marketing_cost),
            cumulative_profit=self.config.initial_revenue - (self.config.content_cost + self.config.marketing_cost),
        )
        self.history = [NewsletterState.from_dict(self.current_state.to_dict())]

    def reset(self) -> NewsletterState:
        """Reset the simulation to initial state.

        Returns:
            Initial state.
        """
        self._initialize_state()
        return self.current_state

    def step(self, action: int | None = None) -> NewsletterState:
        """Advance simulation by one month.

        Args:
            action: Optional action to modify parameters (for RL integration).

        Returns:
            Updated state.
        """
        # Apply action if provided (for RL integration)
        if action is not None:
            self._apply_action(action)

        # Advance month
        self.current_state.month += 1

        # Calculate subscriber dynamics
        new_subscribers = self.current_state.subscribers
        if new_subscribers > 0:
            # Growth from organic and marketing
            growth = new_subscribers * self.config.growth_rate
            # Churn
            churn = new_subscribers * self.config.churn_rate
            # Net change
            new_subscribers += int(growth - churn)
            new_subscribers = max(0, new_subscribers)

        # Calculate revenue and costs
        revenue = new_subscribers * self.config.revenue_per_subscriber
        costs = self.config.content_cost + self.config.marketing_cost
        profit = revenue - costs
        cumulative_profit = self.current_state.cumulative_profit + profit

        # Update state
        self.current_state.subscribers = new_subscribers
        self.current_state.revenue = revenue
        self.current_state.costs = costs
        self.current_state.profit = profit
        self.current_state.cumulative_profit = cumulative_profit

        # Check termination
        if new_subscribers == 0:
            self.current_state.is_terminated = True
            self.current_state.termination_reason = "No subscribers remaining"
        elif self.current_state.month >= self.config.max_months:
            self.current_state.is_terminated = True
            self.current_state.termination_reason = "Maximum months reached"

        # Record state
        self.history.append(NewsletterState.from_dict(self.current_state.to_dict()))

        return self.current_state

    def _apply_action(self, action: int) -> None:
        """Apply action to modify simulation parameters.

        Args:
            action: Action ID (0-4).
        """
        # For simulation mode, actions modify growth rate and marketing cost
        if action == 1:  # Increase marketing
            self.config.growth_rate = min(0.5, self.config.growth_rate + 0.02)
            self.config.marketing_cost = min(5000.0, self.config.marketing_cost + 100)
        elif action == 2:  # Decrease marketing
            self.config.growth_rate = max(0.0, self.config.growth_rate - 0.02)
            self.config.marketing_cost = max(0, self.config.marketing_cost - 100)
        elif action == 3:  # Increase content quality
            self.config.growth_rate = min(0.5, self.config.growth_rate + 0.01)
            self.config.content_cost = min(5000.0, self.config.content_cost + 50)
        elif action == 4:  # Decrease content quality
            self.config.growth_rate = max(0.0, self.config.growth_rate - 0.01)
            self.config.content_cost = max(0, self.config.content_cost - 50)

    def run(self) -> List[NewsletterState]:
        """Run simulation to completion.

        Returns:
            List of states from initial to final.
        """
        self.reset()

        while not self.current_state.is_terminated:
            self.step()

        return self.history

    def get_metrics(self) -> dict:
        """Get current metrics.

        Returns:
            Dictionary of current metrics.
        """
        return {
            "month": self.current_state.month,
            "subscribers": self.current_state.subscribers,
            "revenue": self.current_state.revenue,
            "costs": self.current_state.costs,
            "profit": self.current_state.profit,
            "cumulative_profit": self.current_state.cumulative_profit,
            "is_terminated": self.current_state.is_terminated,
        }
