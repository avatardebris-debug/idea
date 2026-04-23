"""Gymnasium-compatible RL environment for newsletter profit optimization."""

from __future__ import annotations

import gymnasium as gym
import numpy as np
from typing import Any, Optional

from profit_env.config import SimConfig
from profit_env.simulator import NewsletterSimulator
from profit_env.state import NewsletterState


class NewsletterEnv(gym.Env):
    """Gymnasium environment for newsletter profit optimization.

    This environment allows RL agents to learn strategies for optimizing
    newsletter business metrics like subscriber growth, revenue, and profit.

    Action Space:
        Discrete(5): Actions that modify growth_rate and churn_rate:
            0: No change (default)
            1: Increase marketing (increase growth, increase cost)
            2: Decrease marketing (decrease growth, decrease cost)
            3: Improve content (decrease churn, increase cost)
            4: Reduce content (increase churn, decrease cost)

    Observation Space:
        Box(8): [
            month_normalized,
            subscribers_normalized,
            revenue_normalized,
            profit_normalized,
            cumulative_profit_normalized,
            growth_rate,
            churn_rate,
            revenue_per_subscriber_normalized,
        ]
    """

    metadata = {"render_modes": ["human"], "render_fps": 1}

    def __init__(self, config: Optional[SimConfig] = None, render_mode: Optional[str] = None) -> None:
        """Initialize the environment.

        Args:
            config: Configuration for the simulation. Uses default config if None.
            render_mode: Render mode for visualization.
        """
        super().__init__()

        self.config = config or SimConfig()
        self.simulator = NewsletterSimulator(self.config)
        self.render_mode = render_mode

        # Action space: 5 discrete actions
        self.action_space = gym.spaces.Discrete(5)

        # Observation space: 8 continuous features
        self.observation_space = gym.spaces.Box(
            low=np.array([0.0, 0.0, 0.0, -1.0, -1.0, 0.0, 0.0, 0.0]),
            high=np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]),
            dtype=np.float32,
        )

        # Tracking
        self.current_obs: Optional[np.ndarray] = None
        self.max_subscribers: float = 1.0  # For normalization
        self.max_revenue: float = 1.0
        self.max_profit: float = 1.0

    def _normalize_observation(self, state: NewsletterState) -> np.ndarray:
        """Normalize observation features to [0, 1] range.

        Args:
            state: Current newsletter state.

        Returns:
            np.ndarray: Normalized observation vector.
        """
        month_norm = state.month / self.config.max_months
        subs_norm = state.subscribers / max(self.max_subscribers, 1)
        rev_norm = state.revenue / max(self.max_revenue, 1)
        profit_norm = state.profit / max(self.max_profit, 1)
        cum_profit_norm = state.cumulative_profit / max(abs(self.max_profit), 1)
        growth_norm = state.growth_rate
        churn_norm = state.churn_rate
        rps_norm = state.revenue_per_subscriber / 100.0  # Normalize by max expected RPS

        return np.array([
            month_norm,
            subs_norm,
            rev_norm,
            profit_norm,
            cum_profit_norm,
            growth_norm,
            churn_norm,
            rps_norm,
        ], dtype=np.float32)

    def _apply_action(self, action: int) -> None:
        """Apply an action to modify simulation parameters.

        Args:
            action: Action index from action space.
        """
        if action == 0:
            # No change
            pass
        elif action == 1:
            # Increase marketing: increase growth, increase cost
            self.config.growth_rate = min(1.0, self.config.growth_rate + 0.02)
            self.config.marketing_cost = min(5000.0, self.config.marketing_cost + 100.0)
        elif action == 2:
            # Decrease marketing: decrease growth, decrease cost
            self.config.growth_rate = max(0.0, self.config.growth_rate - 0.02)
            self.config.marketing_cost = max(0.0, self.config.marketing_cost - 100.0)
        elif action == 3:
            # Improve content: decrease churn, increase cost
            self.config.churn_rate = max(0.0, self.config.churn_rate - 0.01)
            self.config.content_cost = min(5000.0, self.config.content_cost + 100.0)
        elif action == 4:
            # Reduce content: increase churn, decrease cost
            self.config.churn_rate = min(1.0, self.config.churn_rate + 0.01)
            self.config.content_cost = max(0.0, self.config.content_cost - 100.0)

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict[str, Any]] = None,
    ) -> tuple[np.ndarray, dict]:
        """Reset the environment to initial state.

        Args:
            seed: Random seed for reproducibility.
            options: Additional options (unused).

        Returns:
            tuple: (observation, info)
        """
        super().reset(seed=seed)

        # Reset simulator
        self.simulator = NewsletterSimulator(self.config)
        self.simulator.reset()

        # Reset tracking
        self.max_subscribers = max(self.max_subscribers, self.config.initial_subscribers)
        self.max_revenue = max(self.max_revenue, self.config.initial_revenue)
        self.max_profit = max(self.max_profit, abs(self.config.initial_revenue))

        # Get initial observation
        self.current_obs = self._normalize_observation(self.simulator.current_state)

        info = {
            "month": self.simulator.current_state.month,
            "subscribers": self.simulator.current_state.subscribers,
            "revenue": self.simulator.current_state.revenue,
            "profit": self.simulator.current_state.profit,
            "cumulative_profit": self.simulator.current_state.cumulative_profit,
        }

        return self.current_obs, info

    def step(self, action: int) -> tuple[np.ndarray, float, bool, bool, dict]:
        """Take a step in the environment.

        Args:
            action: Action to take.

        Returns:
            tuple: (observation, reward, terminated, truncated, info)
        """
        # Apply action
        self._apply_action(action)

        # Advance simulation
        state = self.simulator.step()

        # Calculate reward
        reward = self._calculate_reward(state)

        # Update tracking
        self.max_subscribers = max(self.max_subscribers, state.subscribers)
        self.max_revenue = max(self.max_revenue, state.revenue)
        self.max_profit = max(self.max_profit, abs(state.profit))

        # Get new observation
        self.current_obs = self._normalize_observation(state)

        # Check termination
        terminated = state.is_terminated
        truncated = False  # We don't use truncation in this environment

        info = {
            "month": state.month,
            "subscribers": state.subscribers,
            "revenue": state.revenue,
            "costs": state.costs,
            "profit": state.profit,
            "cumulative_profit": state.cumulative_profit,
            "growth_rate": state.growth_rate,
            "churn_rate": state.churn_rate,
            "is_terminated": terminated,
            "termination_reason": state.termination_reason,
        }

        return self.current_obs, reward, terminated, truncated, info

    def _calculate_reward(self, state: NewsletterState) -> float:
        """Calculate reward based on current state.

        Args:
            state: Current newsletter state.

        Returns:
            float: Reward value.
        """
        # Primary reward: cumulative profit
        reward = state.cumulative_profit

        # Bonus for subscriber growth
        if state.new_subscribers > 0:
            reward += state.new_subscribers * 0.1

        # Penalty for high churn
        if state.churned_subscribers > 0:
            reward -= state.churned_subscribers * 0.05

        # Penalty for negative profit
        if state.profit < 0:
            reward -= abs(state.profit) * 0.1

        return reward

    def render(self) -> Optional[str]:
        """Render the environment state.

        Returns:
            Optional[str]: Rendered state as string.
        """
        if self.render_mode != "human":
            return None

        state = self.simulator.current_state
        render_str = (
            f"Month: {state.month:3d} | "
            f"Subscribers: {state.subscribers:6d} | "
            f"Revenue: ${state.revenue:10.2f} | "
            f"Profit: ${state.profit:10.2f} | "
            f"Cumulative: ${state.cumulative_profit:10.2f}"
        )

        if state.is_terminated:
            render_str += f"\nTerminated: {state.termination_reason}"

        return render_str

    def close(self) -> None:
        """Clean up the environment."""
        pass
