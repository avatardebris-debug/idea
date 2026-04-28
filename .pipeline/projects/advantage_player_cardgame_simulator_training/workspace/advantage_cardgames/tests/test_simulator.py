"""Tests for simulator module."""

import pytest

from advantage_cardgames.simulators.blackjack import (
    BlackjackGame,
    BlackjackResult,
    SimulatorStats,
    Card,
    Deck,
    Hand,
)


class TestCard:
    """Tests for Card class."""

    def test_card_creation(self):
        """Test creating a card."""
        card = Card(rank=14, suit="♥")
        assert card.rank == 14
        assert card.suit == "♥"

    def test_card_value(self):
        """Test card value calculation."""
        assert Card(rank=5, suit="♣").value == 5
        assert Card(rank=10, suit="♦").value == 10
        assert Card(rank=11, suit="♠").value == 10  # Jack
        assert Card(rank=12, suit="♥").value == 10  # Queen
        assert Card(rank=13, suit="♣").value == 10  # King
        assert Card(rank=14, suit="♦").value == 14  # Ace

    def test_card_is_ace(self):
        """Test ace detection."""
        assert Card(rank=14, suit="♥").is_ace is True
        assert Card(rank=13, suit="♥").is_ace is False

    def test_card_is_face(self):
        """Test face card detection."""
        assert Card(rank=11, suit="♥").is_face is True  # Jack
        assert Card(rank=12, suit="♥").is_face is True  # Queen
        assert Card(rank=13, suit="♥").is_face is True  # King
        assert Card(rank=14, suit="♥").is_face is False  # Ace
        assert Card(rank=10, suit="♥").is_face is False

    def test_card_serialization(self):
        """Test card serialization."""
        card = Card(rank=14, suit="♥")
        d = card.to_dict()
        assert d == {"rank": 14, "suit": "♥"}
        
        card2 = Card.from_dict(d)
        assert card2.rank == 14
        assert card2.suit == "♥"


class TestDeck:
    """Tests for Deck class."""

    def test_deck_creation(self):
        """Test creating a deck."""
        deck = Deck(num_decks=1)
        assert deck.num_decks == 1
        assert len(deck) == 52

    def test_deck_creation_multiple(self):
        """Test creating a multi-deck shoe."""
        deck = Deck(num_decks=2)
        assert deck.num_decks == 2
        assert len(deck) == 104

    def test_deck_draw(self):
        """Test drawing cards from deck."""
        deck = Deck(num_decks=1)
        card = deck.draw()
        assert isinstance(card, Card)
        assert len(deck) == 51

    def test_deck_reset(self):
        """Test resetting deck."""
        deck = Deck(num_decks=1)
        for _ in range(10):
            deck.draw()
        assert len(deck) == 42
        
        deck.reset()
        assert len(deck) == 52

    def test_deck_auto_reset(self):
        """Test deck auto-resets when empty."""
        deck = Deck(num_decks=1)
        for _ in range(52):
            deck.draw()
        assert len(deck) == 0
        
        # Drawing again should auto-reset
        card = deck.draw()
        assert isinstance(card, Card)
        assert len(deck) == 51


class TestHand:
    """Tests for Hand class."""

    def test_hand_creation(self):
        """Test creating a hand."""
        hand = Hand()
        assert len(hand.cards) == 0
        assert hand.total == 0

    def test_hand_add_card(self):
        """Test adding cards to hand."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        assert len(hand.cards) == 2
        assert hand.total == 17

    def test_hand_total_calculation(self):
        """Test hand total calculation."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        assert hand.total == 17

    def test_hand_soft_total(self):
        """Test soft hand detection."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=6, suit="♣"))
        assert hand.total == 17
        assert hand.is_soft is True

    def test_hand_hard_total(self):
        """Test hard hand detection."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        assert hand.total == 17
        assert hand.is_soft is False

    def test_hand_ace_as_one(self):
        """Test ace counted as 1 when needed."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=10, suit="♣"))  # 10
        hand.add_card(Card(rank=6, suit="♦"))   # 6
        assert hand.total == 17  # Ace counted as 1
        assert hand.is_soft is False

    def test_hand_blackjack(self):
        """Test blackjack detection."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=10, suit="♣"))  # 10
        assert hand.is_blackjack is True

    def test_hand_not_blackjack(self):
        """Test non-blackjack hands."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=9, suit="♣"))   # 9
        assert hand.is_blackjack is False

        hand2 = Hand()
        hand2.add_card(Card(rank=10, suit="♥"))
        hand2.add_card(Card(rank=10, suit="♣"))
        hand2.add_card(Card(rank=1, suit="♦"))  # Invalid rank, but testing
        assert hand2.is_blackjack is False

    def test_hand_bust(self):
        """Test bust detection."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=10, suit="♣"))
        hand.add_card(Card(rank=5, suit="♦"))
        assert hand.is_bust is True

    def test_hand_not_bust(self):
        """Test non-bust hands."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        assert hand.is_bust is False

    def test_hand_pair(self):
        """Test pair detection."""
        hand = Hand()
        hand.add_card(Card(rank=8, suit="♥"))
        hand.add_card(Card(rank=8, suit="♣"))
        assert hand.is_pair is True
        assert hand.pair_rank == 8

    def test_hand_not_pair(self):
        """Test non-pair hands."""
        hand = Hand()
        hand.add_card(Card(rank=8, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        assert hand.is_pair is False
        assert hand.pair_rank is None

    def test_hand_reset(self):
        """Test hand reset."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        hand.stood = True
        hand.reset()
        assert len(hand.cards) == 0
        assert hand.stood is False
        assert hand.total == 0

    def test_hand_serialization(self):
        """Test hand serialization."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♣"))
        
        d = hand.to_dict()
        assert d["total"] == 17
        assert d["soft"] is False
        assert d["blackjack"] is False
        
        hand2 = Hand.from_dict(d)
        assert hand2.total == 17
        assert len(hand2.cards) == 2


class TestBlackjackGame:
    """Tests for BlackjackGame class."""

    def test_game_initialization(self):
        """Test game initialization."""
        game = BlackjackGame()
        assert game.status.name == "IDLE"
        assert game.player_hand.total == 0

    def test_game_reset(self):
        """Test game reset."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.reset()
        assert game.status.name == "IDLE"
        assert game.player_hand.total == 0

    def test_deal_initial_cards(self):
        """Test initial card dealing."""
        game = BlackjackGame()
        game.deal_initial_cards()
        assert len(game.player_hand.cards) == 2
        assert len(game.dealer_hand.cards) == 2
        assert game.dealer_upcard is not None

    def test_player_hit(self):
        """Test player hitting."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hit()
        assert len(game.player_hand.cards) == 3

    def test_player_stand(self):
        """Test player standing."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_stand()
        assert game.player_hand.stood is True
        assert game.status.name == "DEALER_TURN"

    def test_player_double(self):
        """Test player doubling."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_double()
        assert game.player_hand.double is True
        assert len(game.player_hand.cards) == 3
        assert game.status.name == "DEALER_TURN"

    def test_player_surrender(self):
        """Test player surrendering."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_surrender()
        assert game.player_hand.surrendered is True
        assert game.status.name == "FOLD"

    def test_dealer_play_hard_17(self):
        """Test dealer stands on hard 17."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.status = game.status.DEALER_TURN
        
        game.dealer_play()
        assert game.dealer_hand.stood is True
        assert game.dealer_hand.total == 17

    def test_dealer_play_soft_17_stands(self):
        """Test dealer stands on soft 17 when configured."""
        game = BlackjackGame(dealer_stands_soft_17=True)
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=14, suit="♥"), Card(rank=6, suit="♣")]  # Soft 17
        game.status = game.status.DEALER_TURN
        
        game.dealer_play()
        assert game.dealer_hand.stood is True
        assert game.dealer_hand.total == 17

    def test_dealer_play_soft_17_hits(self):
        """Test dealer hits on soft 17 when configured."""
        game = BlackjackGame(dealer_stands_soft_17=False)
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=14, suit="♥"), Card(rank=6, suit="♣")]  # Soft 17
        game.status = game.status.DEALER_TURN
        
        initial_total = game.dealer_hand.total
        game.dealer_play()
        assert game.dealer_hand.total > initial_total

    def test_dealer_play_16_hits(self):
        """Test dealer hits on 16."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=6, suit="♣")]
        game.status = game.status.DEALER_TURN
        
        game.dealer_play()
        assert game.dealer_hand.total > 16

    def test_dealer_play_18_stands(self):
        """Test dealer stands on 18."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=8, suit="♣")]
        game.status = game.status.DEALER_TURN
        
        game.dealer_play()
        assert game.dealer_hand.stood is True
        assert game.dealer_hand.total == 18

    def test_determine_result_player_blackjack(self):
        """Test player blackjack result."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=14, suit="♥"), Card(rank=10, suit="♣")]  # Blackjack
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.status = game.status.PLAYER_TURN
        
        game.determine_result()
        assert game.status.name == "BLACKJACK"

    def test_determine_result_push_blackjack(self):
        """Test push when both have blackjack."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=14, suit="♥"), Card(rank=10, suit="♣")]  # Blackjack
        game.dealer_hand.cards = [Card(rank=14, suit="♣"), Card(rank=10, suit="♥")]  # Blackjack
        game.status = game.status.PLAYER_TURN
        
        game.determine_result()
        assert game.status.name == "PUSH"

    def test_determine_result_player_bust(self):
        """Test player bust result."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=10, suit="♣"), Card(rank=5, suit="♦")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.status = game.status.PLAYER_TURN
        
        game.determine_result()
        assert game.status.name == "BUST"

    def test_determine_result_dealer_bust(self):
        """Test dealer bust result."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=10, suit="♣"), Card(rank=5, suit="♦")]
        game.status = game.status.DEALER_TURN
        
        game.determine_result()
        assert game.status.name == "WIN"

    def test_determine_result_player_wins(self):
        """Test player wins result."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=6, suit="♣")]
        game.status = game.status.DEALER_TURN
        
        game.determine_result()
        assert game.status.name == "WIN"

    def test_determine_result_dealer_wins(self):
        """Test dealer wins result."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=6, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.status = game.status.DEALER_TURN
        
        game.determine_result()
        assert game.status.name == "LOSS"

    def test_determine_result_push(self):
        """Test push result."""
        game = BlackjackGame()
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.status = game.status.DEALER_TURN
        
        game.determine_result()
        assert game.status.name == "PUSH"

    def test_play_round_win(self):
        """Test playing a round that results in win."""
        game = BlackjackGame()
        result = game.play_round()
        assert result in [BlackjackResult.WIN, BlackjackResult.BLACKJACK, BlackjackResult.PUSH, BlackjackResult.LOSS, BlackjackResult.BUST]

    def test_get_player_hand(self):
        """Test getting player hand."""
        game = BlackjackGame()
        game.deal_initial_cards()
        hand = game.get_player_hand()
        assert hand is game.player_hand

    def test_get_dealer_hand(self):
        """Test getting dealer hand."""
        game = BlackjackGame()
        game.deal_initial_cards()
        hand = game.get_dealer_hand()
        assert hand is game.dealer_hand

    def test_get_dealer_upcard(self):
        """Test getting dealer upcard."""
        game = BlackjackGame()
        game.deal_initial_cards()
        upcard = game.get_dealer_upcard()
        assert upcard is not None
        assert upcard in game.dealer_hand.cards

    def test_get_status(self):
        """Test getting game status."""
        game = BlackjackGame()
        game.deal_initial_cards()
        status = game.get_status()
        assert status in [GameStatus.PLAYER_TURN, GameStatus.BLACKJACK]

    def test_get_result(self):
        """Test getting game result."""
        game = BlackjackGame()
        game.play_round()
        result = game.get_result()
        assert result is not None


class TestSimulatorStats:
    """Tests for SimulatorStats class."""

    def test_stats_initialization(self):
        """Test stats initialization."""
        stats = SimulatorStats()
        assert stats.total_episodes == 0
        assert stats.win_rate == 0.0

    def test_stats_update_win(self):
        """Test updating stats with win."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.WIN, bet=1.0)
        assert stats.total_episodes == 1
        assert stats.total_wins == 1
        assert stats.win_rate == 1.0

    def test_stats_update_loss(self):
        """Test updating stats with loss."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.LOSS, bet=1.0)
        assert stats.total_episodes == 1
        assert stats.total_losses == 1
        assert stats.loss_rate == 1.0

    def test_stats_update_push(self):
        """Test updating stats with push."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.PUSH, bet=1.0)
        assert stats.total_episodes == 1
        assert stats.total_pushes == 1
        assert stats.push_rate == 1.0

    def test_stats_update_blackjack(self):
        """Test updating stats with blackjack."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.BLACKJACK, bet=1.0)
        assert stats.total_episodes == 1
        assert stats.total_blackjacks == 1
        assert stats.blackjack_rate == 1.0

    def test_stats_update_bust(self):
        """Test updating stats with bust."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.BUST, bet=1.0)
        assert stats.total_episodes == 1
        assert stats.total_busts == 1
        assert stats.bust_rate == 1.0

    def test_stats_update_surrender(self):
        """Test updating stats with surrender."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.SURRENDER, bet=1.0)
        assert stats.total_episodes == 1
        assert stats.total_surrenders == 1
        assert stats.surrender_rate == 1.0

    def test_stats_roi(self):
        """Test ROI calculation."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.WIN, bet=1.0)
        stats.update(BlackjackResult.WIN, bet=1.0)
        stats.update(BlackjackResult.LOSS, bet=1.0)
        assert stats.roi == 0.5  # 2 wins (2.0 payout) - 3 bets = -1.0 / 3.0 = -0.333...
        # Actually: 2 wins = 2.0 payout, 1 loss = 0.0 payout, total payout = 2.0, total bet = 3.0
        # ROI = (2.0 - 3.0) / 3.0 = -0.333...
        assert abs(stats.roi - (-0.333)) < 0.01

    def test_stats_reset(self):
        """Test resetting stats."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.WIN, bet=1.0)
        stats.reset()
        assert stats.total_episodes == 0
        assert stats.total_wins == 0

    def test_stats_to_dict(self):
        """Test converting stats to dictionary."""
        stats = SimulatorStats()
        stats.update(BlackjackResult.WIN, bet=1.0)
        d = stats.to_dict()
        assert "total_episodes" in d
        assert "win_rate" in d
        assert "roi" in d


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_hand_multiple_aces(self):
        """Test hand with multiple aces."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=14, suit="♣"))  # Ace
        hand.add_card(Card(rank=5, suit="♦"))
        assert hand.total == 17  # A + A + 5 = 1 + 1 + 5 = 7 or 11 + 1 + 5 = 17
        assert hand.is_soft is True  # One ace counted as 11

    def test_hand_three_aces(self):
        """Test hand with three aces."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=14, suit="♣"))  # Ace
        hand.add_card(Card(rank=14, suit="♦"))  # Ace
        hand.add_card(Card(rank=10, suit="♠"))  # 10
        assert hand.total == 12  # A + A + A + 10 = 1 + 1 + 1 + 10 = 13 or 11 + 1 + 1 + 10 = 23 (bust)
        # Actually: 11 + 1 + 1 + 10 = 23 (bust), so 1 + 1 + 1 + 10 = 13
        assert hand.total == 13
        assert hand.is_soft is False

    def test_hand_soft_17_variations(self):
        """Test various soft 17 combinations."""
        # A + 6 = soft 17
        hand1 = Hand()
        hand1.add_card(Card(rank=14, suit="♥"))
        hand1.add_card(Card(rank=6, suit="♣"))
        assert hand1.total == 17
        assert hand1.is_soft is True

        # A + 6 + 2 = soft 19 (ace still counts as 11)
        hand2 = Hand()
        hand2.add_card(Card(rank=14, suit="♥"))
        hand2.add_card(Card(rank=6, suit="♣"))
        hand2.add_card(Card(rank=2, suit="♦"))
        assert hand2.total == 19
        assert hand2.is_soft is True

        # A + 6 + 5 = soft 12 (ace still counts as 11)
        hand3 = Hand()
        hand3.add_card(Card(rank=14, suit="♥"))
        hand3.add_card(Card(rank=6, suit="♣"))
        hand3.add_card(Card(rank=5, suit="♦"))
        assert hand3.total == 12
        assert hand3.is_soft is True

    def test_dealer_soft_17_edge_case(self):
        """Test dealer soft 17 edge case with stands_soft_17=False."""
        game = BlackjackGame(dealer_stands_soft_17=False)
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=14, suit="♥"), Card(rank=6, suit="♣")]  # Soft 17
        game.status = game.status.DEALER_TURN
        
        initial_total = game.dealer_hand.total
        game.dealer_play()
        # Should hit on soft 17 when stands_soft_17=False
        assert game.dealer_hand.total > initial_total

    def test_dealer_soft_17_edge_case_stands(self):
        """Test dealer soft 17 edge case with stands_soft_17=True."""
        game = BlackjackGame(dealer_stands_soft_17=True)
        game.deal_initial_cards()
        game.player_hand.cards = [Card(rank=10, suit="♥"), Card(rank=7, suit="♣")]
        game.dealer_hand.cards = [Card(rank=14, suit="♥"), Card(rank=6, suit="♣")]  # Soft 17
        game.status = game.status.DEALER_TURN
        
        game.dealer_play()
        # Should stand on soft 17 when stands_soft_17=True
        assert game.dealer_hand.stood is True
        assert game.dealer_hand.total == 17

    def test_hard_17_vs_soft_17(self):
        """Test difference between hard and soft 17."""
        # Hard 17: 10 + 7
        hard_17 = Hand()
        hard_17.add_card(Card(rank=10, suit="♥"))
        hard_17.add_card(Card(rank=7, suit="♣"))
        assert hard_17.total == 17
        assert hard_17.is_soft is False

        # Soft 17: A + 6
        soft_17 = Hand()
        soft_17.add_card(Card(rank=14, suit="♥"))
        soft_17.add_card(Card(rank=6, suit="♣"))
        assert soft_17.total == 17
        assert soft_17.is_soft is True

    def test_game_status_transitions(self):
        """Test game status transitions."""
        game = BlackjackGame()
        
        # Initial state
        assert game.status.name == "IDLE"
        
        # After deal
        game.deal_initial_cards()
        assert game.status in [GameStatus.PLAYER_TURN, GameStatus.BLACKJACK]
        
        # After player stands
        game.player_stand()
        assert game.status.name == "DEALER_TURN"
        
        # After dealer plays
        game.dealer_play()
        assert game.status in [GameStatus.WIN, GameStatus.LOSS, GameStatus.PUSH, GameStatus.BUST]

    def test_result_data_serialization(self):
        """Test result data serialization."""
        result = BlackjackResultData(
            outcome=BlackjackResult.WIN,
            bet=1.0,
            payout=1.0,
            net_result=1.0
        )
        d = result.to_dict()
        assert d["outcome"] == "WIN"
        assert d["bet"] == 1.0
        assert d["payout"] == 1.0
        assert d["net_result"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
