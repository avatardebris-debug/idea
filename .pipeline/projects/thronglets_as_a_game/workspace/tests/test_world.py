"""Tests for the 2D World engine (Task 2)."""

import pytest
from thronglets.types import Position, TerrainType
from thronglets.models import WorldConfig
from thronglets.world import World


class TestWorldInit:
    def test_grid_creation(self):
        config = WorldConfig(width=5, height=5, wall_density=0.0)
        world = World(config)
        assert len(world.grid) == 5
        for row in world.grid:
            assert len(row) == 5
            assert all(t == TerrainType.EMPTY for t in row)

    def test_thronglets_empty(self):
        config = WorldConfig(width=10, height=10)
        world = World(config)
        assert world.thronglets == {}

    def test_config_stored(self):
        config = WorldConfig(width=8, height=12)
        world = World(config)
        assert world.config == config


class TestTerrainGeneration:
    def test_wall_density_creates_walls(self):
        config = WorldConfig(width=10, height=10, wall_density=1.0)
        world = World(config)
        for row in world.grid:
            for cell in row:
                assert cell == TerrainType.WALL

    def test_zero_wall_density(self):
        config = WorldConfig(width=10, height=10, wall_density=0.0)
        world = World(config)
        for row in world.grid:
            for cell in row:
                assert cell == TerrainType.EMPTY

    def test_partial_wall_density(self):
        config = WorldConfig(width=10, height=10, wall_density=0.5)
        world = World(config)
        walls = sum(1 for row in world.grid for cell in row if cell == TerrainType.WALL)
        # With density 0.5, expect roughly half walls (allow some variance)
        assert 30 <= walls <= 70


class TestGetTerrain:
    def test_get_empty_terrain(self):
        config = WorldConfig(width=5, height=5, wall_density=0.0)
        world = World(config)
        assert world.get_terrain(Position(0, 0)) == TerrainType.EMPTY

    def test_get_wall_terrain(self):
        config = WorldConfig(width=5, height=5, wall_density=1.0)
        world = World(config)
        assert world.get_terrain(Position(2, 2)) == TerrainType.WALL

    def test_get_out_of_bounds_raises(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        with pytest.raises(ValueError, match="out of bounds"):
            world.get_terrain(Position(5, 0))
        with pytest.raises(ValueError, match="out of bounds"):
            world.get_terrain(Position(-1, 0))
        with pytest.raises(ValueError, match="out of bounds"):
            world.get_terrain(Position(0, 5))
        with pytest.raises(ValueError, match="out of bounds"):
            world.get_terrain(Position(0, -1))


class TestSetTerrain:
    def test_set_terrain(self):
        config = WorldConfig(width=5, height=5, wall_density=0.0)
        world = World(config)
        world.set_terrain(Position(2, 2), TerrainType.WATER)
        assert world.get_terrain(Position(2, 2)) == TerrainType.WATER

    def test_set_out_of_bounds_raises(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        with pytest.raises(ValueError, match="out of bounds"):
            world.set_terrain(Position(5, 0), TerrainType.WATER)


class TestAddThronglet:
    def test_add_thronglet(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        world.add_thronglet("alice", Position(0, 0))
        assert world.thronglets["alice"] == Position(0, 0)

    def test_add_duplicate_thronglet_raises(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        world.add_thronglet("alice", Position(0, 0))
        with pytest.raises(ValueError, match="already exists"):
            world.add_thronglet("alice", Position(1, 1))

    def test_add_to_occupied_position_raises(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        world.add_thronglet("alice", Position(0, 0))
        with pytest.raises(ValueError, match="already occupied"):
            world.add_thronglet("bob", Position(0, 0))

    def test_add_out_of_bounds_raises(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        with pytest.raises(ValueError, match="out of bounds"):
            world.add_thronglet("alice", Position(5, 5))


class TestRemoveThronglet:
    def test_remove_thronglet(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        world.add_thronglet("alice", Position(0, 0))
        world.remove_thronglet("alice")
        assert "alice" not in world.thronglets

    def test_remove_nonexistent_raises(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        with pytest.raises(KeyError, match="does not exist"):
            world.remove_thronglet("bob")


class TestGetThrongletAt:
    def test_get_thronglet_at_position(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        world.add_thronglet("alice", Position(2, 3))
        assert world.get_thronglet_at(Position(2, 3)) == "alice"

    def test_get_thronglet_at_empty_position(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        assert world.get_thronglet_at(Position(0, 0)) is None


class TestIsOccupied:
    def test_occupied_position(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        world.add_thronglet("alice", Position(1, 1))
        assert world.is_occupied(Position(1, 1)) is True
        assert world.is_occupied(Position(0, 0)) is False


class TestIsValidMove:
    def test_valid_move_on_empty(self):
        config = WorldConfig(width=5, height=5, wall_density=0.0)
        world = World(config)
        assert world.is_valid_move(Position(2, 2)) is True

    def test_invalid_move_on_wall(self):
        config = WorldConfig(width=5, height=5, wall_density=1.0)
        world = World(config)
        assert world.is_valid_move(Position(2, 2)) is False

    def test_invalid_move_out_of_bounds(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        assert world.is_valid_move(Position(5, 5)) is False
        assert world.is_valid_move(Position(-1, -1)) is False


class TestGetNeighbors:
    def test_neighbors_within_bounds(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        neighbors = world.get_neighbors(Position(2, 2), radius=1)
        assert len(neighbors) == 8
        for n in neighbors:
            assert world._is_in_bounds(n)

    def test_neighbors_at_corner(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        neighbors = world.get_neighbors(Position(0, 0), radius=1)
        # At corner (0,0), neighbors are (1,0), (0,1), (1,1)
        assert len(neighbors) == 3

    def test_neighbors_at_edge(self):
        config = WorldConfig(width=5, height=5)
        world = World(config)
        neighbors = world.get_neighbors(Position(0, 2), radius=1)
        # At left edge, should have 5 neighbors
        assert len(neighbors) == 5

    def test_neighbors_larger_radius(self):
        config = WorldConfig(width=10, height=10)
        world = World(config)
        neighbors = world.get_neighbors(Position(5, 5), radius=2)
        # 5x5 grid minus center = 24 neighbors
        assert len(neighbors) == 24


class TestGetThrongletsInRange:
    def test_thronglets_in_range(self):
        config = WorldConfig(width=10, height=10)
        world = World(config)
        world.add_thronglet("alice", Position(0, 0))
        world.add_thronglet("bob", Position(1, 0))
        world.add_thronglet("charlie", Position(5, 5))
        in_range = world.get_thronglets_in_range(Position(0, 0), radius=1)
        assert "alice" in in_range
        assert "bob" in in_range
        assert "charlie" not in in_range

    def test_no_thronglets(self):
        config = WorldConfig(width=10, height=10)
        world = World(config)
        in_range = world.get_thronglets_in_range(Position(0, 0), radius=5)
        assert in_range == []


class TestToDict:
    def test_to_dict(self):
        config = WorldConfig(width=3, height=3, wall_density=0.0)
        world = World(config)
        world.add_thronglet("alice", Position(1, 1))
        d = world.to_dict()
        assert d["config"]["width"] == 3
        assert d["config"]["height"] == 3
        assert d["thronglets"]["alice"]["x"] == 1
        assert d["thronglets"]["alice"]["y"] == 1
        assert len(d["grid"]) == 3
        assert len(d["grid"][0]) == 3


class TestFromDict:
    def test_from_dict(self):
        config = WorldConfig(width=3, height=3, wall_density=0.0)
        world = World(config)
        world.add_thronglet("alice", Position(1, 1))
        d = world.to_dict()
        world2 = World.from_dict(d)
        assert world2.config.width == 3
        assert world2.config.height == 3
        assert "alice" in world2.thronglets
        assert world2.thronglets["alice"] == Position(1, 1)

    def test_from_dict_grid(self):
        config = WorldConfig(width=2, height=2, wall_density=1.0)
        world = World(config)
        d = world.to_dict()
        world2 = World.from_dict(d)
        for row in world2.grid:
            for cell in row:
                assert cell == TerrainType.WALL
