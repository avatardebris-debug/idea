"""
Test suite for Card class.
"""

import json
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shuffler_tracker.models.card import Card


class TestCard:
    """Test cases for Card class."""
    
    def test_card_creation_valid(self):
        """Test creating a valid card."""
        card = Card(rank="A", suit="spades")
        assert card.rank == "A"
        assert card.suit == "spades"
    
    def test_card_creation_invalid_rank(self):
        """Test that invalid rank raises ValueError."""
        with pytest.raises(ValueError):
            Card(rank="X", suit="spades")
    
    def test_card_creation_invalid_suit(self):
        """Test that invalid suit raises ValueError."""
        with pytest.raises(ValueError):
            Card(rank="A", suit="clubsx")
    
    def test_card_string_representation(self):
        """Test card string representation."""
        assert str(Card("A", "spades")) == "A♠"
        assert str(Card("K", "hearts")) == "K♥"
        assert str(Card("10", "diamonds")) == "10♦"
        assert str(Card("7", "clubs")) == "7♣"
    
    def test_card_equality(self):
        """Test card equality comparison."""
        card1 = Card("A", "spades")
        card2 = Card("A", "spades")
        card3 = Card("K", "spades")
        
        assert card1 == card2
        assert card1 != card3
        assert card1 != "A♠"  # Different type
    
    def test_card_hash(self):
        """Test card hashing for use in sets."""
        card1 = Card("A", "spades")
        card2 = Card("A", "spades")
        
        assert hash(card1) == hash(card2)
        
        card_set = {Card("A", "spades"), Card("K", "hearts")}
        assert Card("A", "spades") in card_set
        assert len(card_set) == 2
    
    def test_card_less_than(self):
        """Test card comparison for sorting."""
        card1 = Card("2", "clubs")
        card2 = Card("A", "spades")
        
        assert card1 < card2
    
    def test_card_serialization(self):
        """Test card JSON serialization."""
        card = Card("Q", "hearts")
        
        # to_dict
        card_dict = card.to_dict()
        assert card_dict == {"rank": "Q", "suit": "hearts"}
        
        # to_json
        card_json = card.to_json()
        data = json.loads(card_json)
        assert data == {"rank": "Q", "suit": "hearts"}
        
        # from_dict
        card_from_dict = Card.from_dict({"rank": "J", "suit": "diamonds"})
        assert card_from_dict.rank == "J"
        assert card_from_dict.suit == "diamonds"
        
        # from_json
        card_from_json = Card.from_json('{"rank": "10", "suit": "clubs"}')
        assert card_from_json.rank == "10"
        assert card_from_json.suit == "clubs"
    
    def test_card_from_symbol(self):
        """Test creating card from symbol string."""
        card = Card.from_symbol("A♠")
        assert card.rank == "A"
        assert card.suit == "spades"
        
        card = Card.from_symbol("K♥")
        assert card.rank == "K"
        assert card.suit == "hearts"
        
        card = Card.from_symbol("10♦")
        assert card.rank == "10"
        assert card.suit == "diamonds"
    
    def test_card_from_symbol_invalid(self):
        """Test that invalid symbol raises ValueError."""
        with pytest.raises(ValueError):
            Card.from_symbol("X♠")
        
        with pytest.raises(ValueError):
            Card.from_symbol("A♣x")


class TestCardUniqueness:
    """Test cases for card uniqueness."""
    
    def test_all_cards_unique(self):
        """Test that all 52 cards are unique."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = ["hearts", "diamonds", "clubs", "spades"]
        
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append(Card(rank=rank, suit=suit))
        
        # Check all are unique
        assert len(set(cards)) == 52
        assert len(cards) == 52
    
    def test_duplicate_cards_detected(self):
        """Test that duplicate cards are detected."""
        card = Card("A", "spades")
        cards = [card, card]  # Duplicate
        
        with pytest.raises(ValueError):
            from shuffler_tracker.models.deck import Deck
            Deck.from_list(cards)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
