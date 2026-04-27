"""Tests for the Thronglets 2D world simulation engine.

This test suite covers:
- Position and coordinate operations
- Terrain type handling
- Direction and movement
- Thronglet state management
- World configuration and serialization
- World grid management
- Integration tests for complete workflows
"""

import json
import pytest

from src.thronglets.models import Thronglet, WorldConfig, SimulationConfig
from src.thronglets.types import Position, Direction, TerrainType


class TestPosition:
    """Tests for the Position dataclass."""

    def test_position_creation(self):
        """Test position creation."""
        pos = Position(5, 10)
        assert pos.x == 5
        assert pos.y == 10

    def test_position_equality(self):
        """Test position equality."""
        pos1 = Position(5, 10)
        pos2 = Position(5, 10)
        pos3 = Position(5, 11)
        assert pos1 == pos2
        assert pos1 != pos3

    def test_position_offset(self):
        """Test position offset operations."""
        pos = Position(5, 5)
        assert pos.offset(1, 0) == Position(6, 5)
        assert pos.offset(-1, 0) == Position(4, 5)
        assert pos.offset(0, 1) == Position(5, 6)
        assert pos.offset(0, -1) == Position(5, 4)
        assert pos.offset(2, 3) == Position(7, 8)

    def test_position_distance_to(self):
        """Test distance calculation between positions."""
        pos1 = Position(0, 0)
        pos2 = Position(3, 4)
        assert pos1.distance_to(pos2) == 5

        pos3 = Position(5, 5)
        pos4 = Position(5, 5)
        assert pos3.distance_to(pos4) == 0

        pos5 = Position(1, 1)
        pos6 = Position(4, 5)
        assert pos5.distance_to(pos6) == 5

    def test_position_offset_from_direction(self):
        """Test offset using Direction enum."""
        pos = Position(5, 5)
        assert pos.offset_from(Direction.NORTH) == Position(5, 4)
        assert pos.offset_from(Direction.SOUTH) == Position(5, 6)
        assert pos.offset_from(Direction.EAST) == Position(6, 5)
        assert pos.offset_from(Direction.WEST) == Position(4, 5)
        assert pos.offset_from(Direction.NORTH_EAST) == Position(6, 4)
        assert pos.offset_from(Direction.NORTH_WEST) == Position(4, 4)
        assert pos.offset_from(Direction.SOUTH_EAST) == Position(6, 6)
        assert pos.offset_from(Direction.SOUTH_WEST) == Position(4, 6)

    def test_position_to_dict(self):
        """Test position serialization."""
        pos = Position(7, 12)
        data = pos.to_dict()
        assert data == {"x": 7, "y": 12}

    def test_position_from_dict(self):
        """Test position deserialization."""
        data = {"x": 15, "y": 20}
        pos = Position.from_dict(data)
        assert pos.x == 15
        assert pos.y == 20

    def test_position_from_dict_invalid(self):
        """Test position deserialization with invalid data."""
        with pytest.raises(TypeError):
            Position.from_dict({"x": 10})  # Missing 'y'

    def test_position_hash(self):
        """Test position hashing for use in sets and dicts."""
        pos1 = Position(5, 10)
        pos2 = Position(5, 10)
        pos3 = Position(5, 11)
        assert hash(pos1) == hash(pos2)
        assert hash(pos1) != hash(pos3)


class TestDirection:
    """Tests for the Direction enum."""

    def test_direction_values(self):
        """Test direction enum values."""
        assert Direction.NORTH.value == "north"
        assert Direction.SOUTH.value == "south"
        assert Direction.EAST.value == "east"
        assert Direction.WEST.value == "west"
        assert Direction.NORTH_EAST.value == "north_east"
        assert Direction.NORTH_WEST.value == "north_west"
        assert Direction.SOUTH_EAST.value == "south_east"
        assert Direction.SOUTH_WEST.value == "south_west"

    def test_direction_from_string(self):
        """Test direction from string."""
        assert Direction.from_string("north") == Direction.NORTH
        assert Direction.from_string("south") == Direction.SOUTH
        assert Direction.from_string("east") == Direction.EAST
        assert Direction.from_string("west") == Direction.WEST
        assert Direction.from_string("north_east") == Direction.NORTH_EAST
        assert Direction.from_string("north_west") == Direction.NORTH_WEST
        assert Direction.from_string("south_east") == Direction.SOUTH_EAST
        assert Direction.from_string("south_west") == Direction.SOUTH_WEST

    def test_direction_from_string_invalid(self):
        """Test direction from invalid string."""
        with pytest.raises(ValueError, match="Invalid direction"):
            Direction.from_string("invalid")

    def test_direction_to_string(self):
        """Test direction to string."""
        assert Direction.NORTH.to_string() == "north"
        assert Direction.SOUTH.to_string() == "south"
        assert Direction.EAST.to_string() == "east"
        assert Direction.WEST.to_string() == "west"

    def test_direction_opposite(self):
        """Test opposite direction."""
        assert Direction.NORTH.opposite() == Direction.SOUTH
        assert Direction.SOUTH.opposite() == Direction.NORTH
        assert Direction.EAST.opposite() == Direction.WEST
        assert Direction.WEST.opposite() == Direction.EAST
        assert Direction.NORTH_EAST.opposite() == Direction.SOUTH_WEST
        assert Direction.NORTH_WEST.opposite() == Direction.SOUTH_EAST
        assert Direction.SOUTH_EAST.opposite() == Direction.NORTH_WEST
        assert Direction.SOUTH_WEST.opposite() == Direction.NORTH_EAST

    def test_direction_adjacent(self):
        """Test adjacent directions."""
        north_adj = Direction.NORTH.adjacent()
        assert Direction.NORTH in north_adj
        assert Direction.NORTH_EAST in north_adj
        assert Direction.NORTH_WEST in north_adj
        assert Direction.SOUTH not in north_adj

        east_adj = Direction.EAST.adjacent()
        assert Direction.NORTH_EAST in east_adj
        assert Direction.SOUTH_EAST in east_adj
        assert Direction.WEST not in east_adj


class TestTerrainType:
    """Tests for the TerrainType enum."""

    def test_terrain_type_values(self):
        """Test terrain type enum values."""
        assert TerrainType.EMPTY.value == "empty"
        assert TerrainType.WALL.value == "wall"
        assert TerrainType.NEST.value == "nest"
        assert TerrainType.FOOD.value == "food"
        assert TerrainType.WATER.value == "water"

    def test_terrain_type_from_string(self):
        """Test terrain type from string."""
        assert TerrainType.from_string("empty") == TerrainType.EMPTY
        assert TerrainType.from_string("wall") == TerrainType.WALL
        assert TerrainType.from_string("nest") == TerrainType.NEST
        assert TerrainType.from_string("food") == TerrainType.FOOD
        assert TerrainType.from_string("water") == TerrainType.WATER

    def test_terrain_type_from_string_invalid(self):
        """Test terrain type from invalid string."""
        with pytest.raises(ValueError, match="Invalid terrain type"):
            TerrainType.from_string("invalid")

    def test_terrain_type_to_string(self):
        """Test terrain type to string."""
        assert TerrainType.EMPTY.to_string() == "empty"
        assert TerrainType.WALL.to_string() == "wall"
        assert TerrainType.NEST.to_string() == "nest"
        assert TerrainType.FOOD.to_string() == "food"
        assert TerrainType.WATER.to_string() == "water"


class TestThronglet:
    """Tests for the Thronglet dataclass."""

    def test_thronglet_defaults(self):
        """Test thronglet default values."""
        t = Thronglet(name="Alice")
        assert t.name == "Alice"
        assert t.position == Position(0, 0)
        assert t.fuel == 100.0
        assert t.food == 0.0
        assert t.water == 0.0
        assert t.direction == Direction.NORTH
        assert t.age == 0
        assert t.reproduction_count == 0

    def test_thronglet_custom(self):
        """Test thronglet with custom values."""
        t = Thronglet(
            name="Bob",
            position=Position(5, 10),
            fuel=75.5,
            food=10.0,
            water=5.0,
            direction=Direction.EAST,
            age=5,
            reproduction_count=2,
        )
        assert t.name == "Bob"
        assert t.position == Position(5, 10)
        assert t.fuel == 75.5
        assert t.food == 10.0
        assert t.water == 5.0
        assert t.direction == Direction.EAST
        assert t.age == 5
        assert t.reproduction_count == 2

    def test_thronglet_to_dict(self):
        """Test thronglet serialization."""
        t = Thronglet(
            name="Charlie",
            position=Position(3, 7),
            fuel=50.0,
            food=5.0,
            water=3.0,
            direction=Direction.SOUTH,
            age=3,
            reproduction_count=1,
        )
        data = t.to_dict()
        assert data["name"] == "Charlie"
        assert data["position"] == {"x": 3, "y": 7}
        assert data["fuel"] == 50.0
        assert data["food"] == 5.0
        assert data["water"] == 3.0
        assert data["direction"] == "south"
        assert data["age"] == 3
        assert data["reproduction_count"] == 1

    def test_thronglet_from_dict(self):
        """Test thronglet deserialization."""
        data = {
            "name": "Dave",
            "position": {"x": 8, "y": 12},
            "fuel": 80.0,
            "food": 15.0,
            "water": 10.0,
            "direction": "east",
            "age": 7,
            "reproduction_count": 3,
        }
        t = Thronglet.from_dict(data)
        assert t.name == "Dave"
        assert t.position == Position(8, 12)
        assert t.fuel == 80.0
        assert t.food == 15.0
        assert t.water == 10.0
        assert t.direction == Direction.EAST
        assert t.age == 7
        assert t.reproduction_count == 3

    def test_thronglet_to_json(self):
        """Test thronglet JSON serialization."""
        t = Thronglet(name="Eve")
        json_str = t.to_json()
        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["name"] == "Eve"

    def test_thronglet_from_json(self):
        """Test thronglet JSON deserialization."""
        json_str = '{"name": "Frank", "position": {"x": 5, "y": 5}, "fuel": 100.0, "food": 0.0, "water": 0.0, "direction": "north", "age": 0, "reproduction_count": 0}'
        t = Thronglet.from_json(json_str)
        assert t.name == "Frank"
        assert t.position == Position(5, 5)
        assert t.fuel == 100.0

    def test_thronglet_state_update(self):
        """Test thronglet state update method."""
        t = Thronglet(name="Grace", position=Position(5, 5), fuel=100.0)
        t.update_state(
            new_position=Position(6, 5),
            fuel_change=-10.0,
            food_change=5.0,
            water_change=3.0,
            age_change=1,
            reproduction_change=0,
        )
        assert t.position == Position(6, 5)
        assert t.fuel == 90.0
        assert t.food == 5.0
        assert t.water == 3.0
        assert t.age == 1
        assert t.reproduction_count == 0


class TestWorldConfig:
    """Tests for the WorldConfig dataclass."""

    def test_world_config_defaults(self):
        """Test world config default values."""
        config = WorldConfig()
        assert config.width == 20
        assert config.height == 20
        assert config.default_terrain == TerrainType.EMPTY
        assert config.wall_density == 0.1
        assert config.food_density == 0.05
        assert config.water_density == 0.05

    def test_world_config_custom(self):
        """Test world config with custom values."""
        config = WorldConfig(
            width=30,
            height=30,
            default_terrain=TerrainType.NEST,
            wall_density=0.25,
            food_density=0.15,
            water_density=0.12,
        )
        assert config.width == 30
        assert config.height == 30
        assert config.default_terrain == TerrainType.NEST
        assert config.wall_density == 0.25
        assert config.food_density == 0.15
        assert config.water_density == 0.12

    def test_world_config_to_dict(self):
        """Test world config serialization."""
        config = WorldConfig(
            width=30,
            height=30,
            default_terrain=TerrainType.NEST,
            wall_density=0.25,
            food_density=0.15,
            water_density=0.12,
        )
        data = config.to_dict()
        assert data["width"] == 30
        assert data["height"] == 30
        assert data["default_terrain"] == "nest"
        assert data["wall_density"] == 0.25
        assert data["food_density"] == 0.15
        assert data["water_density"] == 0.12

    def test_world_config_from_dict(self):
        """Test world config deserialization."""
        data = {
            "width": 30,
            "height": 30,
            "default_terrain": "nest",
            "wall_density": 0.25,
            "food_density": 0.15,
            "water_density": 0.12,
        }
        config = WorldConfig.from_dict(data)
        assert config.width == 30
        assert config.height == 30
        assert config.default_terrain == TerrainType.NEST
        assert config.wall_density == 0.25
        assert config.food_density == 0.15
        assert config.water_density == 0.12


class TestSimulationConfig:
    """Tests for SimulationConfig dataclass."""

    def test_simulation_config_defaults(self):
        """Test simulation config default values."""
        config = SimulationConfig()
        assert config.world.width == 20
        assert config.world.height == 20
        assert config.max_ticks == 100
        assert config.render_interval == 1
        assert config.interaction_range == 3

    def test_simulation_config_custom(self):
        """Test simulation config with custom values."""
        config = SimulationConfig(
            max_ticks=50,
            render_interval=5,
            interaction_range=5,
        )
        assert config.max_ticks == 50
        assert config.render_interval == 5
        assert config.interaction_range == 5

    def test_simulation_config_to_dict(self):
        """Test simulation config serialization."""
        config = SimulationConfig(
            max_ticks=75,
            render_interval=10,
            interaction_range=4,
        )
        data = config.to_dict()
        assert data["max_ticks"] == 75
        assert data["render_interval"] == 10
        assert data["interaction_range"] == 4
        assert "world" in data
        assert "thronglets" in data

    def test_simulation_config_from_dict(self):
        """Test simulation config deserialization."""
        data = {
            "world": {
                "width": 25,
                "height": 25,
                "default_terrain": "empty",
                "wall_density": 0.15,
                "food_density": 0.08,
                "water_density": 0.07,
            },
            "thronglets": [
                {"name": "Alice", "position": {"x": 5, "y": 5}},
                {"name": "Bob", "position": {"x": 10, "y": 10}},
            ],
            "max_ticks": 200,
            "render_interval": 20,
            "interaction_range": 5,
        }
        config = SimulationConfig.from_dict(data)
        assert config.world.width == 25
        assert config.world.height == 25
        assert len(config.thronglets) == 2
        assert config.max_ticks == 200
        assert config.render_interval == 20
        assert config.interaction_range == 5

    def test_simulation_config_json_roundtrip(self):
        """Test JSON serialization and deserialization."""
        config = SimulationConfig(
            max_ticks=150,
            render_interval=15,
            interaction_range=4,
        )
        json_str = config.to_json()
        restored = SimulationConfig.from_json(json_str)
        assert restored.max_ticks == config.max_ticks
        assert restored.render_interval == config.render_interval
        assert restored.interaction_range == config.interaction_range


class TestWorld:
    """Tests for the World class."""

    @pytest.fixture
    def small_world(self):
        """Create a small test world."""
        config = WorldConfig(width=10, height=10, wall_density=0.0)
        return World(config=config)

    def test_world_creation(self, small_world):
        """Test world creation."""
        assert small_world.config.width == 10
        assert small_world.config.height == 10
        assert len(small_world.grid) == 10
        assert len(small_world.grid[0]) == 10

    def test_world_get_terrain(self, small_world):
        """Test getting terrain at a position."""
        terrain = small_world.get_terrain(Position(5, 5))
        assert terrain == TerrainType.EMPTY

    def test_world_set_terrain(self, small_world):
        """Test setting terrain at a position."""
        small_world.set_terrain(Position(5, 5), TerrainType.WALL)
        assert small_world.get_terrain(Position(5, 5)) == TerrainType.WALL

    def test_world_set_terrain_out_of_bounds(self, small_world):
        """Test that setting terrain out of bounds raises error."""
        with pytest.raises(ValueError, match="out of bounds"):
            small_world.set_terrain(Position(100, 100), TerrainType.WALL)

    def test_world_get_terrain_out_of_bounds(self, small_world):
        """Test that getting terrain out of bounds raises error."""
        with pytest.raises(ValueError, match="out of bounds"):
            small_world.get_terrain(Position(100, 100))

    def test_world_add_thronglet(self, small_world):
        """Test adding a thronglet to the world."""
        small_world.add_thronglet("Alice", Position(5, 5))
        assert "Alice" in small_world.thronglets
        assert small_world.thronglets["Alice"] == Position(5, 5)

    def test_world_add_thronglet_duplicate(self, small_world):
        """Test that adding a thronglet with duplicate name raises error."""
        small_world.add_thronglet("Alice", Position(5, 5))
        with pytest.raises(ValueError, match="already exists"):
            small_world.add_thronglet("Alice", Position(6, 6))

    def test_world_add_thronglet_occupied(self, small_world):
        """Test that adding a thronglet to occupied position raises error."""
        small_world.add_thronglet("Alice", Position(5, 5))
        with pytest.raises(ValueError, match="already occupied"):
            small_world.add_thronglet("Bob", Position(5, 5))

    def test_world_remove_thronglet(self, small_world):
        """Test removing a thronglet from the world."""
        small_world.add_thronglet("Alice", Position(5, 5))
        small_world.remove_thronglet("Alice")
        assert "Alice" not in small_world.thronglets

    def test_world_remove_thronglet_not_found(self, small_world):
        """Test that removing non-existent thronglet raises KeyError."""
        with pytest.raises(KeyError, match="does not exist"):
            small_world.remove_thronglet("NonExistent")

    def test_world_get_thronglet_at(self, small_world):
        """Test getting thronglet at a position."""
        small_world.add_thronglet("Alice", Position(5, 5))
        assert small_world.get_thronglet_at(Position(5, 5)) == "Alice"
        assert small_world.get_thronglet_at(Position(6, 6)) is None

    def test_world_is_occupied(self, small_world):
        """Test checking if a position is occupied."""
        assert small_world.is_occupied(Position(5, 5)) is False
        small_world.add_thronglet("Alice", Position(5, 5))
        assert small_world.is_occupied(Position(5, 5)) is True

    def test_world_is_valid_move(self, small_world):
        """Test checking if a move is valid."""
        assert small_world.is_valid_move(Position(5, 5)) is True
        small_world.set_terrain(Position(3, 3), TerrainType.WALL)
        assert small_world.is_valid_move(Position(3, 3)) is False

    def test_world_is_valid_move_out_of_bounds(self, small_world):
        """Test that out of bounds positions are invalid moves."""
        assert small_world.is_valid_move(Position(100, 100)) is False

    def test_world_get_neighbors(self, small_world):
        """Test getting neighbor positions."""
        neighbors = small_world.get_neighbors(Position(5, 5), radius=1)
        assert len(neighbors) == 8
        assert Position(4, 4) in neighbors
        assert Position(6, 6) in neighbors

    def test_world_get_neighbors_radius_2(self, small_world):
        """Test getting neighbors with larger radius."""
        neighbors = small_world.get_neighbors(Position(5, 5), radius=2)
        assert len(neighbors) == 24  # 5x5 square minus center

    def test_world_get_thronglets_in_range(self, small_world):
        """Test getting thronglets within range."""
        small_world.add_thronglet("Alice", Position(5, 5))
        small_world.add_thronglet("Bob", Position(5, 6))  # Adjacent to Alice
        small_world.add_thronglet("Charlie", Position(8, 8))  # Further away

        in_range = small_world.get_thronglets_in_range(Position(5, 5), radius=1)
        assert "Alice" in in_range
        assert "Bob" in in_range
        assert "Charlie" not in in_range

    def test_world_get_random_empty_position(self, small_world):
        """Test getting a random empty position."""
        pos = small_world.get_random_empty_position()
        assert small_world.is_valid_move(pos) is True
        assert small_world.is_occupied(pos) is False

    def test_world_get_random_empty_position_full(self, small_world):
        """Test that getting random position raises error when full."""
        # Fill the world with walls
        for y in range(10):
            for x in range(10):
                small_world.set_terrain(Position(x, y), TerrainType.WALL)

        with pytest.raises(ValueError, match="No empty positions"):
            small_world.get_random_empty_position()

    def test_world_to_dict(self, small_world):
        """Test world serialization."""
        small_world.add_thronglet("Alice", Position(5, 5))
        data = small_world.to_dict()
        assert "config" in data
        assert "grid" in data
        assert "thronglets" in data
        assert "Alice" in data["thronglets"]

    def test_world_from_dict(self, small_world):
        """Test world deserialization."""
        small_world.add_thronglet("Alice", Position(5, 5))
        data = small_world.to_dict()
        restored = World.from_dict(data)
        assert restored.config.width == small_world.config.width
        assert restored.config.height == small_world.config.height
        assert "Alice" in restored.thronglets
        assert restored.thronglets["Alice"] == Position(5, 5)


class TestIntegration:
    """Integration tests for the complete system."""

    def test_full_simulation_setup(self):
        """Test setting up a complete simulation."""
        config = SimulationConfig(
            world=WorldConfig(width=20, height=20, wall_density=0.1),
            max_ticks=50,
            render_interval=5,
            interaction_range=3,
        )
        assert config.world.width == 20
        assert config.world.height == 20
        assert config.max_ticks == 50

    def test_world_with_thronglets(self):
        """Test world with multiple thronglets."""
        config = WorldConfig(width=15, height=15, wall_density=0.0)
        world = World(config=config)

        # Add multiple thronglets
        world.add_thronglet("Alice", Position(5, 5))
        world.add_thronglet("Bob", Position(7, 7))
        world.add_thronglet("Charlie", Position(10, 10))

        # Verify all thronglets are present
        assert "Alice" in world.thronglets
        assert "Bob" in world.thronglets
        assert "Charlie" in world.thronglets

        # Verify positions
        assert world.thronglets["Alice"] == Position(5, 5)
        assert world.thronglets["Bob"] == Position(7, 7)
        assert world.thronglets["Charlie"] == Position(10, 10)

        # Test neighbor queries
        alice_neighbors = world.get_thronglets_in_range(Position(5, 5), radius=3)
        assert "Alice" in alice_neighbors
        assert "Bob" in alice_neighbors
        assert "Charlie" not in alice_neighbors

    def test_world_serialization_roundtrip(self):
        """Test complete world serialization and deserialization."""
        config = WorldConfig(width=10, height=10, wall_density=0.2)
        world = World(config=config)

        # Add some walls and thronglets
        world.set_terrain(Position(2, 2), TerrainType.WALL)
        world.set_terrain(Position(5, 5), TerrainType.FOOD)
        world.add_thronglet("Alice", Position(3, 3))
        world.add_thronglet("Bob", Position(7, 7))

        # Serialize and deserialize
        data = world.to_dict()
        restored = World.from_dict(data)

        # Verify restored world
        assert restored.config.width == 10
        assert restored.config.height == 10
        assert restored.get_terrain(Position(2, 2)) == TerrainType.WALL
        assert restored.get_terrain(Position(5, 5)) == TerrainType.FOOD
        assert "Alice" in restored.thronglets
        assert "Bob" in restored.thronglets
        assert restored.thronglets["Alice"] == Position(3, 3)
        assert restored.thronglets["Bob"] == Position(7, 7)
