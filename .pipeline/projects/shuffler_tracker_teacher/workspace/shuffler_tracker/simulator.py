"""
Shuffle Simulator for performing multiple shuffle iterations with stochastic cut variation.
"""

import random
from dataclasses import dataclass, field
from typing import List, Optional

from .models.deck import Deck
from .models.shuffle_cut import ShuffleCut
from .config import Config


@dataclass
class ShuffleResult:
    """
    Result of a single shuffle iteration.
    
    Attributes:
        cut: The ShuffleCut performed
        deck_before: Deck state before shuffle
        deck_after: Deck state after shuffle
    """
    
    cut: ShuffleCut
    deck_before: Deck
    deck_after: Deck


@dataclass
class SimulationStats:
    """
    Statistical summary of a shuffle simulation.
    
    Attributes:
        num_iterations: Total number of shuffle iterations performed
        cut_statistics: Statistics from ShuffleCut.compute_statistics
        mean_left_half: Mean left half size
        mean_right_half: Mean right half size
        mean_cut_ratio: Mean cut ratio
    """
    
    num_iterations: int
    cut_statistics: dict
    
    @property
    def mean_left_half(self) -> float:
        """Return mean left half size."""
        return self.cut_statistics.get("left_half_mean", 0.0)
    
    @property
    def mean_right_half(self) -> float:
        """Return mean right half size."""
        return 52 - self.mean_left_half
    
    @property
    def mean_cut_ratio(self) -> float:
        """Return mean cut ratio."""
        return self.cut_statistics.get("mean", 0.0)
    
    @property
    def std_cut_ratio(self) -> float:
        """Return standard deviation of cut ratio."""
        return self.cut_statistics.get("std", 0.0)


class ShuffleSimulator:
    """
    Simulates card shuffling with stochastic cut variation.
    
    Each iteration performs a random cut with variation around
    the ideal 26/26 split.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the simulator.
        
        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or Config.default()
        self.results: List[ShuffleResult] = []
        self._random = random.Random()
    
    def set_seed(self, seed: int) -> None:
        """
        Set random seed for reproducibility.
        
        Args:
            seed: Random seed value
        """
        self._random.seed(seed)
    
    def _generate_random_cut(self) -> ShuffleCut:
        """
        Generate a random cut with variation around 26/26.
        
        The cut position is chosen uniformly within
        [ideal - variation, ideal + variation].
        
        Returns:
            ShuffleCut instance
        """
        ideal = self.config.ideal_cut_position
        variation = self.config.cut_variation_range
        
        # Generate random cut position
        min_pos = max(1, ideal - variation)
        max_pos = min(51, ideal + variation)
        
        cut_position = self._random.randint(min_pos, max_pos)
        
        return ShuffleCut(
            left_half_size=cut_position,
            right_half_size=52 - cut_position
        )
    
    def run_iteration(self) -> ShuffleResult:
        """
        Run a single shuffle iteration.
        
        Returns:
            ShuffleResult with cut and deck states
        """
        # Create fresh deck
        deck_before = Deck.fresh()
        
        # Generate random cut
        cut = self._generate_random_cut()
        
        # Apply cut to deck
        deck_after = Deck.fresh()
        deck_after.cut_and_reorder(cut.left_half_size)
        
        return ShuffleResult(
            cut=cut,
            deck_before=deck_before,
            deck_after=deck_after
        )
    
    def run_simulation(self, num_iterations: Optional[int] = None) -> List[ShuffleResult]:
        """
        Run multiple shuffle iterations.
        
        Args:
            num_iterations: Number of iterations. If None, uses config value.
            
        Returns:
            List of ShuffleResult instances
        """
        iterations = num_iterations or self.config.num_iterations
        
        self.results = []
        for _ in range(iterations):
            result = self.run_iteration()
            self.results.append(result)
        
        return self.results
    
    def get_statistics(self) -> SimulationStats:
        """
        Compute statistics from all simulation results.
        
        Returns:
            SimulationStats with computed statistics
        """
        if not self.results:
            raise RuntimeError("No simulation results. Run simulation first.")
        
        cuts = [result.cut for result in self.results]
        cut_stats = ShuffleCut.compute_statistics(cuts)
        
        return SimulationStats(
            num_iterations=len(self.results),
            cut_statistics=cut_stats
        )
    
    def print_summary(self) -> None:
        """Print a summary of simulation results to console."""
        stats = self.get_statistics()
        
        print("=" * 60)
        print("Shuffle Simulation Summary")
        print("=" * 60)
        print(f"Total iterations: {stats.num_iterations}")
        print(f"Mean cut ratio: {stats.mean_cut_ratio:.4f} (ideal: 0.5000)")
        print(f"Mean left half: {stats.mean_left_half:.2f} cards (ideal: 26)")
        print(f"Mean right half: {stats.mean_right_half:.2f} cards (ideal: 26)")
        print(f"Std deviation: {stats.std_cut_ratio:.4f}")
        print(f"Cut ratio range: [{stats.cut_statistics['min']:.4f}, {stats.cut_statistics['max']:.4f}]")
        print(f"Median cut ratio: {stats.cut_statistics['median']:.4f}")
        print("=" * 60)
    
    def get_results(self) -> List[ShuffleResult]:
        """Return the simulation results."""
        return self.results.copy()
