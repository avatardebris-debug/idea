"""2D World engine for the Thronglets simulation.

Handles grid management, terrain generation, and bounds checking.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from .models import Thronglet, WorldConfig
from .types import Position, TerrainType


@dataclass
class World:
    """A 2D grid world containing terrain and thronglets.

    Attributes:
        config: Configuration for the world.
        grid: 2D list of terrain types.
        thronglets: Dict mapping thronglet names to their positions.
    """

    config: WorldConfig
    grid: list[list[TerrainType]] = field(default_factory=list)
    thronglets: dict[str, Position] = field(default_factory=dict)
    _thronglet_objects: dict[str, Thronglet] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize the world grid and generate terrain."""
        self._init_grid()
        self._generate_terrain()

    def _init_grid(self) -> None:
        """Create an empty grid filled with EMPTY terrain."""
        self.grid = [
            [TerrainType.EMPTY for _ in range(self.config.width)]
            for _ in range(self.config.height)
        ]

    def _generate_terrain(self) -> None:
        """Generate terrain based on configuration."""
        for y in range(self.config.height):
            for x in range(self.config.width):
                if random.random() < self.config.wall_density:
                    self.grid[y][x] = TerrainType.WALL

    def get_terrain(self, pos: Position) -> TerrainType:
        """Get the terrain type at a position.

        Args:
            pos: The position to query.

        Returns:
            The terrain type at the position.

        Raises:
            ValueError: If the position is out of bounds.
        """
        self._check_bounds(pos)
        return self.grid[pos.y][pos.x]

    def set_terrain(self, pos: Position, terrain: TerrainType) -> None:
        """Set the terrain type at a position.

        Args:
            pos: The position to update.
            terrain: The terrain type to set.

        Raises:
            ValueError: If the position is out of bounds.
        """
        self._check_bounds(pos)
        self.grid[pos.y][pos.x] = terrain

    def add_thronglet(self, name: str, pos: Position, thronglet: Thronglet | None = None) -> None:
        """Add a thronglet to the world at the given position.

        Args:
            name: The name of the thronglet.
            pos: The position to place the thronglet.
            thronglet: Optional Thronglet object to associate with the name.

        Raises:
            ValueError: If the position is out of bounds.
            ValueError: If the position is already occupied.
        """
        self._check_bounds(pos)
        if name in self.thronglets:
            raise ValueError(f"Thronglet '{name}' already exists in the world.")
        if pos in self.thronglets.values():
            raise ValueError(f"Position {pos} is already occupied.")
        self.thronglets[name] = pos
        if thronglet:
            self._thronglet_objects[name] = thronglet

    def remove_thronglet(self, name: str) -> None:
        """Remove a thronglet from the world.

        Args:
            name: The name of the thronglet to remove.

        Raises:
            KeyError: If the thronglet does not exist.
        """
        if name not in self.thronglets:
            raise KeyError(f"Thronglet '{name}' does not exist in the world.")
        del self.thronglets[name]
        if name in self._thronglet_objects:
            del self._thronglet_objects[name]

    def get_thronglet(self, name: str) -> Optional[Thronglet]:
        """Get a thronglet object by name.

        Args:
            name: The name of the thronglet.

        Returns:
            The Thronglet object if it exists, None otherwise.
        """
        return self._thronglet_objects.get(name)

    def get_thronglet_at(self, pos: Position) -> Optional[str]:
        """Get the name of the thronglet at a position.

        Args:
            pos: The position to query.

        Returns:
            The name of the thronglet at the position, or None if empty.
        """
        for name, p in self.thronglets.items():
            if p == pos:
                return name
        return None

    def is_occupied(self, pos: Position) -> bool:
        """Check if a position is occupied by a thronglet.

        Args:
            pos: The position to check.

        Returns:
            True if the position is occupied, False otherwise.
        """
        return pos in self.thronglets.values()

    def is_valid_move(self, pos: Position) -> bool:
        """Check if a position is a valid move (in bounds and not a wall).

        Args:
            pos: The position to check.

        Returns:
            True if the position is valid, False otherwise.
        """
        if not self._is_in_bounds(pos):
            return False
        return self.grid[pos.y][pos.x] != TerrainType.WALL

    def _is_in_bounds(self, pos: Position) -> bool:
        """Check if a position is within the world bounds.

        Args:
            pos: The position to check.

        Returns:
            True if the position is in bounds, False otherwise.
        """
        return 0 <= pos.x < self.config.width and 0 <= pos.y < self.config.height

    def _check_bounds(self, pos: Position) -> None:
        """Check if a position is within the world bounds.

        Args:
            pos: The position to check.

        Raises:
            ValueError: If the position is out of bounds.
        """
        if not self._is_in_bounds(pos):
            raise ValueError(f"Position {pos} is out of bounds.")

    def get_neighbors(self, pos: Position, radius: int = 1) -> list[Position]:
        """Get all positions within a given radius of a position.

        Args:
            pos: The center position.
            radius: The radius to search within.

        Returns:
            A list of valid neighbor positions.
        """
        neighbors = []
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue
                neighbor = pos.offset(dx, dy)
                if self._is_in_bounds(neighbor):
                    neighbors.append(neighbor)
        return neighbors

    def get_thronglets_in_range(self, pos: Position, radius: int = 1) -> list[str]:
        """Get all thronglet names within a given radius of a position.

        Args:
            pos: The center position.
            radius: The radius to search within.

        Returns:
            A list of thronglet names within range.
        """
        in_range = []
        for name, p in self.thronglets.items():
            if p.distance_to(pos) <= radius:
                in_range.append(name)
        return in_range

    def get_random_empty_position(self) -> Position:
        """Get a random empty position in the world.

        Returns:
            A random Position that is not occupied and not a wall.

        Raises:
            ValueError: If no empty positions are available.
        """
        empty_positions = [
            Position(x, y)
            for y in range(self.config.height)
            for x in range(self.config.width)
            if self.grid[y][x] == TerrainType.EMPTY and not self.is_occupied(Position(x, y))
        ]
        if not empty_positions:
            raise ValueError("No empty positions available.")
        return random.choice(empty_positions)

    def to_dict(self) -> dict:
        """Serialize the world to a dictionary.

        Returns:
            A dictionary representation of the world.
        """
        return {
            "config": self.config.to_dict(),
            "grid": [[t.value for t in row] for row in self.grid],
            "thronglets": {name: pos.to_dict() for name, pos in self.thronglets.items()},
            "thronglet_objects": {name: obj.to_dict() for name, obj in self._thronglet_objects.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> World:
        """Deserialize a world from a dictionary.

        Args:
            data: A dictionary representation of the world.

        Returns:
            A World instance.
        """
        config = WorldConfig.from_dict(data["config"])
        world = cls(config=config)
        world.grid = [
            [TerrainType(t) for t in row]
            for row in data["grid"]
        ]
        for name, pos_data in data["thronglets"].items():
            pos = Position(**pos_data)
            world.thronglets[name] = pos
        for name, obj_data in data.get("thronglet_objects", {}).items():
            thronglet = Thronglet.from_dict(obj_data)
            world._thronglet_objects[name] = thronglet
        return world
