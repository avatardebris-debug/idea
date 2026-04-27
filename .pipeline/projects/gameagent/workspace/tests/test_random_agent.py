"""Tests for RandomAgent."""

import pytest

from gameagent.agent.base import RandomAgent
from gameagent.env.types import Action


class TestRandomAgent:
    """Tests for the RandomAgent class."""

    def test_init(self):
        """Test RandomAgent initialization."""
        agent = RandomAgent()
        assert agent is not None

    def test_act_returns_valid_action(self):
        """Test that act returns a valid action."""
        agent = RandomAgent()
        action = agent.act(None)
        assert action in Action

    def test_act_returns_different_actions(self):
        """Test that act can return different actions."""
        agent = RandomAgent()
        actions = [agent.act(None) for _ in range(100)]
        # With 5 actions, we should see variety
        unique_actions = set(actions)
        assert len(unique_actions) > 1

    def test_act_is_deterministic_with_seed(self):
        """Test that act is deterministic with same seed."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=42)

        actions1 = [agent1.act(None) for _ in range(10)]
        actions2 = [agent2.act(None) for _ in range(10)]

        assert actions1 == actions2

    def test_act_with_different_seeds(self):
        """Test that different seeds produce different sequences."""
        agent1 = RandomAgent(seed=42)
        agent2 = RandomAgent(seed=123)

        actions1 = [agent1.act(None) for _ in range(10)]
        actions2 = [agent2.act(None) for _ in range(10)]

        assert actions1 != actions2
