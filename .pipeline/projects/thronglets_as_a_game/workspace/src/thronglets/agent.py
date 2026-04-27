"""Agent implementation for Thronglet simulation.

This module provides the ThrongletAgent class that controls individual thronglets
in the simulation, handling behavior decisions, movement, and interactions.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.thronglets.models import Thronglet
from src.thronglets.types import (
    Behavior,
    Direction,
    InteractionEvent,
    InteractionType,
    Position,
    TerrainType,
)
from src.thronglets.world import World


@dataclass
class AgentState:
    """State tracking for an agent.

    Attributes:
        current_behavior: The agent's current behavior.
        target_position: The current target position.
        step_count: Number of steps taken.
        last_interaction: Last interaction event.
        preferences: Agent preferences.
    """

    current_behavior: Behavior = Behavior.EXPLORE
    target_position: Position | None = None
    step_count: int = 0
    last_interaction: InteractionEvent | None = None
    preferences: dict = field(default_factory=dict)


class ThrongletAgent:
    """Agent that controls a thronglet in the simulation.

    Attributes:
        thronglet: The thronglet being controlled.
        world: The world the agent operates in.
        energy_decay_rate: Rate at which energy decays.
        hunger_rate: Rate at which hunger increases.
        agent_state: Current state of the agent.
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
            thronglet: The thronglet to control.
            world: The world the agent operates in.
            energy_decay_rate: Rate at which energy decays.
            hunger_rate: Rate at which hunger increases.
        """
        self.thronglet = thronglet
        self.world = world
        self.energy_decay_rate = energy_decay_rate
        self.hunger_rate = hunger_rate
        self.agent_state = AgentState()

    def tick(self) -> list[InteractionEvent]:
        """Process one time step.

        Returns:
            List of interaction events generated.
        """
        # Decide behavior
        behavior = self._decide_behavior()
        self.agent_state.current_behavior = behavior

        # Execute behavior
        interactions: list[InteractionEvent] = []
        if behavior == Behavior.REST:
            interactions = self._rest()
        elif behavior == Behavior.EXPLORE:
            interactions = self._explore()
        elif behavior == Behavior.SEEK_FOOD:
            interactions = self._seek_food()
        elif behavior == Behavior.SEEK_WATER:
            interactions = self._seek_water()
        elif behavior == Behavior.INTERACT:
            interactions = self._interact()

        # Update state
        self._update_state()
        self.agent_state.step_count += 1

        return interactions

    def _decide_behavior(self) -> Behavior:
        """Decide the next behavior based on state and environment.

        Returns:
            The chosen behavior.
        """
        # Check for critical conditions first
        if self.thronglet.state.energy < 10:
            return Behavior.REST

        if self.thronglet.state.hunger > 80:
            return Behavior.SEEK_FOOD

        # Check for water nearby
        if self._has_water_nearby():
            return Behavior.SEEK_WATER

        # Check for nearby thronglets
        nearby = self._find_nearby_thronglets(radius=2)
        if nearby:
            # 30% chance to interact
            if random.random() < 0.3:
                return Behavior.INTERACT

        # Default to exploration
        return Behavior.EXPLORE

    def _rest(self) -> list[InteractionEvent]:
        """Rest and recover energy.

        Returns:
            Empty list (no interactions).
        """
        # Stay in place
        return []

    def _explore(self) -> list[InteractionEvent]:
        """Explore the environment.

        Returns:
            Empty list (no interactions).
        """
        # Move in a random direction
        current = self.thronglet.position
        directions = [
            Direction.NORTH,
            Direction.SOUTH,
            Direction.EAST,
            Direction.WEST,
        ]
        random.shuffle(directions)

        for direction in directions:
            next_pos = current.offset(*direction.delta())
            if self.world.is_valid_move(next_pos):
                self._move_to(next_pos)
                return []

        # If all directions blocked, stay in place
        return []

    def _seek_food(self) -> list[InteractionEvent]:
        """Seek food in the environment.

        Returns:
            List of interaction events.
        """
        # Find nearby food
        food_positions = self._find_nearby_terrain(TerrainType.FOOD, radius=5)

        if food_positions:
            target = food_positions[0]
            self._move_toward(target)
            return []

        # If no food nearby, explore
        return self._explore()

    def _seek_water(self) -> list[InteractionEvent]:
        """Seek water in the environment.

        Returns:
            List of interaction events.
        """
        # Find nearby water
        water_positions = self._find_nearby_terrain(TerrainType.WATER, radius=5)

        if water_positions:
            target = water_positions[0]
            self._move_toward(target)
            return []

        # If no water nearby, explore
        return self._explore()

    def _interact(self) -> list[InteractionEvent]:
        """Interact with nearby thronglets.

        Returns:
            List of interaction events.
        """
        nearby = self._find_nearby_thronglets(radius=2)

        if not nearby:
            return []

        # Pick a random nearby thronglet to interact with
        target = random.choice(nearby)
        event = InteractionEvent(
            sender=self.thronglet.name,
            receiver=target.name,
            interaction_type=InteractionType.GREETING,
            timestamp=self.agent_state.step_count,
        )
        self.agent_state.last_interaction = event
        return [event]

    def _move_to(self, target: Position) -> None:
        """Move to a target position.

        Args:
            target: The target position.
        """
        # Check if position is valid
        if not self.world.is_valid_move(target):
            return

        # Update thronglet state
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

    def _find_nearby_thronglets(self, radius: int) -> list[Thronglet]:
        """Find all thronglets within radius.

        Args:
            radius: The search radius.

        Returns:
            List of nearby thronglets.
        """
        nearby = []
        for name, pos in self.world.thronglets.items():
            if name != self.thronglet.name:
                dist = self.thronglet.position.distance_to(pos)
                if dist <= radius:
                    # Get the thronglet object from world
                    nearby_thronglet = self.world.get_thronglet(name)
                    if nearby_thronglet:
                        nearby.append(nearby_thronglet)
        return nearby

    def _has_water_nearby(self) -> bool:
        """Check if there is water nearby.

        Returns:
            True if water is within radius 5.
        """
        return len(self._find_nearby_terrain(TerrainType.WATER, radius=5)) > 0

    def _update_state(self) -> None:
        """Update agent state based on current conditions."""
        # Decay energy
        self.thronglet.state.energy = max(
            0, self.thronglet.state.energy - self.energy_decay_rate
        )

        # Increase hunger
        self.thronglet.state.hunger = min(
            100, self.thronglet.state.hunger + self.hunger_rate
        )

        # Adjust mood based on state
        if self.thronglet.state.hunger > 70 or self.thronglet.state.energy < 20:
            self.thronglet.state.mood = max(-10, self.thronglet.state.mood - 1)
        elif self.thronglet.state.hunger < 30 and self.thronglet.state.energy > 80:
            self.thronglet.state.mood = min(10, self.thronglet.state.mood + 1)

    def _eat(self) -> list[InteractionEvent]:
        """Eat food at current position.

        Returns:
            List of interaction events.
        """
        terrain = self.world.get_terrain(self.thronglet.position)
        if terrain == TerrainType.FOOD:
            self.thronglet.state.energy = min(100, self.thronglet.state.energy + 20)
            self.thronglet.state.hunger = max(0, self.thronglet.state.hunger - 20)
            self.world.set_terrain(self.thronglet.position, TerrainType.EMPTY)
            return []
        return []

    def _drink(self) -> list[InteractionEvent]:
        """Drink water at current position.

        Returns:
            List of interaction events.
        """
        terrain = self.world.get_terrain(self.thronglet.position)
        if terrain == TerrainType.WATER:
            self.thronglet.state.hunger = max(0, self.thronglet.state.hunger - 20)
            self.thronglet.state.energy = min(100, self.thronglet.state.energy + 10)
            self.world.set_terrain(self.thronglet.position, TerrainType.EMPTY)
            return []
        return []

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
