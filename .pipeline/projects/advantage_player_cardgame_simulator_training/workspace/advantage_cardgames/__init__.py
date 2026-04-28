"""Advantage Card Games - Blackjack simulation and training.

A comprehensive framework for simulating blackjack games and training
optimal strategies using Monte Carlo reinforcement learning.

Submodules:
    core: Card game primitives (Card, Deck, Hand)
    simulators: Game simulations (BlackjackGame)
    monte_carlo: Monte Carlo training and learning algorithms
    trainers: High-level training interfaces
"""

__version__ = "0.1.0"

# Core components
from .core import Card, Deck, Hand

# Simulators
from .simulators.blackjack import (
    BlackjackGame,
    BlackjackResult,
    BlackjackResultData,
    GameStatus,
    SimulatorStats,
)

# Monte Carlo components
from .monte_carlo import (
    State,
    Action,
    Episode,
    StateValueEstimator,
    EpsilonGreedyPolicy,
)

# Trainers
from .trainers.blackjack_training import (
    BlackjackMonteCarloTrainer,
)

__all__ = [
    # Core
    "Card",
    "Deck",
    "Hand",
    # Simulators
    "BlackjackGame",
    "BlackjackResult",
    "BlackjackResultData",
    "GameStatus",
    "SimulatorStats",
    # Monte Carlo
    "State",
    "Action",
    "Episode",
    "StateValueEstimator",
    "EpsilonGreedyPolicy",
    # Trainers
    "BlackjackMonteCarloTrainer",
]
