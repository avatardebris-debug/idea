"""Tests for core data models and types (Task 1)."""

import json
import time

import pytest

from thronglets.models import SimulationConfig, Thronglet, ThrongletState, WorldConfig
from thronglets.types import (
    InteractionEvent,
    InteractionType,
    Position,
    Prompt,
    TerrainType,
)


# ── Position tests ────────────────────────────────────────────────────────────────


class TestPosition:
    def test_creation(self):
        pos = Position(3, 4)
        assert pos.x == 3
        assert pos.y == 4

    def test_equality(self):
        assert Position(1, 2) == Position(1, 2)
        assert Position(1, 2) != Position(1, 3)

    def test_hash(self):
        s = {Position(1, 2), Position(1, 2), Position(3, 4)}
        assert len(s) == 2

    def test_repr(self):
        assert repr(Position(5, 10)) == "Position(5, 10)"

    def test_offset(self):
        pos = Position(2, 3)
        offset = pos.offset(1, -1)
        assert offset.x == 3
        assert offset.y == 2

    def test_distance_to(self):
        p1 = Position(0, 0)
        p2 = Position(3, 4)
        assert p1.distance_to(p2) == 7


# ── Direction tests ─────────────────────────────────────────────────────────────────


class TestDirection:
    def test_delta(self):
        from thronglets.types import Direction

        assert Direction.NORTH.delta() == (0, -1)
        assert Direction.SOUTH.delta() == (0, 1)
        assert Direction.EAST.delta() == (1, 0)
        assert Direction.WEST.delta() == (-1, 0)
        assert Direction.STAY.delta() == (0, 0)


# ── TerrainType tests ───────────────────────────────────────────────────────────────


class TestTerrainType:
    def test_values(self):
        assert TerrainType.EMPTY.value == "empty"
        assert TerrainType.WALL.value == "wall"
        assert TerrainType.WATER.value == "water"
        assert TerrainType.FOOD.value == "food"
        assert TerrainType.NEST.value == "nest"


# ── Prompt tests ────────────────────────────────────────────────────────────────────


class TestPrompt:
    def test_creation_defaults(self):
        p = Prompt(content="hello")
        assert p.content == "hello"
        assert p.sender is None
        assert p.priority == 1

    def test_creation_full(self):
        ts = time.time()
        p = Prompt(content="hi", sender="alice", timestamp=ts, priority=5)
        assert p.sender == "alice"
        assert p.priority == 5

    def test_to_dict(self):
        p = Prompt(content="test", sender="bob", priority=3)
        d = p.to_dict()
        assert d["content"] == "test"
        assert d["sender"] == "bob"
        assert d["priority"] == 3

    def test_from_dict(self):
        d = {"content": "hi", "sender": "alice", "priority": 2}
        p = Prompt.from_dict(d)
        assert p.content == "hi"
        assert p.sender == "alice"
        assert p.priority == 2

    def test_from_dict_defaults(self):
        d = {"content": "minimal"}
        p = Prompt.from_dict(d)
        assert p.sender is None
        assert p.priority == 1


# ── InteractionEvent tests ──────────────────────────────────────────────────────────


class TestInteractionEvent:
    def test_creation_defaults(self):
        evt = InteractionEvent(
            interaction_type=InteractionType.MESSAGE,
            sender="alice",
        )
        assert evt.receiver is None
        assert evt.message == ""
        assert evt.position is None

    def test_creation_full(self):
        pos = Position(1, 2)
        evt = InteractionEvent(
            interaction_type=InteractionType.COOPERATE,
            sender="alice",
            receiver="bob",
            message="help",
            position=pos,
            metadata={"bonus": 10},
        )
        assert evt.receiver == "bob"
        assert evt.message == "help"
        assert evt.position == pos
        assert evt.metadata["bonus"] == 10

    def test_to_dict(self):
        evt = InteractionEvent(
            interaction_type=InteractionType.GREET,
            sender="alice",
            receiver="bob",
            message="hello",
        )
        d = evt.to_dict()
        assert d["interaction_type"] == "greet"
        assert d["sender"] == "alice"
        assert d["receiver"] == "bob"
        assert d["message"] == "hello"

    def test_to_dict_with_position(self):
        evt = InteractionEvent(
            interaction_type=InteractionType.MESSAGE,
            sender="alice",
            position=Position(5, 6),
        )
        d = evt.to_dict()
        assert d["position"] == {"x": 5, "y": 6}

    def test_from_dict(self):
        d = {
            "interaction_type": "conflict",
            "sender": "alice",
            "receiver": "bob",
            "message": "fight",
            "position": {"x": 1, "y": 2},
            "metadata": {"damage": 5},
        }
        evt = InteractionEvent.from_dict(d)
        assert evt.interaction_type == InteractionType.CONFLICT
        assert evt.receiver == "bob"
        assert evt.message == "fight"
        assert evt.position == Position(1, 2)
        assert evt.metadata["damage"] == 5

    def test_from_dict_defaults(self):
        d = {"interaction_type": "greet", "sender": "alice"}
        evt = InteractionEvent.from_dict(d)
        assert evt.receiver is None
        assert evt.message == ""
        assert evt.position is None


# ── ThrongletState tests ────────────────────────────────────────────────────────────


class TestThrongletState:
    def test_creation_defaults(self):
        s = ThrongletState()
        assert s.energy == 100
        assert s.hunger == 0
        assert s.mood == 0
        assert s.knowledge == []
        assert s.inventory == []

    def test_to_dict(self):
        s = ThrongletState(energy=50, hunger=30, mood=5, knowledge=["a"], inventory=["b"])
        d = s.to_dict()
        assert d["energy"] == 50
        assert d["hunger"] == 30
        assert d["mood"] == 5
        assert d["knowledge"] == ["a"]
        assert d["inventory"] == ["b"]

    def test_from_dict(self):
        d = {"energy": 75, "hunger": 20, "mood": -3, "knowledge": ["x"], "inventory": ["y"]}
        s = ThrongletState.from_dict(d)
        assert s.energy == 75
        assert s.hunger == 20
        assert s.mood == -3
        assert s.knowledge == ["x"]
        assert s.inventory == ["y"]

    def test_from_dict_defaults(self):
        s = ThrongletState.from_dict({})
        assert s.energy == 100
        assert s.hunger == 0


# ── Thronglet tests ─────────────────────────────────────────────────────────────────


class TestThronglet:
    def test_creation_defaults(self):
        t = Thronglet(name="alice", position=Position(0, 0))
        assert t.name == "alice"
        assert t.position == Position(0, 0)
        assert t.state.energy == 100
        assert t.color == "\033[94m"
        assert t.symbol == "T"

    def test_to_dict(self):
        t = Thronglet(name="bob", position=Position(3, 4))
        d = t.to_dict()
        assert d["name"] == "bob"
        assert d["position"]["x"] == 3
        assert d["position"]["y"] == 4
        assert d["symbol"] == "T"

    def test_from_dict(self):
        d = {
            "name": "charlie",
            "position": {"x": 5, "y": 6},
            "state": {"energy": 80, "hunger": 10},
            "symbol": "C",
        }
        t = Thronglet.from_dict(d)
        assert t.name == "charlie"
        assert t.position == Position(5, 6)
        assert t.state.energy == 80
        assert t.symbol == "C"


# ── WorldConfig tests ───────────────────────────────────────────────────────────────


class TestWorldConfig:
    def test_creation_defaults(self):
        wc = WorldConfig()
        assert wc.width == 20
        assert wc.height == 20
        assert wc.default_terrain == TerrainType.EMPTY
        assert wc.wall_density == 0.1

    def test_to_dict(self):
        wc = WorldConfig(width=10, height=15, wall_density=0.2)
        d = wc.to_dict()
        assert d["width"] == 10
        assert d["height"] == 15
        assert d["wall_density"] == 0.2

    def test_from_dict(self):
        d = {"width": 30, "height": 25, "wall_density": 0.15}
        wc = WorldConfig.from_dict(d)
        assert wc.width == 30
        assert wc.height == 25
        assert wc.wall_density == 0.15


# ── SimulationConfig tests ──────────────────────────────────────────────────────────


class TestSimulationConfig:
    def test_creation_defaults(self):
        sc = SimulationConfig()
        assert sc.max_ticks == 100
        assert sc.render_interval == 1
        assert sc.interaction_range == 3
        assert sc.thronglets == []

    def test_to_dict(self):
        sc = SimulationConfig(max_ticks=50, interaction_range=5)
        d = sc.to_dict()
        assert d["max_ticks"] == 50
        assert d["interaction_range"] == 5

    def test_from_dict(self):
        d = {"max_ticks": 200, "interaction_range": 10, "thronglets": [{"name": "a"}]}
        sc = SimulationConfig.from_dict(d)
        assert sc.max_ticks == 200
        assert sc.interaction_range == 10
        assert len(sc.thronglets) == 1

    def test_to_json_from_json(self):
        sc = SimulationConfig(max_ticks=42, interaction_range=7)
        sc.thronglets = [{"name": "test"}]
        json_str = sc.to_json()
        parsed = SimulationConfig.from_json(json_str)
        assert parsed.max_ticks == 42
        assert parsed.interaction_range == 7
        assert len(parsed.thronglets) == 1

    def test_from_json_invalid(self):
        with pytest.raises(json.JSONDecodeError):
            SimulationConfig.from_json("not json")
