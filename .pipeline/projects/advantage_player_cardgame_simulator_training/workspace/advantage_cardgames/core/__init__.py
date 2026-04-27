"""Core module for advantage card games.

This module provides the fundamental building blocks for card game simulations:
- Card: Represents a playing card with rank and suit
- Deck: Manages a deck of cards with shuffling and dealing
- Hand: Represents a player's or dealer's hand of cards
- HandType: Enum for classifying hand types (hard, soft, pair)
"""

from .card import Card
from .deck import Deck
from .hand import Hand, HandType

__all__ = [
    "Card",
    "Deck",
    "Hand",
    "HandType",
]
