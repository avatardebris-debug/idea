"""
ShuffleCut model representing a cut operation and its statistical analysis.
"""

import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class ShuffleCut:
    """
    Represents a cut operation performed during shuffling.
    
    Attributes:
        left_half_size: Number of cards in the left/top half
        right_half_size: Number of cards in the right/bottom half
        cut_ratio: Ratio of left half to total (left / total)
    """
    
    left_half_size: int
    right_half_size: int
    
    # Computed field
    cut_ratio: float = field(default=0.0, init=False)
    
    def __post_init__(self):
        """Validate that left + right equals total deck size."""
        total = self.left_half_size + self.right_half_size
        if total == 0:
            raise ValueError("Total deck size cannot be zero")
        
        self.cut_ratio = self.left_half_size / total
    
    @property
    def total(self) -> int:
        """Return the total deck size."""
        return self.left_half_size + self.right_half_size
    
    @property
    def deviation_from_ideal(self) -> int:
        """
        Calculate deviation from ideal 26/26 cut.
        
        Returns:
            Positive if left half is larger than ideal (26),
            negative if left half is smaller than ideal
        """
        return self.left_half_size - 26
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"ShuffleCut(left={self.left_half_size}, right={self.right_half_size}, ratio={self.cut_ratio:.3f})"
    
    def __repr__(self) -> str:
        """Return detailed representation."""
        return f"ShuffleCut(left_half_size={self.left_half_size}, right_half_size={self.right_half_size})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another ShuffleCut."""
        if not isinstance(other, ShuffleCut):
            return False
        return (self.left_half_size == other.left_half_size and 
                self.right_half_size == other.right_half_size)
    
    @classmethod
    def from_dict(cls, data: dict) -> "ShuffleCut":
        """Create a ShuffleCut from a dictionary."""
        return cls(
            left_half_size=data["left_half_size"],
            right_half_size=data["right_half_size"]
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "ShuffleCut":
        """Create a ShuffleCut from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_dict(self) -> dict:
        """Convert ShuffleCut to a dictionary."""
        return {
            "left_half_size": self.left_half_size,
            "right_half_size": self.right_half_size,
            "cut_ratio": self.cut_ratio
        }
    
    def to_json(self) -> str:
        """Convert ShuffleCut to a JSON string."""
        return json.dumps(self.to_dict())
    
    @staticmethod
    def compute_statistics(cuts: List["ShuffleCut"]) -> dict:
        """
        Compute statistics for a list of ShuffleCuts.
        
        Args:
            cuts: List of ShuffleCut instances
            
        Returns:
            Dictionary containing statistics:
                - mean: Mean cut ratio
                - std: Standard deviation of cut ratio
                - min: Minimum cut ratio
                - max: Maximum cut ratio
                - median: Median cut ratio
                - left_half_mean: Mean left half size
                - distribution: List of cut ratios for histogram
        """
        if not cuts:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0,
                "left_half_mean": 0.0,
                "distribution": []
            }
        
        ratios = [cut.cut_ratio for cut in cuts]
        left_sizes = [cut.left_half_size for cut in cuts]
        
        # Calculate statistics
        n = len(ratios)
        mean_ratio = sum(ratios) / n
        mean_left = sum(left_sizes) / n
        
        # Standard deviation
        variance = sum((r - mean_ratio) ** 2 for r in ratios) / n
        std_ratio = variance ** 0.5
        
        # Median
        sorted_ratios = sorted(ratios)
        median_ratio = sorted_ratios[n // 2]
        
        return {
            "mean": mean_ratio,
            "std": std_ratio,
            "min": min(ratios),
            "max": max(ratios),
            "median": median_ratio,
            "left_half_mean": mean_left,
            "distribution": ratios
        }
