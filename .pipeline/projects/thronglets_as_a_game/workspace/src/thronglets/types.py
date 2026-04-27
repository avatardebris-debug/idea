"""Core type definitions for the thronglets system.

Provides:
    - Position: 2D grid coordinates
    - TerrainType: Enum of possible cell terrain types
    - Direction: Cardinal movement directions
    - ActionType: Enum of possible thronglet actions
    - InteractionType: Enum of interaction kinds between thronglets
    - Prompt: Typed prompt message structure
    - InteractionEvent: Typed interaction event record
"""

from __future__ import annotations

import enum
import time
from dataclasses import dataclass, field
from typing import Optional


class TerrainType(enum.Enum):
    """Types of terrain that can exist on a world cell."""

    EMPTY = "empty"
    WALL = "wall"
    WATER = "water"
    FOOD = "food"
    NEST = "nest"


class Direction(enum.Enum):
    """Cardinal directions for thronglet movement."""

    NORTH = (0, -1)
    SOUTH = (0, 1)
    EAST = (1, 0)
    WEST = (-1, 0)
    STAY = (0, 0)

    def delta(self) -> tuple[int, int]:
        """Return the (dx, dy) offset for this direction."""
        return self.value  # type: ignore[no-any-return]


class ActionType(enum.Enum):
    """Actions a thronglet can take."""

    MOVE = "move"
    COMMUNICATE = "communicate"
    OBSERVE = "observe"
    EAT = "eat"
    REST = "rest"
    IDLE = "idle"


class InteractionType(enum.Enum):
    """Types of interactions between thronglets."""

    MESSAGE = "message"
    COLLECT = "collect"
    CONFLICT = "conflict"
    COOPERATE = "cooperate"
    GREETING = "greet"


class Behavior(enum.Enum):
    """Behaviors an agent can exhibit."""

    REST = "rest"
    EXPLORE = "explore"
    SEEK_FOOD = "seek_food"
    SEEK_WATER = "seek_water"
    INTERACT = "interact"


@dataclass
class Position:
    """A 2D grid position.

    Attributes:
        x: Column index (0-based, left to right).
        y: Row index (0-based, top to bottom).
    """

    x: int
    y: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Position({self.x}, {self.y})"

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {"x": self.x, "y": self.y}

    def offset(self, dx: int, dy: int) -> Position:
        """Return a new Position offset by (dx, dy)."""
        return Position(self.x + dx, self.y + dy)

    def distance_to(self, other: Position) -> int:
        """Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class Prompt:
    """A prompt/message sent to a thronglet.

    Attributes:
        content: The text content of the prompt.
        sender: Name of the sender (None if from the environment).
        timestamp: Unix timestamp when the prompt was created.
        priority: Priority level 0-10 (higher = more urgent).
    """

    content: str
    sender: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    priority: int = 1

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "content": self.content,
            "sender": self.sender,
            "timestamp": self.timestamp,
            "priority": self.priority,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Prompt:
        """Deserialize from a dictionary."""
        return cls(
            content=data["content"],
            sender=data.get("sender"),
            timestamp=data.get("timestamp", time.time()),
            priority=data.get("priority", 1),
        )


@dataclass
class InteractionEvent:
    """Record of an interaction between two thronglets.

    Attributes:
        interaction_type: The kind of interaction.
        sender: Name of the initiating thronglet.
        receiver: Name of the receiving thronglet (None for broadcast).
        message: The message content.
        position: Position where the interaction occurred.
        timestamp: Unix timestamp of the interaction.
        metadata: Additional context data.
    """

    interaction_type: InteractionType
    sender: str
    receiver: Optional[str] = None
    message: str = ""
    position: Optional[Position] = None
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to a dictionary."""
        return {
            "interaction_type": self.interaction_type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "message": self.message,
            "position": self.position.to_dict() if self.position else None,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> InteractionEvent:
        """Deserialize from a dictionary."""
        pos_data = data.get("position")
        pos = Position(**pos_data) if pos_data else None
        return cls(
            interaction_type=InteractionType(data["interaction_type"]),
            sender=data["sender"],
            receiver=data.get("receiver"),
            message=data.get("message", ""),
            position=pos,
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
        )
