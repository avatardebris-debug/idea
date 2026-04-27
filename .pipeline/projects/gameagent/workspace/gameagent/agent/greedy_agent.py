"""Greedy agent implementation."""

from gameagent.agent.base import BaseAgent
from gameagent.env.types import Action


class GreedyAgent(BaseAgent):
    """Greedy agent that always selects the best known action."""

    def __init__(self):
        """Initialize the greedy agent."""
        self._q_table: dict[tuple, dict[Action, float]] = {}

    def act(self, observation: Any) -> Action:
        """Select the best known action.

        Args:
            observation: The current observation.

        Returns:
            The action with the highest Q-value, or a random action if no Q-values exist.
        """
        state_key = (
            observation.agent_position,
            observation.goal_position,
            tuple(sorted(observation.info.get("obstacles", []))),
        )

        if state_key in self._q_table and self._q_table[state_key]:
            return max(self._q_table[state_key], key=self._q_table[state_key].get)
        else:
            return Action(random.randint(0, 4))

    def update(self, state_key: tuple, action: Action, q_value: float) -> None:
        """Update the Q-value for a state-action pair.

        Args:
            state_key: The state key.
            action: The action.
            q_value: The new Q-value.
        """
        if state_key not in self._q_table:
            self._q_table[state_key] = {}
        self._q_table[state_key][action] = q_value

    def reset(self) -> None:
        """Reset the agent's internal state."""
        self._q_table = {}
