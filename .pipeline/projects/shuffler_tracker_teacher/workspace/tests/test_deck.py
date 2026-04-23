"""
Test suite for Deck class.
"""

import json
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shuffler_tracker.models.card import Card
from shuffler_tracker.models.deck import Deck


class TestDeckCreation:
    """Test cases for Deck creation."""
    
    def test_fresh_deck(self):
        """Test creating a fresh deck."""
        deck = Deck.fresh()
        assert len(deck.cards) == 52
    
    def test_fresh_deck_uniqueness(self):
        """Test that fresh deck contains unique cards."""
        deck = Deck.fresh()
        card_set = set(deck.cards)
        assert len(card_set) == 52
    
    def test_fresh_deck_ordering(self):
        """Test that fresh deck is in expected order."""
        deck = Deck.fresh()
        assert deck.cards[0].rank == "2"
        assert deck.cards[0].suit == "clubs"
        assert deck.cards[-1].rank == "A"
        assert deck.cards[-1].suit == "spades"
    
    def test_deck_from_list(self):
        """Test creating deck from list of cards."""
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = ["clubs", "diamonds", "hearts", "spades"]
        
        cards = []
        for suit in suits:
            for rank in ranks:
                cards.append(Card(rank=rank, suit=suit))
        
        deck = Deck.from_list(cards)
        assert len(deck.cards) == 52
    
    def test_deck_from_list_invalid(self):
        """Test that invalid list raises ValueError."""
        # Too few cards
        with pytest.raises(ValueError):
            Deck.from_list([Card("A", "spades")])
        
        # Duplicate cards
        card = Card("A", "spades")
        cards = [card] * 52
        with pytest.raises(ValueError):
            Deck.from_list(cards)


class TestDeckOperations:
    """Test cases for Deck operations."""
    
    def test_shuffle(self):
        """Test deck shuffling."""
        deck = Deck.fresh()
        original = deck.cards.copy()
        
        deck.shuffle()
        
        # Deck should be shuffled (very unlikely to be same order)
        assert deck.cards != original
    
    def test_shuffle_fisher_yates(self):
        """Test that shuffling uses Fisher-Yates (randomizes properly)."""
        deck = Deck.fresh()
        deck.shuffle()
        
        # After shuffle, first card should not be 2♣
        assert deck.cards[0].rank != "2" or deck.cards[0].suit != "clubs"
    
    def test_cut_valid_position(self):
        """Test cutting at valid positions."""
        deck = Deck.fresh()
        
        # Cut at position 26 (ideal)
        top, bottom = deck.cut(26)
        assert len(top) == 26
        assert len(bottom) == 26
    
    def test_cut_invalid_position(self):
        """Test that invalid cut position raises ValueError."""
        deck = Deck.fresh()
        
        with pytest.raises(ValueError):
            deck.cut(0)
        
        with pytest.raises(ValueError):
            deck.cut(52)
        
        with pytest.raises(ValueError):
            deck.cut(-1)
        
        with pytest.raises(ValueError):
            deck.cut(100)
    
    def test_cut_and_reorder(self):
        """Test cut and reorder operation."""
        deck = Deck.fresh()
        
        # Cut at position 26
        deck.cut_and_reorder(26)
        
        # New top should be what was at position 26 (7♣)
        # Actually, after cut at 26, position 26 becomes position 0
        # Position 26 in fresh deck is 7♣
        assert deck.cards[0].rank == "7"
        assert deck.cards[0].suit == "clubs"
    
    def test_get_top_card(self):
        """Test getting top card."""
        deck = Deck.fresh()
        top = deck.get_top_card()
        
        assert top.rank == "2"
        assert top.suit == "clubs"
    
    def test_get_bottom_card(self):
        """Test getting bottom card."""
        deck = Deck.fresh()
        bottom = deck.get_bottom_card()
        
        assert bottom.rank == "A"
        assert bottom.suit == "spades"
    
    def test_is_sorted(self):
        """Test deck sorting check."""
        deck = Deck.fresh()
        assert deck.is_sorted()
        
        deck.shuffle()
        assert not deck.is_sorted()


class TestDeckSerialization:
    """Test cases for Deck serialization."""
    
    def test_deck_to_dict(self):
        """Test deck serialization to dictionary."""
        deck = Deck.fresh()
        data = deck.to_dict()
        
        assert "cards" in data
        assert len(data["cards"]) == 52
        assert data["cards"][0] == {"rank": "2", "suit": "clubs"}
    
    def test_deck_to_json(self):
        """Test deck serialization to JSON."""
        deck = Deck.fresh()
        json_str = deck.to_json()
        
        data = json.loads(json_str)
        assert len(data["cards"]) == 52
    
    def test_deck_from_dict(self):
        """Test creating deck from dictionary."""
        data = {
            "cards": [
                {"rank": "A", "suit": "spades"},
                {"rank": "K", "suit": "spades"}
            ]
        }
        with pytest.raises(ValueError):  # Only 2 cards
            Deck.from_dict(data)
    
    def test_deck_from_json(self):
        """Test creating deck from JSON string."""
        # Create a valid deck JSON
        cards_data = []
        for suit in ["clubs", "diamonds", "hearts", "spades"]:
            for rank in ["2", "3", "4", "5"]:
                cards_data.append({"rank": rank, "suit": suit})
        
        json_str = json.dumps({"cards": cards_data})
        with pytest.raises(ValueError):  # Only 20 cards
            Deck.from_json(json_str)


class TestDeckStringRepresentation:
    """Test cases for deck string representation."""
    
    def test_deck_str(self):
        """Test deck string representation."""
        deck = Deck.fresh()
        str_repr = str(deck)
        
        assert "2♣" in str_repr
        assert "A♠" in str_repr
    
    def test_deck_repr(self):
        """Test deck detailed representation."""
        deck = Deck.fresh()
        repr_str = repr(deck)
        
        assert "Deck" in repr_str
        assert "cards" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
