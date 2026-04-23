"""Base agent interface for the GridWorld environment."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from gameagent.env.types import Action, Observation


class BaseAgent(ABC):
    """Abstract base class for all agents.

    Subclasses must implement the `act` method which takes an observation
    and returns an action from the GridWorld action space.
    """

    def __init__(self, name: str = "BaseAgent"):
        self.name = name

    @abstractmethod
    def act(self, observation: Observation, **kwargs: Any) -> Action:
        """Choose an action given an observation.

        Args:
            observation: The current environment observation.
            **kwargs: Additional context (e.g., training mode, epsilon).

        Returns:
            Action: The chosen action from the action space.
        """
        pass

    def reset(self, **kwargs: Any) -> None:
        """Reset the agent's internal state. Called at the start of each episode."""
        pass

    def set_training_mode(self, training: bool) -> None:
        """Set the agent to training or evaluation mode.

        Default implementation does nothing. Subclasses that need
        mode-specific behavior (e.g., epsilon-greedy) should override.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class RandomAgent(BaseAgent):
    """A random agent that selects actions uniformly at random."""

    def __init__(self, num_actions: int = 5, name: str = "RandomAgent"):
        super().__init__(name=name)
        self.num_actions = num_actions

    def act(self, observation: Observation, **kwargs: Any) -> Action:
        """Choose a random action."""
        import random
        return Action(random.randint(0, self.num_actions - 1))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(num_actions={self.num_actions}, name={self.name!r})"


class GreedyAgent(BaseAgent):
    """A greedy agent that always moves toward the goal using Manhattan distance."""

    def __init__(self, name: str = "GreedyAgent"):
        super().__init__(name=name)

    def act(self, observation: Observation, **kwargs: Any) -> Action:
        """Move toward the goal using Manhattan distance heuristic."""
        agent_x, agent_y = observation.agent_position
        goal_x, goal_y = observation.goal_position

        dx = goal_x - agent_x
        dy = goal_y - agent_y

        # Prefer the axis with larger distance
        if abs(dx) >= abs(dy):
            if dx > 0:
                return Action.RIGHT
            elif dx < 0:
                return Action.LEFT
            else:
                # dx == 0, move vertically
                if dy > 0:
                    return Action.DOWN
                elif dy < 0:
                    return Action.UP
                else:
                    # At goal, interact
                    return Action.INTERACT
        else:
            if dy > 0:
                return Action.DOWN
            elif dy < 0:
                return Action.UP
            else:
                # dy == 0, move horizontally
                if dx > 0:
                    return Action.RIGHT
                elif dx < 0:
                    return Action.LEFT
                else:
                    return Action.INTERACT

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"
