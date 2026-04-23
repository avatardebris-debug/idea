"""
Deck model representing a standard 52-card playing card deck.
"""

import json
import random
from dataclasses import dataclass, field
from typing import List, Optional

from .card import Card


@dataclass
class Deck:
    """
    Represents a standard 52-card playing card deck.
    
    Attributes:
        cards: List of Card objects in the deck
    """
    
    cards: List[Card] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate that deck contains exactly 52 unique cards."""
        if len(self.cards) != 52:
            raise ValueError(f"Deck must contain exactly 52 cards, got {len(self.cards)}")
        
        # Check for uniqueness
        card_set = set(self.cards)
        if len(card_set) != 52:
            raise ValueError("Deck contains duplicate cards")
    
    @classmethod
    def fresh(cls) -> "Deck":
        """
        Create a fresh, ordered 52-card deck.
        
        Cards are ordered by suit (clubs, diamonds, hearts, spades)
        and within each suit by rank (2 through A).
        
        Returns:
            New Deck with all 52 cards in order
        """
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = ["clubs", "diamonds", "hearts", "spades"]
        
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append(Card(rank=rank, suit=suit))
        
        return cls(cards=cards)
    
    @classmethod
    def from_list(cls, cards: List[Card]) -> "Deck":
        """
        Create a Deck from a list of cards.
        
        Args:
            cards: List of Card objects
            
        Returns:
            New Deck instance
            
        Raises:
            ValueError: If cards list doesn't contain exactly 52 unique cards
        """
        if len(cards) != 52:
            raise ValueError(f"Must provide exactly 52 cards, got {len(cards)}")
        
        card_set = set(cards)
        if len(card_set) != 52:
            raise ValueError("Cards list contains duplicates")
        
        return cls(cards=cards)
    
    def shuffle(self) -> "Deck":
        """
        Shuffle the deck using Fisher-Yates algorithm.
        
        Returns:
            Self for method chaining
        """
        cards_list = self.cards  # Make a copy first
        random.shuffle(cards_list)
        self.cards = cards_list
        return self
    
    def cut(self, position: int) -> tuple:
        """
        Cut the deck at the specified position.
        
        Args:
            position: Number of cards to take from top (must be 1-51)
            
        Returns:
            Tuple of (top_half, bottom_half)
            
        Raises:
            ValueError: If position is out of valid range
        """
        if not 1 <= position <= 51:
            raise ValueError(f"Cut position must be between 1 and 51, got {position}")
        
        top_half = self.cards[:position]
        bottom_half = self.cards[position:]
        
        return top_half, bottom_half
    
    def cut_and_reorder(self, position: int) -> "Deck":
        """
        Cut the deck and reorder by placing bottom half on top.
        
        This simulates a real card cut where the bottom portion
        is moved to the top.
        
        Args:
            position: Number of cards to cut at
            
        Returns:
            Self for method chaining
        """
        top, bottom = self.cut(position)
        self.cards = bottom + top
        return self
    
    def get_top_card(self) -> Optional[Card]:
        """Return the top card without removing it."""
        return self.cards[0] if self.cards else None
    
    def get_bottom_card(self) -> Optional[Card]:
        """Return the bottom card without removing it."""
        return self.cards[-1] if self.cards else None
    
    def __str__(self) -> str:
        """Return a compact string representation of the deck."""
        return "[" + ", ".join(str(card) for card in self.cards) + "]"
    
    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return f"Deck(cards={self.cards})"
    
    @classmethod
    def from_dict(cls, data: dict) -> "Deck":
        """Create a Deck from a dictionary."""
        cards_data = data.get("cards", [])
        cards = [Card.from_dict(c) for c in cards_data]
        return cls.from_list(cards)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Deck":
        """Create a Deck from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_dict(self) -> dict:
        """Convert Deck to a dictionary."""
        return {
            "cards": [card.to_dict() for card in self.cards]
        }
    
    def to_json(self) -> str:
        """Convert Deck to a JSON string."""
        return json.dumps(self.to_dict())
    
    def is_sorted(self) -> bool:
        """
        Check if the deck is in its original sorted order.
        
        Returns:
            True if deck is sorted, False otherwise
        """
        expected = Deck.fresh()
        return self.cards == expected.cards
