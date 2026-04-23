"""
Shuffler Tracker Teacher - Phase 1

A visualization and educational tool that demonstrates card deck shuffling
mechanics with realistic stochastic variation.
"""

from .config import Config
from .models.card import Card
from .models.deck import Deck
from .models.shuffle_cut import ShuffleCut
from .simulator import ShuffleSimulator
from .visualizer import Visualizer

__version__ = "1.0.0"
__all__ = [
    "Config",
    "Card",
    "Deck",
    "ShuffleCut",
    "ShuffleSimulator",
    "Visualizer",
]
