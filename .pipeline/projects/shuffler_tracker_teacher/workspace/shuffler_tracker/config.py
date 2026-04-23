"""
Configuration settings for the Shuffler Tracker Teacher.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Config:
    """Configuration for the shuffler tracker."""
    
    # Deck settings
    deck_size: int = 52
    
    # Shuffle settings
    num_iterations: int = 1000
    cut_variation_range: int = 6  # ±6 cards from ideal 26/26 split
    
    # Visualization settings
    output_dir: str = "output"
    save_visualizations: bool = True
    histogram_bins: int = 20
    
    # Ideal cut position (center of deck)
    ideal_cut_position: int = 26
    
    # Card ranks and suits
    ranks: List[str] = None
    suits: List[str] = None
    
    def __post_init__(self):
        """Initialize default ranks and suits if not provided."""
        if self.ranks is None:
            self.ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        if self.suits is None:
            self.suits = ["hearts", "diamonds", "clubs", "spades"]
    
    @classmethod
    def default(cls) -> "Config":
        """Create a default configuration."""
        return cls()
    
    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create a Config from a dictionary."""
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert Config to a dictionary."""
        return {
            "deck_size": self.deck_size,
            "num_iterations": self.num_iterations,
            "cut_variation_range": self.cut_variation_range,
            "output_dir": self.output_dir,
            "save_visualizations": self.save_visualizations,
            "histogram_bins": self.histogram_bins,
            "ideal_cut_position": self.ideal_cut_position,
        }
