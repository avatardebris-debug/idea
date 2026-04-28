"""Hand class with blackjack hand evaluation.

Provides:
- Hand: manages a collection of cards with blackjack-specific evaluation
  (soft/hard totals, bust detection, blackjack detection, push/win/loss).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from advantage_cardgames.core.deck import Card


class HandType(Enum):
    """Types of blackjack hands."""
    HARD = "HARD"
    SOFT = "SOFT"
    PAIR = "PAIR"


class Outcome(Enum):
    """Possible outcomes of a blackjack hand."""
    BLACKJACK = "BLACKJACK"
    WIN = "WIN"
    PUSH = "PUSH"
    LOSS = "LOSS"
    BUST = "BUST"
    FOLD = "FOLD"  # surrendered


@dataclass
class Hand:
    """A blackjack hand with card management and evaluation."""

    cards: List[Card] = field(default_factory=list)
    is_split: bool = False
    is_doubled: bool = False
    is_surrendered: bool = False
    is_finished: bool = False

    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        self.cards.append(card)

    def remove_card(self, card: Card) -> None:
        """Remove a specific card from the hand."""
        if card in self.cards:
            self.cards.remove(card)

    def clear(self) -> None:
        """Clear all cards and reset state."""
        self.cards.clear()
        self.is_split = False
        self.is_doubled = False
        self.is_surrendered = False
        self.is_finished = False

    @property
    def is_empty(self) -> bool:
        return len(self.cards) == 0

    @property
    def is_blackjack(self) -> bool:
        """Check if hand is a natural blackjack (2 cards totaling 21)."""
        return (
            len(self.cards) == 2
            and self.blackjack_total == 21
        )

    @property
    def is_bust(self) -> bool:
        """Check if hand has busted (hard total > 21)."""
        return self.hard_total > 21

    @property
    def is_soft(self) -> bool:
        """Check if hand is a soft hand (contains an ace counted as 11)."""
        return self.soft_total == self.hard_total and self._has_ace_as_11

    @property
    def hard_total(self) -> int:
        """Calculate the hard total of the hand (aces count as 1)."""
        total = 0
        aces = 0

        for card in self.cards:
            if card.rank.is_ace:
                aces += 1
                total += 1
            elif card.rank.is_face:
                total += 10
            else:
                total += card.rank.value

        return total

    @property
    def soft_total(self) -> int:
        """Calculate the soft total of the hand (aces count as 11 if beneficial)."""
        total = 0
        aces = 0

        for card in self.cards:
            if card.rank.is_ace:
                aces += 1
                total += 1
            elif card.rank.is_face:
                total += 10
            else:
                total += card.rank.value

        # Add 10 for each ace if it doesn't cause bust
        while aces > 0 and total + 10 <= 21:
            total += 10
            aces -= 1

        return total

    @property
    def blackjack_total(self) -> int:
        """Calculate the best total for blackjack purposes."""
        if self.is_blackjack:
            return 21
        return self.soft_total

    @property
    def _has_ace_as_11(self) -> bool:
        """Check if hand has an ace counted as 11."""
        total = 0
        aces = 0

        for card in self.cards:
            if card.rank.is_ace:
                aces += 1
                total += 1
            elif card.rank.is_face:
                total += 10
            else:
                total += card.rank.value

        return aces > 0 and total + 10 <= 21

    @property
    def hand_type(self) -> HandType:
        """Determine the type of hand."""
        if len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank:
            return HandType.PAIR
        elif self.is_soft:
            return HandType.SOFT
        else:
            return HandType.HARD

    @property
    def total(self) -> int:
        """Get the best total for the hand."""
        if self.is_bust:
            return self.hard_total
        return self.soft_total

    @total.setter
    def total(self, value: int) -> None:
        """Set the total (for testing purposes)."""
        self._total = value

    @property
    def stood(self) -> bool:
        """Check if player has stood."""
        return self.is_finished

    @property
    def double(self) -> bool:
        """Check if hand is doubled."""
        return self.is_doubled

    @property
    def blackjack(self) -> bool:
        """Check if hand is blackjack."""
        return self.is_blackjack

    @property
    def can_split(self) -> bool:
        """Check if hand can be split (has exactly 2 cards of same rank)."""
        return (
            len(self.cards) == 2 and
            self.cards[0].rank == self.cards[1].rank and
            not self.is_split
        )

    def to_dict(self) -> dict:
        """Convert hand to dictionary."""
        return {
            "cards": [card.to_dict() for card in self.cards],
            "is_split": self.is_split,
            "is_doubled": self.is_doubled,
            "is_surrendered": self.is_surrendered,
            "is_finished": self.is_finished,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Hand":
        """Create hand from dictionary."""
        from advantage_cardgames.core.deck import Card
        hand = cls(
            cards=[Card.from_dict(card_dict) for card_dict in d["cards"]],
            is_split=d["is_split"],
            is_doubled=d["is_doubled"],
            is_surrendered=d["is_surrendered"],
            is_finished=d["is_finished"],
        )
        return hand

    def __str__(self) -> str:
        cards_str = ", ".join(str(card) for card in self.cards)
        return f"Hand([{cards_str}])"

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards}, is_split={self.is_split})"

    def __len__(self) -> int:
        return len(self.cards)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hand):
            return False
        return (
            self.cards == other.cards and
            self.is_split == other.is_split and
            self.is_doubled == other.is_doubled
        )

    def copy(self) -> "Hand":
        """Create a copy of this hand."""
        new_hand = Hand(
            cards=self.cards.copy(),
            is_split=self.is_split,
            is_doubled=self.is_doubled,
            is_surrendered=self.is_surrendered,
            is_finished=self.is_finished,
        )
        return new_hand
