"""Thronglet agent core for the simulation.

Provides:
    - ThrongletAgent: The main agent class with behavior logic
    - Behavior: Enum of possible agent behaviors
    - AgentState: Extended state tracking for agents
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from .models import Thronglet, ThrongletState
from .types import (
    ActionType,
    Direction,
    InteractionEvent,
    InteractionType,
    Position,
    TerrainType,
)
from .world import World


class Behavior:
    """Enum-like class for agent behaviors."""

    EXPLORE = "explore"
    SEEK_FOOD = "seek_food"
    SEEK_WATER = "seek_water"
    REST = "rest"
    INTERACT = "interact"
    IDLE = "idle"


@dataclass
class AgentState:
    """Extended state tracking for an agent.

    Attributes:
        current_behavior: The agent's current behavior mode.
        target_position: Optional target position for navigation.
        step_count: Number of steps taken.
        last_interaction: Last interaction event.
        preferences: Agent-specific preferences.
    """

    current_behavior: str = Behavior.EXPLORE
    target_position: Optional[Position] = None
    step_count: int = 0
    last_interaction: Optional[InteractionEvent] = None
    preferences: dict = field(default_factory=dict)


class ThrongletAgent:
    """A thronglet agent with behavior logic.

    Attributes:
        thronglet: The underlying thronglet model.
        world: Reference to the world.
        agent_state: Extended agent state.
        energy_decay_rate: Rate of energy loss per tick.
        hunger_rate: Rate of hunger increase per tick.
    """

    def __init__(
        self,
        thronglet: Thronglet,
        world: World,
        energy_decay_rate: float = 1.0,
        hunger_rate: float = 0.5,
    ) -> None:
        """Initialize the agent.

        Args:
            thronglet: The thronglet model.
            world: The world the agent inhabits.
            energy_decay_rate: Rate of energy loss per tick.
            hunger_rate: Rate of hunger increase per tick.
        """
        self.thronglet = thronglet
        self.world = world
        self.agent_state = AgentState()
        self.energy_decay_rate = energy_decay_rate
        self.hunger_rate = hunger_rate

    def tick(self) -> list[InteractionEvent]:
        """Process one tick of the agent's behavior.

        Returns:
            List of interaction events generated this tick.
        """
        interactions: list[InteractionEvent] = []

        # Update state
        self._update_state()

        # Decide and execute behavior
        behavior = self._decide_behavior()
        interactions.extend(self._execute_behavior(behavior))

        self.agent_state.step_count += 1
        return interactions

    def _update_state(self) -> None:
        """Update the agent's internal state."""
        state = self.thronglet.state
        state.energy = max(0, state.energy - self.energy_decay_rate)
        state.hunger = min(100, state.hunger + self.hunger_rate)

        # Mood adjustments
        if state.hunger > 80:
            state.mood = max(-10, state.mood - 1)
        elif state.energy < 20:
            state.mood = max(-10, state.mood - 1)
        elif state.hunger < 20 and state.energy > 80:
            state.mood = min(10, state.mood + 1)

    def _decide_behavior(self) -> str:
        """Decide the next behavior based on current state.

        Returns:
            The chosen behavior string.
        """
        state = self.thronglet.state

        # Priority: critical needs first
        if state.energy < 10:
            return Behavior.REST
        if state.hunger > 80:
            return Behavior.SEEK_FOOD
        if state.hunger > 50 and self._has_water_nearby():
            return Behavior.SEEK_WATER

        # Check for nearby thronglets to interact
        nearby = self.world.get_thronglets_in_range(
            self.thronglet.position, radius=3
        )
        if len(nearby) > 0 and random.random() < 0.3:
            return Behavior.INTERACT

        # Default: explore
        return Behavior.EXPLORE

    def _has_water_nearby(self) -> bool:
        """Check if there's water within range."""
        neighbors = self.world.get_neighbors(
            self.thronglet.position, radius=5
        )
        for pos in neighbors:
            if self.world.get_terrain(pos) == TerrainType.WATER:
                return True
        return False

    def _execute_behavior(self, behavior: str) -> list[InteractionEvent]:
        """Execute the chosen behavior.

        Args:
            behavior: The behavior to execute.

        Returns:
            List of interaction events generated.
        """
        interactions: list[InteractionEvent] = []

        if behavior == Behavior.EXPLORE:
            interactions.extend(self._explore())
        elif behavior == Behavior.SEEK_FOOD:
            interactions.extend(self._seek_food())
        elif behavior == Behavior.SEEK_WATER:
            interactions.extend(self._seek_water())
        elif behavior == Behavior.REST:
            interactions.extend(self._rest())
        elif behavior == Behavior.INTERACT:
            interactions.extend(self._interact())
        else:
            interactions.extend(self._idle())

        return interactions

    def _explore(self) -> list[InteractionEvent]:
        """Explore the environment.

        Returns:
            List of interaction events.
        """
        neighbors = self.world.get_neighbors(
            self.thronglet.position, radius=1
        )
        valid_moves = [
            pos for pos in neighbors if self.world.is_valid_move(pos)
        ]

        if not valid_moves:
            return self._idle()

        # Prefer moving toward empty space, avoid walls
        target = random.choice(valid_moves)
        self._move_to(target)

        # Record observation
        terrain = self.world.get_terrain(self.thronglet.position)
        self.thronglet.state.knowledge.append(
            f"observed {terrain.value} at {self.thronglet.position}"
        )

        return []

    def _seek_food(self) -> list[InteractionEvent]:
        """Seek food in the environment.

        Returns:
            List of interaction events.
        """
        # Check current position for food
        current_terrain = self.world.get_terrain(self.thronglet.position)
        if current_terrain == TerrainType.FOOD:
            return self._eat()

        # Find nearest food
        food_positions = self._find_nearby_terrain(TerrainType.FOOD, radius=10)
        if food_positions:
            target = min(
                food_positions,
                key=lambda pos: pos.distance_to(self.thronglet.position),
            )
            self._move_toward(target)
        else:
            return self._explore()

        return []

    def _seek_water(self) -> list[InteractionEvent]:
        """Seek water in the environment.

        Returns:
            List of interaction events.
        """
        # Check current position for water
        current_terrain = self.world.get_terrain(self.thronglet.position)
        if current_terrain == TerrainType.WATER:
            return self._drink()

        # Find nearest water
        water_positions = self._find_nearby_terrain(
            TerrainType.WATER, radius=10
        )
        if water_positions:
            target = min(
                water_positions,
                key=lambda pos: pos.distance_to(self.thronglet.position),
            )
            self._move_toward(target)
        else:
            return self._explore()

        return []

    def _rest(self) -> list[InteractionEvent]:
        """Rest to recover energy.

        Returns:
            List of interaction events.
        """
        self.thronglet.state.energy = min(
            100, self.thronglet.state.energy + 10
        )
        self.thronglet.state.last_action = "rest"
        return []

    def _interact(self) -> list[InteractionEvent]:
        """Interact with nearby thronglets.

        Returns:
            List of interaction events.
        """
        nearby = self.world.get_thronglets_in_range(
            self.thronglet.position, radius=3
        )
        if not nearby:
            return self._idle()

        # Pick a random thronglet to interact with
        target_name = random.choice(nearby)
        if target_name == self.thronglet.name:
            return self._idle()

        # Create interaction event
        interaction_type = random.choice(
            [
                InteractionType.MESSAGE,
                InteractionType.GREET,
                InteractionType.COOPERATE,
            ]
        )
        messages = {
            InteractionType.MESSAGE: "Hello! How are you?",
            InteractionType.GREET: "Greetings, friend!",
            InteractionType.COOPERATE: "Shall we explore together?",
        }

        event = InteractionEvent(
            interaction_type=interaction_type,
            sender=self.thronglet.name,
            receiver=target_name,
            message=messages[interaction_type],
            position=self.thronglet.position,
        )

        self.thronglet.state.last_action = f"interact with {target_name}"
        self.thronglet.state.last_prompt = event.message
        self.agent_state.last_interaction = event

        return [event]

    def _idle(self) -> list[InteractionEvent]:
        """Do nothing this tick.

        Returns:
            Empty list of interaction events.
        """
        self.thronglet.state.last_action = "idle"
        return []

    def _eat(self) -> list[InteractionEvent]:
        """Eat food at current position.

        Returns:
            List of interaction events.
        """
        self.thronglet.state.energy = min(
            100, self.thronglet.state.energy + 30
        )
        self.thronglet.state.hunger = max(0, self.thronglet.state.hunger - 50)
        self.thronglet.state.last_action = "eat"

        # Remove food from world
        self.world.set_terrain(
            self.thronglet.position, TerrainType.EMPTY
        )

        return []

    def _drink(self) -> list[InteractionEvent]:
        """Drink water at current position.

        Returns:
            List of interaction events.
        """
        self.thronglet.state.hunger = max(0, self.thronglet.state.hunger - 30)
        self.thronglet.state.energy = min(
            100, self.thronglet.state.energy + 10
        )
        self.thronglet.state.last_action = "drink"

        return []

    def _move_to(self, target: Position) -> None:
        """Move the agent to a specific position.

        Args:
            target: The target position.
        """
        if not self.world.is_valid_move(target):
            return

        # Remove from old position
        del self.world.thronglets[self.thronglet.name]

        # Update position
        self.thronglet.position = target
        self.thronglet.state.last_action = f"move to {target}"

        # Add to new position
        self.world.thronglets[self.thronglet.name] = target

    def _move_toward(self, target: Position) -> None:
        """Move one step toward the target.

        Args:
            target: The target position.
        """
        current = self.thronglet.position
        dx = target.x - current.x
        dy = target.y - current.y

        # Determine direction
        if abs(dx) > abs(dy):
            direction = Direction.EAST if dx > 0 else Direction.WEST
        else:
            direction = Direction.SOUTH if dy > 0 else Direction.NORTH

        # Calculate next position
        next_pos = current.offset(*direction.delta())

        # Try to move, if blocked try perpendicular
        if not self.world.is_valid_move(next_pos):
            if direction == Direction.EAST or direction == Direction.WEST:
                direction = Direction.SOUTH if dy > 0 else Direction.NORTH
            else:
                direction = Direction.EAST if dx > 0 else Direction.WEST
            next_pos = current.offset(*direction.delta())

        self._move_to(next_pos)

    def _find_nearby_terrain(
        self, terrain_type: TerrainType, radius: int
    ) -> list[Position]:
        """Find all positions of a specific terrain type within radius.

        Args:
            terrain_type: The terrain type to find.
            radius: The search radius.

        Returns:
            List of positions with the specified terrain.
        """
        positions = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                pos = self.thronglet.position.offset(dx, dy)
                if self.world._is_in_bounds(pos):
                    if self.world.get_terrain(pos) == terrain_type:
                        positions.append(pos)
        return positions

    def get_status(self) -> dict:
        """Get the current status of the agent.

        Returns:
            Dictionary with agent status information.
        """
        return {
            "name": self.thronglet.name,
            "position": self.thronglet.position.to_dict(),
            "energy": self.thronglet.state.energy,
            "hunger": self.thronglet.state.hunger,
            "mood": self.thronglet.state.mood,
            "behavior": self.agent_state.current_behavior,
            "step_count": self.agent_state.step_count,
        }

    def to_dict(self) -> dict:
        """Serialize the agent to a dictionary.

        Returns:
            Dictionary representation of the agent.
        """
        return {
            "thronglet": self.thronglet.to_dict(),
            "agent_state": {
                "current_behavior": self.agent_state.current_behavior,
                "target_position": (
                    self.agent_state.target_position.to_dict()
                    if self.agent_state.target_position
                    else None
                ),
                "step_count": self.agent_state.step_count,
                "energy_decay_rate": self.energy_decay_rate,
                "hunger_rate": self.hunger_rate,
            },
        }

    @classmethod
    def from_dict(cls, data: dict, world: World) -> ThrongletAgent:
        """Deserialize an agent from a dictionary.

        Args:
            data: Dictionary representation of the agent.
            world: The world to associate with the agent.

        Returns:
            ThrongletAgent instance.
        """
        thronglet = Thronglet.from_dict(data["thronglet"])
        agent_state_data = data["agent_state"]
        agent_state = AgentState(
            current_behavior=agent_state_data["current_behavior"],
            target_position=(
                Position(**agent_state_data["target_position"])
                if agent_state_data["target_position"]
                else None
            ),
            step_count=agent_state_data["step_count"],
        )

        agent = cls(
            thronglet=thronglet,
            world=world,
            energy_decay_rate=agent_state_data.get(
                "energy_decay_rate", 1.0
            ),
            hunger_rate=agent_state_data.get("hunger_rate", 0.5),
        )
        agent.agent_state = agent_state
        return agent
