"""Core data models for the thronglets system.

Provides:
    - ThrongletState: Internal state of a thronglet agent
    - Thronglet: The main agent data model
    - WorldConfig: Configuration for the simulation world
    - SimulationConfig: Top-level simulation configuration
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from .types import Position, TerrainType


@dataclass
class ThrongletState:
    """Internal state of a thronglet agent.

    Attributes:
        energy: Current energy level (0-100).
        hunger: Hunger level (0-100, 0 = not hungry).
        mood: Current mood (-10 to 10).
        knowledge: Set of known facts/locations.
        inventory: Items carried by the thronglet.
        last_action: The last action taken.
        last_prompt: The last prompt received.
    """

    energy: int = 100
    hunger: int = 0
    mood: int = 0
    knowledge: list[str] = field(default_factory=list)
    inventory: list[str] = field(default_factory=list)
    last_action: Optional[str] = None
    last_prompt: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "energy": self.energy,
            "hunger": self.hunger,
            "mood": self.mood,
            "knowledge": self.knowledge,
            "inventory": self.inventory,
            "last_action": self.last_action,
            "last_prompt": self.last_prompt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ThrongletState:
        """Deserialize from a dictionary."""
        return cls(
            energy=data.get("energy", 100),
            hunger=data.get("hunger", 0),
            mood=data.get("mood", 0),
            knowledge=data.get("knowledge", []),
            inventory=data.get("inventory", []),
            last_action=data.get("last_action"),
            last_prompt=data.get("last_prompt"),
        )


@dataclass
class Thronglet:
    """A thronglet agent in the simulation.

    Attributes:
        name: Unique name of the thronglet.
        position: Current grid position.
        state: Internal agent state.
        color: Display color code (ANSI).
        symbol: Display character on the grid.
    """

    name: str
    position: Position
    state: ThrongletState = field(default_factory=ThrongletState)
    color: str = "\033[94m"  # Blue
    symbol: str = "T"

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "name": self.name,
            "position": {"x": self.position.x, "y": self.position.y},
            "state": self.state.to_dict(),
            "color": self.color,
            "symbol": self.symbol,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Thronglet:
        """Deserialize from a dictionary."""
        pos_data = data["position"]
        state_data = data.get("state", {})
        return cls(
            name=data["name"],
            position=Position(x=pos_data["x"], y=pos_data["y"]),
            state=ThrongletState.from_dict(state_data),
            color=data.get("color", "\033[94m"),
            symbol=data.get("symbol", "T"),
        )


@dataclass
class WorldConfig:
    """Configuration for the simulation world.

    Attributes:
        width: Number of columns in the grid.
        height: Number of rows in the grid.
        default_terrain: Default terrain type for empty cells.
        wall_density: Probability of a wall cell (0.0-1.0).
        food_density: Probability of a food cell (0.0-1.0).
        water_density: Probability of a water cell (0.0-1.0).
    """

    width: int = 20
    height: int = 20
    default_terrain: TerrainType = TerrainType.EMPTY
    wall_density: float = 0.1
    food_density: float = 0.05
    water_density: float = 0.05

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "width": self.width,
            "height": self.height,
            "default_terrain": self.default_terrain.value,
            "wall_density": self.wall_density,
            "food_density": self.food_density,
            "water_density": self.water_density,
        }

    @classmethod
    def from_dict(cls, data: dict) -> WorldConfig:
        """Deserialize from a dictionary."""
        return cls(
            width=data.get("width", 20),
            height=data.get("height", 20),
            default_terrain=TerrainType(data.get("default_terrain", "empty")),
            wall_density=data.get("wall_density", 0.1),
            food_density=data.get("food_density", 0.05),
            water_density=data.get("water_density", 0.05),
        )


@dataclass
class SimulationConfig:
    """Top-level simulation configuration.

    Attributes:
        world: World configuration.
        thronglets: List of thronglet configurations.
        max_ticks: Maximum number of simulation ticks.
        render_interval: Render every N ticks (0 = every tick).
        interaction_range: Default interaction range between thronglets.
    """

    world: WorldConfig = field(default_factory=WorldConfig)
    thronglets: list[dict] = field(default_factory=list)
    max_ticks: int = 100
    render_interval: int = 1
    interaction_range: int = 3

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "world": self.world.to_dict(),
            "thronglets": self.thronglets,
            "max_ticks": self.max_ticks,
            "render_interval": self.render_interval,
            "interaction_range": self.interaction_range,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SimulationConfig:
        """Deserialize from a dictionary."""
        return cls(
            world=WorldConfig.from_dict(data.get("world", {})),
            thronglets=data.get("thronglets", []),
            max_ticks=data.get("max_ticks", 100),
            render_interval=data.get("render_interval", 1),
            interaction_range=data.get("interaction_range", 3),
        )

    @classmethod
    def from_json(cls, json_str: str) -> SimulationConfig:
        """Deserialize from a JSON string."""
        return cls.from_dict(json.loads(json_str))

    def to_json(self) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
