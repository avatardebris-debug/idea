"""Q-Learning agent for the GridWorld environment."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Any, Optional

import numpy as np

from gameagent.agent.base import BaseAgent
from gameagent.env.types import Action, Observation


class QLearningAgent(BaseAgent):
    """Tabular Q-Learning agent.

    Uses a Q-table to learn the optimal policy for navigating the grid.
    State representation: (agent_position, goal_position, obstacles)
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
        name: str = "QLearningAgent",
    ):
        super().__init__(name=name)
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_table: dict[tuple, dict[Action, float]] = defaultdict(lambda: defaultdict(float))
        self._training_mode = True

    def _get_state_key(self, observation: Observation) -> tuple:
        """Create a hashable state key from the observation."""
        return (
            observation.agent_position,
            observation.goal_position,
            tuple(sorted(observation.info.get("obstacles", []))),
        )

    def act(self, observation: Observation, **kwargs: Any) -> Action:
        """Choose an action using epsilon-greedy policy."""
        state_key = self._get_state_key(observation)
        actions = self.q_table[state_key]

        # Epsilon-greedy action selection
        if self._training_mode and random.random() < self.epsilon:
            return Action(random.randint(0, 4))
        else:
            # Choose best action (fallback to random if no Q-values yet)
            if actions:
                best_action = max(actions, key=actions.get)
                return best_action
            else:
                return Action(random.randint(0, 4))

    def update(self, observation: Observation, action: Action, reward: float, next_observation: Observation, terminated: bool) -> None:
        """Update the Q-table with the new experience."""
        state_key = self._get_state_key(observation)
        next_state_key = self._get_state_key(next_observation)

        current_q = self.q_table[state_key][action]

        if terminated:
            target = reward
        else:
            next_actions = self.q_table[next_state_key]
            max_next_q = max(next_actions.values()) if next_actions else 0.0
            target = reward + self.discount_factor * max_next_q

        # Q-learning update rule
        self.q_table[state_key][action] += self.learning_rate * (target - current_q)

    def decay_epsilon(self) -> None:
        """Decay the exploration rate."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def set_training_mode(self, training: bool) -> None:
        """Set the agent to training or evaluation mode."""
        self._training_mode = training

    def reset(self, **kwargs: Any) -> None:
        """Reset the agent's internal state."""
        pass

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"lr={self.learning_rate}, "
            f"gamma={self.discount_factor}, "
            f"epsilon={self.epsilon:.3f}, "
            f"name={self.name!r})"
        )
