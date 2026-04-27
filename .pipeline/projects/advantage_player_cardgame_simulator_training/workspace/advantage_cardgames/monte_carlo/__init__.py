"""Monte Carlo learning module for blackjack advantage card games.

This module provides Monte Carlo control algorithms for learning optimal
blackjack strategy through simulation and reinforcement learning.

Modules:
    training: Monte Carlo training engine with state-value estimation
"""

from .training import (
    Action,
    Episode,
    EpsilonGreedyPolicy,
    MonteCarloTrainer,
    State,
    StateValueEstimator,
)

__all__ = [
    "Action",
    "Episode",
    "EpsilonGreedyPolicy",
    "MonteCarloTrainer",
    "State",
    "StateValueEstimator",
]
