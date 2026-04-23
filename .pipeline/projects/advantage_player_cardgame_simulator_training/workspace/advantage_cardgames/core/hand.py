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


class Outcome(Enum):
    """Possible outcomes of a blackjack hand."""
    BLACKJACK = "blackjack"
    WIN = "win"
    PUSH = "push"
    LOSS = "loss"
    BUST = "bust"
    FOLD = "fold"  # surrendered


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
        """Calculate the hard total of the hand (aces counted as 1)."""
        total = 0
        aces = 0
        for card in self.cards:
            if card.rank.value == 14:  # Ace
                aces += 1
                total += 1
            elif card.rank.value >= 11:  # Face cards
                total += 10
            else:
                total += card.rank.value
        # Add 10 for each ace that can be 11 without busting
        for _ in range(aces):
            if total + 11 <= 21:
                total += 10
                break
        return total

    @property
    def soft_total(self) -> int:
        """Calculate the soft total (always counts aces as 11 if possible)."""
        total = 0
        aces = 0
        for card in self.cards:
            if card.rank.value == 14:  # Ace
                aces += 1
            elif card.rank.value >= 11:  # Face cards
                total += 10
            else:
                total += card.rank.value
        total += aces * 11
        return total

    @property
    def blackjack_total(self) -> int:
        """Get the best blackjack total (soft if possible, else hard)."""
        if self._has_ace_as_11:
            return self.soft_total
        return self.hard_total

    @property
    def _has_ace_as_11(self) -> bool:
        """Check if the hand contains an ace that can be counted as 11."""
        if not self.cards:
            return False
        total = 0
        aces = 0
        for card in self.cards:
            if card.rank.value == 14:
                aces += 1
            elif card.rank.value >= 11:
                total += 10
            else:
                total += card.rank.value
        # Can we count at least one ace as 11 without busting?
        for i in range(aces):
            if total + 11 + i * 10 <= 21:
                return True
        return False

    @property
    def is_double_down_eligible(self) -> bool:
        """Check if hand is eligible for double down (exactly 2 cards)."""
        return len(self.cards) == 2 and not self.is_split

    @property
    def is_split_eligible(self) -> bool:
        """Check if hand is eligible for split (exactly 2 cards of same rank)."""
        return (
            len(self.cards) == 2
            and self.cards[0].rank == self.cards[1].rank
            and not self.is_split
        )

    @property
    def is_surrender_eligible(self) -> bool:
        """Check if hand is eligible for surrender (exactly 2 cards, not busted)."""
        return len(self.cards) == 2 and not self.is_bust and not self.is_blackjack

    def evaluate_against_dealer(self, dealer_total: int, dealer_is_blackjack: bool) -> Outcome:
        """Evaluate this hand's outcome against the dealer's total.

        Args:
            dealer_total: The dealer's final hand total.
            dealer_is_blackjack: Whether the dealer has a natural blackjack.

        Returns:
            Outcome enum indicating the result.
        """
        if self.is_surrendered:
            return Outcome.FOLD

        if self.is_bust:
            return Outcome.BUST

        if self.is_blackjack:
            if dealer_is_blackjack:
                return Outcome.PUSH
            return Outcome.WIN

        if dealer_is_blackjack:
            return Outcome.LOSS

        if dealer_total > 21:
            return Outcome.WIN

        if self.blackjack_total > dealer_total:
            return Outcome.WIN

        if self.blackjack_total == dealer_total:
            return Outcome.PUSH

        return Outcome.LOSS

    def __str__(self) -> str:
        if not self.cards:
            return "Hand[]"
        cards_str = ", ".join(str(c) for c in self.cards)
        total = self.blackjack_total
        soft_tag = " (soft)" if self.is_soft else ""
        return f"Hand[{cards_str}] = {total}{soft_tag}"

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards}, is_split={self.is_split})"

    def to_dict(self) -> dict:
        return {
            "cards": [c.to_dict() for c in self.cards],
            "is_split": self.is_split,
            "is_doubled": self.is_doubled,
            "is_surrendered": self.is_surrendered,
            "is_finished": self.is_finished,
        }

    @classmethod
    def from_dict(cls, d: dict) -> Hand:
        h = cls()
        h.cards = [Card.from_dict(c) for c in d["cards"]]
        h.is_split = d.get("is_split", False)
        h.is_doubled = d.get("is_doubled", False)
        h.is_surrendered = d.get("is_surrendered", False)
        h.is_finished = d.get("is_finished", False)
        return h
