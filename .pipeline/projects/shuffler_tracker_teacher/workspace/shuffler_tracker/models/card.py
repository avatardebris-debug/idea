"""
Card model representing an individual playing card.
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Card:
    """
    Represents a single playing card with rank and suit.
    
    Attributes:
        rank: Card rank (2-10, J, Q, K, A)
        suit: Card suit (hearts, diamonds, clubs, spades)
    """
    
    rank: str
    suit: str
    
    # Unicode symbols for suits
    SUIT_SYMBOLS = {
        "hearts": "♥",
        "diamonds": "♦",
        "clubs": "♣",
        "spades": "♠"
    }
    
    # Reverse mapping for deserialization
    SUIT_SYMBOLS_REVERSE = {v: k for k, v in SUIT_SYMBOLS.items()}
    
    VALID_RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    VALID_SUITS = ["hearts", "diamonds", "clubs", "spades"]
    
    def __post_init__(self):
        """Validate rank and suit on initialization."""
        if self.rank not in self.VALID_RANKS:
            raise ValueError(f"Invalid rank: {self.rank}. Must be one of {self.VALID_RANKS}")
        if self.suit not in self.VALID_SUITS:
            raise ValueError(f"Invalid suit: {self.suit}. Must be one of {self.VALID_SUITS}")
    
    def __str__(self) -> str:
        """
        Return string representation of the card.
        
        Returns:
            e.g., "A♠", "K♥", "10♦"
        """
        symbol = self.SUIT_SYMBOLS.get(self.suit, self.suit)
        return f"{self.rank}{symbol}"
    
    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return f"Card(rank='{self.rank}', suit='{self.suit}')"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another card."""
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        """Return hash for use in sets and dicts."""
        return hash((self.rank, self.suit))
    
    def __lt__(self, other: "Card") -> bool:
        """
        Compare cards for sorting.
        
        Cards are compared first by suit, then by rank.
        """
        suit_order = ["clubs", "diamonds", "hearts", "spades"]
        rank_order = self.VALID_RANKS
        
        if self.suit != other.suit:
            return suit_order.index(self.suit) < suit_order.index(other.suit)
        return rank_order.index(self.rank) < rank_order.index(other.rank)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Card":
        """Create a Card from a dictionary."""
        return cls(rank=data["rank"], suit=data["suit"])
    
    @classmethod
    def from_json(cls, json_str: str) -> "Card":
        """Create a Card from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def to_dict(self) -> dict:
        """Convert Card to a dictionary."""
        return {
            "rank": self.rank,
            "suit": self.suit
        }
    
    def to_json(self) -> str:
        """Convert Card to a JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_symbol(cls, symbol_str: str) -> "Card":
        """
        Create a Card from a symbol string (e.g., "A♠").
        
        Args:
            symbol_str: String like "A♠", "K♥", "10♦"
            
        Returns:
            Card instance
            
        Raises:
            ValueError: If the symbol string cannot be parsed
        """
        # Find which suit symbol is in the string
        suit_char = None
        suit_name = None
        
        for char, name in cls.SUIT_SYMBOLS.items():
            if char in symbol_str:
                suit_char = char
                suit_name = name
                break
        
        if not suit_char:
            raise ValueError(f"Could not find suit symbol in: {symbol_str}")
        
        # Extract rank (everything except the suit symbol)
        rank = symbol_str.replace(suit_char, "").strip()
        
        if rank not in cls.VALID_RANKS:
            raise ValueError(f"Invalid rank '{rank}' in symbol string: {symbol_str}")
        
        return cls(rank=rank, suit=suit_name)
