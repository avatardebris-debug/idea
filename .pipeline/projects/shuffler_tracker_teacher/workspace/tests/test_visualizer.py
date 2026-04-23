"""
Test suite for Visualizer class.
"""

import os
import pytest
import sys
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shuffler_tracker.config import Config
from shuffler_tracker.simulator import ShuffleSimulator, ShuffleResult
from shuffler_tracker.visualizer import Visualizer
from shuffler_tracker.models.deck import Deck
from shuffler_tracker.models.shuffle_cut import ShuffleCut


class TestVisualizerCreation:
    """Test cases for Visualizer creation."""
    
    def test_visualizer_creation_default(self):
        """Test visualizer with default config."""
        vis = Visualizer()
        assert vis.config is not None
        assert vis.fig_width == 10
        assert vis.fig_height == 6
    
    def test_visualizer_creation_custom(self):
        """Test visualizer with custom config."""
        config = Config(output_dir="custom_output", histogram_bins=30)
        vis = Visualizer(config)
        assert vis.config.output_dir == "custom_output"
        assert vis.config.histogram_bins == 30


class TestVisualizerDeckVisualization:
    """Test cases for deck visualization."""
    
    def test_visualize_deck(self):
        """Test deck visualization creates figure."""
        vis = Visualizer()
        deck = Deck.fresh()
        
        fig = vis.visualize_deck(deck, "Test Deck")
        
        assert isinstance(fig, plt.Figure)
        assert fig.get_num_axes() > 0
    
    def test_visualize_deck_saves(self, tmp_path):
        """Test that deck visualization can be saved."""
        vis = Visualizer()
        deck = Deck.fresh()
        
        output_file = tmp_path / "test_deck.png"
        vis.save_figure(vis.visualize_deck(deck, "Test"), str(output_file))
        
        assert output_file.exists()


class TestVisualizerCutDistribution:
    """Test cases for cut distribution visualization."""
    
    def test_visualize_cut_distribution(self):
        """Test cut distribution visualization."""
        vis = Visualizer()
        cuts = [ShuffleCut(left_half_size=26, right_half_size=26)] * 10
        
        fig = vis.visualize_cut_distribution(cuts, "Test Distribution")
        
        assert isinstance(fig, plt.Figure)
        assert fig.get_num_axes() == 1
    
    def test_visualize_cut_distribution_with_variation(self):
        """Test cut distribution with variation."""
        vis = Visualizer()
        
        # Create cuts with variation
        cuts = [
            ShuffleCut(left_half_size=20, right_half_size=32),
            ShuffleCut(left_half_size=26, right_half_size=26),
            ShuffleCut(left_half_size=30, right_half_size=22),
        ]
        
        fig = vis.visualize_cut_distribution(cuts, "Test Distribution")
        
        assert isinstance(fig, plt.Figure)
        assert fig.get_num_axes() == 1


class TestVisualizerBeforeAfter:
    """Test cases for before/after visualization."""
    
    def test_visualize_before_after(self):
        """Test before/after visualization."""
        vis = Visualizer()
        deck_before = Deck.fresh()
        deck_after = Deck.fresh()
        deck_after.shuffle()
        
        fig = vis.visualize_before_after(
            deck_before, deck_after, 26, "Test"
        )
        
        assert isinstance(fig, plt.Figure)
        assert fig.get_num_axes() == 2
    
    def test_visualize_before_after_saves(self, tmp_path):
        """Test that before/after visualization can be saved."""
        vis = Visualizer()
        deck_before = Deck.fresh()
        deck_after = Deck.fresh()
        deck_after.shuffle()
        
        output_file = tmp_path / "test_before_after.png"
        fig = vis.visualize_before_after(deck_before, deck_after, 26, "Test")
        vis.save_figure(fig, str(output_file))
        
        assert output_file.exists()


class TestVisualizerCombined:
    """Test cases for combined visualization."""
    
    def test_visualize_combined(self):
        """Test combined visualization."""
        vis = Visualizer()
        cuts = [ShuffleCut(left_half_size=26, right_half_size=26)] * 10
        
        fig = vis.visualize_combined(cuts, None, "Test Combined")
        
        assert isinstance(fig, plt.Figure)
        assert fig.get_num_axes() == 2
    
    def test_visualize_combined_with_sample(self):
        """Test combined visualization with sample result."""
        config = Config(num_iterations=1, cut_variation_range=6)
        sim = ShuffleSimulator(config)
        result = sim.run_iteration()
        
        vis = Visualizer()
        cuts = [result.cut]
        
        fig = vis.visualize_combined(cuts, result, "Test Combined")
        
        assert isinstance(fig, plt.Figure)
        assert fig.get_num_axes() == 2
    
    def test_visualize_combined_saves(self, tmp_path):
        """Test that combined visualization can be saved."""
        vis = Visualizer()
        cuts = [ShuffleCut(left_half_size=26, right_half_size=26)] * 10
        
        output_file = tmp_path / "test_combined.png"
        fig = vis.visualize_combined(cuts, None, "Test")
        vis.save_figure(fig, str(output_file))
        
        assert output_file.exists()


class TestVisualizerSaveFunctionality:
    """Test cases for save functionality."""
    
    def test_save_figure_creates_directory(self, tmp_path):
        """Test that save creates output directory."""
        config = Config(output_dir=str(tmp_path / "output"))
        vis = Visualizer(config)
        
        deck = Deck.fresh()
        fig = vis.visualize_deck(deck, "Test")
        
        output_file = tmp_path / "output" / "test.png"
        vis.save_figure(fig, "test.png")
        
        assert output_file.parent.exists()
        assert output_file.exists()
    
    def test_save_figure_with_custom_filename(self, tmp_path):
        """Test saving with custom filename."""
        config = Config(output_dir=str(tmp_path))
        vis = Visualizer(config)
        
        deck = Deck.fresh()
        fig = vis.visualize_deck(deck, "Test")
        
        output_file = tmp_path / "custom_name.png"
        vis.save_figure(fig, "custom_name.png")
        
        assert output_file.exists()


class TestVisualizerVisualizeAndSave:
    """Test cases for visualize_and_save convenience method."""
    
    def test_visualize_and_save(self, tmp_path):
        """Test visualize_and_save method."""
        vis = Visualizer()
        cuts = [ShuffleCut(left_half_size=26, right_half_size=26)] * 10
        
        output_file = tmp_path / "test_save.png"
        result_path = vis.visualize_and_save(
            cuts=cuts,
            sample_result=None,
            filename="test_save.png",
            title="Test"
        )
        
        assert os.path.exists(result_path)
        assert result_path.endswith(".png")


class TestVisualizerIntegration:
    """Integration tests for visualizer."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete visualization workflow."""
        config = Config(
            num_iterations=100,
            cut_variation_range=6,
            output_dir=str(tmp_path)
        )
        sim = ShuffleSimulator(config)
        sim.run_simulation()
        
        vis = Visualizer(config)
        results = sim.get_results()
        cuts = [result.cut for result in results]
        
        # Test all visualization methods
        fig1 = vis.visualize_deck(Deck.fresh(), "Fresh Deck")
        fig2 = vis.visualize_cut_distribution(cuts)
        fig3 = vis.visualize_combined(cuts, results[0])
        
        # Test saving
        fig1_path = vis.save_figure(fig1, "fresh_deck.png")
        fig2_path = vis.save_figure(fig2, "distribution.png")
        fig3_path = vis.save_figure(fig3, "combined.png")
        
        assert os.path.exists(fig1_path)
        assert os.path.exists(fig2_path)
        assert os.path.exists(fig3_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
