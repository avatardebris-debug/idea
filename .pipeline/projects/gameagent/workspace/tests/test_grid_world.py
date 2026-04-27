"""Tests for GridWorld environment."""

import pytest

from gameagent.env.grid_world import GridWorld
from gameagent.env.types import Action, GridConfig


class TestGridWorld:
    """Tests for the GridWorld environment."""

    def test_initialization(self):
        """Test that GridWorld initializes correctly."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)

        assert env.config.width == 5
        assert env.config.height == 5
        assert env.config.goal_position == (4, 4)
        assert env.agent_position == (0, 0)
        assert env.step_count == 0

    def test_reset(self):
        """Test that reset returns initial state."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)

        obs, info = env.reset()

        assert obs.agent_position == (0, 0)
        assert obs.goal_position == (4, 4)
        assert env.agent_position == (0, 0)
        assert env.step_count == 0

    def test_move_up(self):
        """Test UP action."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)
        env.reset()

        result = env.step(Action.UP)
        assert result.observation.agent_position == (0, 1)
        assert result.reward == -0.1

    def test_move_down(self):
        """Test DOWN action."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)
        env.reset()

        result = env.step(Action.DOWN)
        assert result.observation.agent_position == (0, 0)  # Can't go below 0
        assert result.reward == -0.1

    def test_move_left(self):
        """Test LEFT action."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)
        env.reset()

        result = env.step(Action.LEFT)
        assert result.observation.agent_position == (0, 0)  # Can't go left of 0
        assert result.reward == -0.1

    def test_move_right(self):
        """Test RIGHT action."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)
        env.reset()

        result = env.step(Action.RIGHT)
        assert result.observation.agent_position == (1, 0)
        assert result.reward == -0.1

    def test_goal_reached(self):
        """Test reaching the goal."""
        config = GridConfig(width=5, height=5, goal_position=(1, 1), seed=42, obstacles=[])
        env = GridWorld(config)
        env.reset()

        # Move to goal
        env.step(Action.RIGHT)
        env.step(Action.UP)

        result = env.step(Action.INTERACT)
        assert result.reward == 10.0
        assert result.terminated is True

    def test_obstacle_collision(self):
        """Test obstacle collision."""
        config = GridConfig(
            width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[(1, 0)]
        )
        env = GridWorld(config)
        env.reset()

        result = env.step(Action.RIGHT)
        assert result.reward == -5.0
        assert result.terminated is False
        assert result.observation.agent_position == (0, 0)  # Position reverted

    def test_truncation(self):
        """Test episode truncation after max steps."""
        config = GridConfig(width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[])
        env = GridWorld(config)
        env.reset()

        # Run 100 steps
        for _ in range(100):
            result = env.step(Action.RIGHT)
            if result.terminated:
                break

        assert result.truncated is True

    def test_render(self):
        """Test grid rendering."""
        config = GridConfig(
            width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[(2, 2)]
        )
        env = GridWorld(config)
        env.reset()

        render_str = env.render()
        assert "A" in render_str  # Agent
        assert "G" in render_str  # Goal
        assert "X" in render_str  # Obstacle

    def test_invalid_goal_position(self):
        """Test that invalid goal position raises error."""
        config = GridConfig(width=5, height=5, goal_position=(10, 10), seed=42, obstacles=[])
        with pytest.raises(ValueError):
            GridWorld(config)

    def test_obstacle_overlaps_goal(self):
        """Test that obstacle overlapping goal raises error."""
        config = GridConfig(
            width=5, height=5, goal_position=(4, 4), seed=42, obstacles=[(4, 4)]
        )
        with pytest.raises(ValueError):
            GridWorld(config)
