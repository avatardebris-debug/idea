"""Card, Deck, and Shoe implementations for card games.

Provides:
- Card: represents a single playing card with suit, rank, and display.
- Deck: a standard 52-card deck with shuffle and deal operations.
- Shoe: multiple decks combined, with cut-card shuffle for casino-style dealing.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Suit(Enum):
    """Standard playing card suits."""
    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"

    def __str__(self) -> str:
        return self.value


class Rank(Enum):
    """Standard playing card ranks."""
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def display(self) -> str:
        """Human-readable rank display."""
        mapping = {
            Rank.TWO: "2", Rank.THREE: "3", Rank.FOUR: "4", Rank.FIVE: "5",
            Rank.SIX: "6", Rank.SEVEN: "7", Rank.EIGHT: "8", Rank.NINE: "9",
            Rank.TEN: "10", Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K",
            Rank.ACE: "A",
        }
        return mapping[self]

    @property
    def blackjack_value(self) -> int:
        """Card value for blackjack: face cards = 10, aces = 11."""
        if self in (Rank.JACK, Rank.QUEEN, Rank.KING):
            return 10
        if self == Rank.ACE:
            return 11
        return self.value


@dataclass(frozen=True)
class Card:
    """A single playing card."""
    suit: Suit
    rank: Rank

    @property
    def display(self) -> str:
        """Display string like 'AH', '10C', 'KS'."""
        return f"{self.rank.display}{self.suit.value}"

    @property
    def blackjack_value(self) -> int:
        """Blackjack numeric value of this card."""
        return self.rank.blackjack_value

    def __str__(self) -> str:
        return self.display

    def __repr__(self) -> str:
        return f"Card({self.rank.display}{self.suit.value})"

    def to_dict(self) -> dict:
        return {"suit": self.suit.value, "rank": self.rank.value}

    @classmethod
    def from_dict(cls, d: dict) -> Card:
        return cls(suit=Suit(d["suit"]), rank=Rank(d["rank"]))


class Deck:
    """A standard 52-card deck with shuffle and deal operations."""

    def __init__(self, seed: Optional[int] = None):
        self._original_cards: List[Card] = []
        self._cards: List[Card] = []
        self._rng = random.Random(seed)
        self._build_deck()

    def _build_deck(self) -> None:
        """Create a fresh 52-card deck."""
        self._original_cards = [
            Card(suit=suit, rank=rank)
            for suit in Suit
            for rank in Rank
        ]
        self._cards = list(self._original_cards)

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset deck to fresh state, optionally with a new seed."""
        if seed is not None:
            self._rng = random.Random(seed)
        self._build_deck()

    def shuffle(self) -> None:
        """Shuffle the deck in place using Fisher-Yates."""
        self._rng.shuffle(self._cards)

    def deal(self, n: int = 1) -> List[Card]:
        """Deal n cards from the top of the deck."""
        if n > len(self._cards):
            raise ValueError(f"Cannot deal {n} cards from a deck with {len(self._cards)} cards.")
        cards = self._cards[:n]
        self._cards = self._cards[n:]
        return cards

    def deal_one(self) -> Card:
        """Deal a single card."""
        return self.deal(1)[0]

    @property
    def remaining(self) -> int:
        """Number of cards remaining in the deck."""
        return len(self._cards)

    @property
    def cards(self) -> List[Card]:
        """Return a copy of the remaining cards."""
        return list(self._cards)

    @property
    def is_empty(self) -> bool:
        return len(self._cards) == 0


class Shoe:
    """Multiple decks combined, with cut-card shuffle for casino-style dealing."""

    def __init__(self, num_decks: int = 6, cut_card_percent: float = 0.25, seed: Optional[int] = None):
        """
        Args:
            num_decks: Number of standard decks in the shoe.
            cut_card_percent: Percentage of cards to leave undealt before reshuffling (0.0-1.0).
            seed: Optional random seed for reproducibility.
        """
        self._num_decks = num_decks
        self._cut_card_percent = max(0.0, min(1.0, cut_card_percent))
        self._rng = random.Random(seed)
        self._cards: List[Card] = []
        self._cut_point: int = 0
        self._build_shoe()

    def _build_shoe(self) -> None:
        """Build the shoe from multiple decks."""
        self._cards = []
        for _ in range(self._num_decks):
            deck = Deck()
            self._cards.extend(deck.cards)
        self._shuffle_with_cut()

    def _shuffle_with_cut(self) -> None:
        """Shuffle and set cut point."""
        self._rng.shuffle(self._cards)
        self._cut_point = int(len(self._cards) * self._cut_card_percent)

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset shoe with optional new seed."""
        if seed is not None:
            self._rng = random.Random(seed)
        self._build_shoe()

    @property
    def num_decks(self) -> int:
        return self._num_decks

    @property
    def remaining(self) -> int:
        return len(self._cards)

    @property
    def cards(self) -> List[Card]:
        return list(self._cards)

    @property
    def is_empty(self) -> bool:
        return len(self._cards) <= self._cut_point

    def deal(self, n: int = 1) -> List[Card]:
        """Deal n cards. If cut point reached, reshuffle."""
        if self.is_empty:
            self._shuffle_with_cut()

        if n > len(self._cards) - self._cut_point:
            n = len(self._cards) - self._cut_point
            if n <= 0:
                self._shuffle_with_cut()
                n = len(self._cards) - self._cut_point

        cards = self._cards[:n]
        self._cards = self._cards[n:]
        return cards

    def deal_one(self) -> Card:
        return self.deal(1)[0]
