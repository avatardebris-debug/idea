"""Tests for the ThrongletAgent class and related components.

Tests cover:
    - Agent initialization and state
    - Behavior decision logic
    - Movement and navigation
    - Eating and drinking
    - Interaction with other agents
    - Serialization/deserialization
    - Status reporting
"""

from __future__ import annotations

import random
from unittest.mock import MagicMock, patch

import pytest

from src.thronglets.agent import (
    AgentState,
    Behavior,
    ThrongletAgent,
)
from src.thronglets.models import Thronglet, ThrongletState, WorldConfig
from src.thronglets.types import (
    Direction,
    InteractionEvent,
    InteractionType,
    Position,
    TerrainType,
)
from src.thronglets.world import World


@pytest.fixture
def world_config():
    """Create a world configuration for testing."""
    return WorldConfig(width=10, height=10, wall_density=0.1)


@pytest.fixture
def world(world_config):
    """Create a world for testing."""
    return World(config=world_config)


@pytest.fixture
def thronglet():
    """Create a thronglet for testing."""
    return Thronglet(
        name="TestThronglet",
        position=Position(5, 5),
        state=ThrongletState(
            energy=50.0,
            hunger=50.0,
            mood=0,
            knowledge=[],
            last_action=None,
            last_prompt=None,
        ),
    )


@pytest.fixture
def agent(world, thronglet):
    """Create an agent for testing."""
    return ThrongletAgent(
        thronglet=thronglet,
        world=world,
        energy_decay_rate=1.0,
        hunger_rate=0.5,
    )


class TestAgentInitialization:
    """Tests for agent initialization."""

    def test_agent_creation(self, agent, thronglet, world):
        """Test that agent is created correctly."""
        assert agent.thronglet == thronglet
        assert agent.world == world
        assert agent.energy_decay_rate == 1.0
        assert agent.hunger_rate == 0.5
        assert agent.agent_state.current_behavior == Behavior.EXPLORE
        assert agent.agent_state.step_count == 0

    def test_agent_custom_rates(self, world, thronglet):
        """Test agent with custom rates."""
        agent = ThrongletAgent(
            thronglet=thronglet,
            world=world,
            energy_decay_rate=2.0,
            hunger_rate=1.0,
        )
        assert agent.energy_decay_rate == 2.0
        assert agent.hunger_rate == 1.0

    def test_agent_state_defaults(self, agent):
        """Test agent state defaults."""
        assert agent.agent_state.current_behavior == Behavior.EXPLORE
        assert agent.agent_state.target_position is None
        assert agent.agent_state.step_count == 0
        assert agent.agent_state.last_interaction is None
        assert agent.agent_state.preferences == {}


class TestStateUpdates:
    """Tests for agent state updates."""

    def test_energy_decay(self, agent):
        """Test energy decay over time."""
        initial_energy = agent.thronglet.state.energy
        agent.tick()
        assert agent.thronglet.state.energy == initial_energy - agent.energy_decay_rate

    def test_hunger_increase(self, agent):
        """Test hunger increase over time."""
        initial_hunger = agent.thronglet.state.hunger
        agent.tick()
        assert agent.thronglet.state.hunger == initial_hunger + agent.hunger_rate

    def test_energy_clamped_at_zero(self, agent):
        """Test energy doesn't go below zero."""
        agent.thronglet.state.energy = 0.5
        agent.tick()
        assert agent.thronglet.state.energy >= 0

    def test_hunger_clamped_at_100(self, agent):
        """Test hunger doesn't go above 100."""
        agent.thronglet.state.hunger = 99.8
        agent.tick()
        assert agent.thronglet.state.hunger <= 100

    def test_mood_decreases_when_hungry(self, agent):
        """Test mood decreases when hunger is high."""
        agent.thronglet.state.hunger = 85
        agent.tick()
        assert agent.thronglet.state.mood < 0

    def test_mood_decreases_when_low_energy(self, agent):
        """Test mood decreases when energy is low."""
        agent.thronglet.state.energy = 15
        agent.tick()
        assert agent.thronglet.state.mood < 0

    def test_mood_increases_when_happy(self, agent):
        """Test mood increases when conditions are good."""
        agent.thronglet.state.hunger = 10
        agent.thronglet.state.energy = 90
        agent.tick()
        assert agent.thronglet.state.mood > 0


class TestBehaviorDecision:
    """Tests for behavior decision logic."""

    def test_rest_when_energy_critical(self, agent):
        """Test agent chooses to rest when energy is critical."""
        agent.thronglet.state.energy = 5
        behavior = agent._decide_behavior()
        assert behavior == Behavior.REST

    def test_seek_food_when_hungry(self, agent):
        """Test agent chooses to seek food when hungry."""
        agent.thronglet.state.hunger = 85
        behavior = agent._decide_behavior()
        assert behavior == Behavior.SEEK_FOOD

    def test_seek_water_when_thirsty(self, agent, world):
        """Test agent chooses to seek water when thirsty."""
        # Add water nearby
        water_pos = Position(6, 6)
        world.set_terrain(water_pos, TerrainType.WATER)
        agent.thronglet.state.hunger = 60
        behavior = agent._decide_behavior()
        assert behavior == Behavior.SEEK_WATER

    def test_interact_when_nearby_thronglets(self, agent, world):
        """Test agent chooses to interact when nearby thronglets exist."""
        # Add another thronglet nearby
        other_thronglet = Thronglet(
            name="OtherThronglet",
            position=Position(6, 6),
            state=ThrongletState(),
        )
        world.add_thronglet("OtherThronglet", Position(6, 6))
        agent.thronglet.state.energy = 50
        agent.thronglet.state.hunger = 40

        # Mock random to ensure interaction is chosen
        with patch("thronglets.agent.random.random", return_value=0.3):
            behavior = agent._decide_behavior()
            assert behavior == Behavior.INTERACT

    def test_explore_by_default(self, agent):
        """Test agent explores by default."""
        agent.thronglet.state.energy = 50
        agent.thronglet.state.hunger = 40
        behavior = agent._decide_behavior()
        assert behavior == Behavior.EXPLORE


class TestMovement:
    """Tests for agent movement."""

    def test_move_to_valid_position(self, agent, world):
        """Test moving to a valid position."""
        target = Position(6, 6)
        agent._move_to(target)
        assert agent.thronglet.position == target
        assert agent.world.thronglets[agent.thronglet.name] == target

    def test_move_to_invalid_position(self, agent, world):
        """Test moving to an invalid position doesn't change position."""
        initial_pos = agent.thronglet.position
        # Create a wall at target
        target = Position(6, 6)
        world.set_terrain(target, TerrainType.WALL)
        agent._move_to(target)
        assert agent.thronglet.position == initial_pos

    def test_move_toward_target(self, agent, world):
        """Test moving toward a target."""
        target = Position(8, 8)
        agent._move_toward(target)
        # Position should be closer to target
        new_dist = agent.thronglet.position.distance_to(target)
        old_dist = Position(5, 5).distance_to(target)
        assert new_dist < old_dist

    def test_move_toward_blocked(self, agent, world):
        """Test moving toward a blocked target."""
        # Block direct path
        blocked_pos = Position(6, 5)
        world.set_terrain(blocked_pos, TerrainType.WALL)
        target = Position(8, 8)
        initial_pos = agent.thronglet.position
        agent._move_toward(target)
        # Should still move, just not directly
        assert agent.thronglet.position != initial_pos


class TestEatingAndDrinking:
    """Tests for eating and drinking behaviors."""

    def test_eat_food(self, agent, world):
        """Test eating food at current position."""
        # Place food at agent position
        world.set_terrain(agent.thronglet.position, TerrainType.FOOD)
        initial_energy = agent.thronglet.state.energy
        initial_hunger = agent.thronglet.state.hunger

        interactions = agent._eat()

        assert agent.thronglet.state.energy == initial_energy + 30
        assert agent.thronglet.state.hunger == initial_hunger - 50
        assert agent.thronglet.state.last_action == "eat"
        assert world.get_terrain(agent.thronglet.position) == TerrainType.EMPTY

    def test_drink_water(self, agent, world):
        """Test drinking water at current position."""
        # Place water at agent position
        world.set_terrain(agent.thronglet.position, TerrainType.WATER)
        initial_energy = agent.thronglet.state.energy
        initial_hunger = agent.thronglet.state.hunger

        interactions = agent._drink()

        assert agent.thronglet.state.hunger == initial_hunger - 30
        assert agent.thronglet.state.energy == initial_energy + 10
        assert agent.thronglet.state.last_action == "drink"


class TestInteraction:
    """Tests for agent interaction."""

    def test_interact_with_nearby_thronglet(self, agent, world):
        """Test interacting with a nearby thronglet."""
        # Add another thronglet nearby
        other_thronglet = Thronglet(
            name="OtherThronglet",
            position=Position(6, 6),
            state=ThrongletState(),
        )
        world.add_thronglet("OtherThronglet", Position(6, 6))

        interactions = agent._interact()

        assert len(interactions) == 1
        assert isinstance(interactions[0], InteractionEvent)
        assert interactions[0].sender == agent.thronglet.name
        assert interactions[0].receiver == "OtherThronglet"
        assert interactions[0].interaction_type in [
            InteractionType.MESSAGE,
            InteractionType.GREET,
            InteractionType.COOPERATE,
        ]

    def test_no_interaction_when_no_nearby(self, agent):
        """Test no interaction when no nearby thronglets."""
        interactions = agent._interact()
        assert len(interactions) == 0

    def test_interact_records_event(self, agent, world):
        """Test that interaction records the event."""
        # Add another thronglet nearby
        world.add_thronglet("OtherThronglet", Position(6, 6))

        agent._interact()

        assert agent.agent_state.last_interaction is not None
        assert agent.agent_state.last_interaction.sender == agent.thronglet.name


class TestTick:
    """Tests for the main tick method."""

    def test_tick_updates_state(self, agent):
        """Test that tick updates agent state."""
        initial_energy = agent.thronglet.state.energy
        initial_hunger = agent.thronglet.state.hunger

        agent.tick()

        assert agent.thronglet.state.energy == initial_energy - agent.energy_decay_rate
        assert agent.thronglet.state.hunger == initial_hunger + agent.hunger_rate
        assert agent.agent_state.step_count == 1

    def test_tick_returns_interactions(self, agent, world):
        """Test that tick returns interaction events."""
        # Add another thronglet nearby to trigger interaction
        world.add_thronglet("OtherThronglet", Position(6, 6))

        interactions = agent.tick()

        assert isinstance(interactions, list)
        # Interactions may or may not be returned depending on behavior
        # but the method should always return a list

    def test_tick_multiple_times(self, agent):
        """Test multiple ticks."""
        for _ in range(5):
            agent.tick()

        assert agent.agent_state.step_count == 5
        assert agent.thronglet.state.energy >= 0
        assert agent.thronglet.state.hunger <= 100


class TestSerialization:
    """Tests for agent serialization."""

    def test_to_dict(self, agent):
        """Test agent serialization to dict."""
        data = agent.to_dict()

        assert "thronglet" in data
        assert "agent_state" in data
        assert data["agent_state"]["current_behavior"] == Behavior.EXPLORE
        assert data["agent_state"]["step_count"] == 0
        assert data["agent_state"]["energy_decay_rate"] == 1.0
        assert data["agent_state"]["hunger_rate"] == 0.5

    def test_from_dict(self, world, thronglet):
        """Test agent deserialization from dict."""
        agent = ThrongletAgent(
            thronglet=thronglet,
            world=world,
            energy_decay_rate=2.0,
            hunger_rate=1.0,
        )
        agent.agent_state.current_behavior = Behavior.REST
        agent.agent_state.step_count = 10

        data = agent.to_dict()
        restored_agent = ThrongletAgent.from_dict(data, world)

        assert restored_agent.thronglet.name == agent.thronglet.name
        assert restored_agent.energy_decay_rate == 2.0
        assert restored_agent.hunger_rate == 1.0
        assert restored_agent.agent_state.current_behavior == Behavior.REST
        assert restored_agent.agent_state.step_count == 10


class TestStatus:
    """Tests for agent status reporting."""

    def test_get_status(self, agent):
        """Test getting agent status."""
        status = agent.get_status()

        assert status["name"] == agent.thronglet.name
        assert status["position"] == agent.thronglet.position.to_dict()
        assert "energy" in status
        assert "hunger" in status
        assert "mood" in status
        assert "behavior" in status
        assert "step_count" in status

    def test_status_reflects_current_state(self, agent):
        """Test that status reflects current state."""
        agent.thronglet.state.energy = 75
        agent.thronglet.state.hunger = 25
        agent.thronglet.state.mood = 5
        agent.agent_state.current_behavior = Behavior.REST
        agent.agent_state.step_count = 42

        status = agent.get_status()

        assert status["energy"] == 75
        assert status["hunger"] == 25
        assert status["mood"] == 5
        assert status["behavior"] == Behavior.REST
        assert status["step_count"] == 42


class TestAgentState:
    """Tests for AgentState dataclass."""

    def test_agent_state_defaults(self):
        """Test AgentState defaults."""
        state = AgentState()
        assert state.current_behavior == Behavior.EXPLORE
        assert state.target_position is None
        assert state.step_count == 0
        assert state.last_interaction is None
        assert state.preferences == {}

    def test_agent_state_custom(self):
        """Test AgentState with custom values."""
        target = Position(5, 5)
        state = AgentState(
            current_behavior=Behavior.REST,
            target_position=target,
            step_count=10,
        )
        assert state.current_behavior == Behavior.REST
        assert state.target_position == target
        assert state.step_count == 10
