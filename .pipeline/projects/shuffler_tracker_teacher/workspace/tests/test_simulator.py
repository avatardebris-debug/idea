"""
Test suite for ShuffleSimulator class.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shuffler_tracker.config import Config
from shuffler_tracker.simulator import ShuffleSimulator, ShuffleResult, SimulationStats
from shuffler_tracker.models.deck import Deck
from shuffler_tracker.models.shuffle_cut import ShuffleCut


class TestShuffleSimulatorCreation:
    """Test cases for ShuffleSimulator creation."""
    
    def test_simulator_creation_default(self):
        """Test simulator with default config."""
        sim = ShuffleSimulator()
        assert sim.config is not None
        assert sim.config.num_iterations == 1000
        assert sim.config.cut_variation_range == 6
    
    def test_simulator_creation_custom(self):
        """Test simulator with custom config."""
        config = Config(num_iterations=500, cut_variation_range=10)
        sim = ShuffleSimulator(config)
        assert sim.config.num_iterations == 500
        assert sim.config.cut_variation_range == 10
    
    def test_simulator_seed(self):
        """Test setting random seed."""
        sim = ShuffleSimulator()
        sim.set_seed(42)
        # Should not raise an error


class TestShuffleSimulatorIteration:
    """Test cases for single iteration."""
    
    def test_iteration_result(self):
        """Test that iteration produces valid result."""
        config = Config(num_iterations=1, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        result = sim.run_iteration()
        
        assert isinstance(result, ShuffleResult)
        assert isinstance(result.cut, ShuffleCut)
        assert isinstance(result.deck_before, Deck)
        assert isinstance(result.deck_after, Deck)
        assert len(result.deck_before.cards) == 52
        assert len(result.deck_after.cards) == 52
    
    def test_iteration_cut_valid(self):
        """Test that cut is within valid range."""
        config = Config(num_iterations=1, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        result = sim.run_iteration()
        
        cut = result.cut
        assert 1 <= cut.left_half_size <= 51
        assert cut.left_half_size + cut.right_half_size == 52
    
    def test_iteration_deck_changed(self):
        """Test that deck is shuffled after iteration."""
        config = Config(num_iterations=1, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        result = sim.run_iteration()
        
        # Deck should be different after shuffle
        assert result.deck_before.cards != result.deck_after.cards


class TestShuffleSimulatorSimulation:
    """Test cases for full simulation."""
    
    def test_run_simulation(self):
        """Test running multiple iterations."""
        config = Config(num_iterations=100, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        results = sim.run_simulation()
        
        assert len(results) == 100
        assert len(sim.get_results()) == 100
    
    def test_run_simulation_custom_iterations(self):
        """Test running with custom iteration count."""
        config = Config(num_iterations=1000, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        results = sim.run_simulation(num_iterations=50)
        
        assert len(results) == 50
    
    def test_statistics_computation(self):
        """Test statistics computation."""
        config = Config(num_iterations=100, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        stats = sim.get_statistics()
        
        assert isinstance(stats, SimulationStats)
        assert stats.num_iterations == 100
        assert "mean" in stats.cut_statistics
        assert "std" in stats.cut_statistics
    
    def test_cut_distribution_centered(self):
        """Test that cut distribution is centered around 26/26."""
        config = Config(num_iterations=1000, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        stats = sim.get_statistics()
        
        # Mean should be close to 0.5 (26/52)
        mean_ratio = stats.mean_cut_ratio
        assert 0.45 < mean_ratio < 0.55, f"Mean ratio {mean_ratio} not centered around 0.5"
    
    def test_cut_variation_range(self):
        """Test that cut variation respects configured range."""
        config = Config(num_iterations=100, cut_variation_range=3)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        results = sim.get_results()
        
        # All cuts should be within variation range
        for result in results:
            deviation = abs(result.cut.deviation_from_ideal)
            assert deviation <= config.cut_variation_range
    
    def test_reproducibility_with_seed(self):
        """Test that same seed produces same results."""
        config = Config(num_iterations=10, cut_variation_range=6)
        
        sim1 = ShuffleSimulator(config)
        sim1.set_seed(42)
        sim1.run_simulation()
        
        sim2 = ShuffleSimulator(config)
        sim2.set_seed(42)
        sim2.run_simulation()
        
        # Results should be identical
        results1 = sim1.get_results()
        results2 = sim2.get_results()
        
        assert len(results1) == len(results2)
        
        for r1, r2 in zip(results1, results2):
            assert r1.cut.left_half_size == r2.cut.left_half_size


class TestShuffleSimulatorSummary:
    """Test cases for summary printing."""
    
    def test_print_summary(self, capsys):
        """Test that summary prints correctly."""
        config = Config(num_iterations=10, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        
        # Should not raise an error
        sim.print_summary()
        
        captured = capsys.readouterr()
        assert "Shuffle Simulation Summary" in captured.out
        assert "iterations" in captured.out


class TestShuffleSimulatorStatistics:
    """Test cases for statistics properties."""
    
    def test_statistics_mean_left_half(self):
        """Test mean left half calculation."""
        config = Config(num_iterations=10, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        stats = sim.get_statistics()
        
        # Mean left half should be around 26
        assert 20 < stats.mean_left_half < 32
    
    def test_statistics_mean_right_half(self):
        """Test mean right half calculation."""
        config = Config(num_iterations=10, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        stats = sim.get_statistics()
        
        # Mean right half should be around 26
        assert 20 < stats.mean_right_half < 32
    
    def test_statistics_std_cut_ratio(self):
        """Test standard deviation calculation."""
        config = Config(num_iterations=100, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        
        sim.run_simulation()
        stats = sim.get_statistics()
        
        # Std should be positive
        assert stats.std_cut_ratio > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
