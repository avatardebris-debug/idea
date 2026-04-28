"""Comprehensive tests for blackjack simulator module.

Tests cover:
- Card and Deck functionality
- Hand calculations and properties
- Game state management
- Result tracking and statistics
- Complete round simulation
"""

import pytest
from advantage_cardgames.simulators.blackjack import (
    BlackjackGame,
    BlackjackResult,
    BlackjackResultData,
    SimulatorStats,
    Deck,
    Card,
    Hand,
    GameStatus,
)


class TestCard:
    """Tests for Card class."""

    def test_card_creation(self):
        """Test creating a card."""
        card = Card(rank=10, suit="♥")
        assert card.rank == 10
        assert card.suit == "♥"

    def test_card_value_number(self):
        """Test card value for number cards."""
        card = Card(rank=7, suit="♠")
        assert card.value == 7

    def test_card_value_face(self):
        """Test card value for face cards."""
        assert Card(rank=11, suit="♦").value == 10
        assert Card(rank=12, suit="♥").value == 10
        assert Card(rank=13, suit="♣").value == 10

    def test_card_value_ace(self):
        """Test card value for ace."""
        assert Card(rank=14, suit="♠").value == 11

    def test_card_is_ace(self):
        """Test ace detection."""
        assert Card(rank=14, suit="♥").is_ace is True
        assert Card(rank=10, suit="♥").is_ace is False

    def test_card_is_face(self):
        """Test face card detection."""
        assert Card(rank=11, suit="♦").is_face is True
        assert Card(rank=14, suit="♥").is_face is False

    def test_card_to_dict(self):
        """Test card serialization."""
        card = Card(rank=10, suit="♥")
        card_dict = card.to_dict()
        assert card_dict == {"rank": 10, "suit": "♥"}

    def test_card_from_dict(self):
        """Test card deserialization."""
        card_dict = {"rank": 11, "suit": "♠"}
        card = Card.from_dict(card_dict)
        assert card.rank == 11
        assert card.suit == "♠"


class TestDeck:
    """Tests for Deck class."""

    def test_deck_creation(self):
        """Test creating a deck."""
        deck = Deck(num_decks=1)
        assert len(deck._cards) == 52

    def test_deck_creation_multiple_decks(self):
        """Test creating a multi-deck shoe."""
        deck = Deck(num_decks=2)
        assert len(deck._cards) == 104

    def test_deck_draw(self):
        """Test drawing cards from deck."""
        deck = Deck(num_decks=1)
        card = deck.draw()
        assert isinstance(card, Card)
        assert len(deck._cards) == 51

    def test_deck_reset(self):
        """Test resetting deck."""
        deck = Deck(num_decks=1)
        # Draw some cards
        for _ in range(10):
            deck.draw()
        assert len(deck._cards) == 42
        
        # Reset
        deck.reset()
        assert len(deck._cards) == 52

    def test_deck_empty_auto_reset(self):
        """Test deck auto-resets when empty."""
        deck = Deck(num_decks=1)
        # Draw all cards
        for _ in range(52):
            deck.draw()
        assert len(deck._cards) == 0
        
        # Draw again should auto-reset
        card = deck.draw()
        assert isinstance(card, Card)


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
        hand.add_card(Card(rank=7, suit="♠"))
        assert len(hand.cards) == 2
        assert hand.total == 17

    def test_hand_total_with_ace(self):
        """Test hand total with ace counted as 11."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=7, suit="♠"))
        assert hand.total == 18
        assert hand.soft_total == 18

    def test_hand_total_ace_as_1(self):
        """Test hand total with ace counted as 1 when bust."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=10, suit="♠"))  # 10
        hand.add_card(Card(rank=10, suit="♦"))  # 10
        assert hand.total == 11  # Ace counts as 1
        assert hand.is_bust is False

    def test_hand_is_soft(self):
        """Test soft hand detection."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=6, suit="♠"))
        assert hand.is_soft is True

    def test_hand_is_soft_bust(self):
        """Test soft hand becomes hard when bust."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=10, suit="♠"))  # 10
        hand.add_card(Card(rank=10, suit="♦"))  # 10
        assert hand.is_soft is False

    def test_hand_is_blackjack(self):
        """Test blackjack detection."""
        hand = Hand()
        hand.add_card(Card(rank=14, suit="♥"))  # Ace
        hand.add_card(Card(rank=10, suit="♠"))  # 10
        assert hand.is_blackjack is True

    def test_hand_is_bust(self):
        """Test bust detection."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=10, suit="♠"))
        hand.add_card(Card(rank=10, suit="♦"))
        assert hand.is_bust is True

    def test_hand_is_pair(self):
        """Test pair detection."""
        hand = Hand()
        hand.add_card(Card(rank=7, suit="♥"))
        hand.add_card(Card(rank=7, suit="♠"))
        assert hand.is_pair is True

    def test_hand_pair_rank(self):
        """Test pair rank extraction."""
        hand = Hand()
        hand.add_card(Card(rank=7, suit="♥"))
        hand.add_card(Card(rank=7, suit="♠"))
        assert hand.pair_rank == 7

    def test_hand_to_dict(self):
        """Test hand serialization."""
        hand = Hand()
        hand.add_card(Card(rank=10, suit="♥"))
        hand.add_card(Card(rank=7, suit="♠"))
        hand_dict = hand.to_dict()
        assert len(hand_dict["cards"]) == 2
        assert hand_dict["total"] == 17


class TestBlackjackResult:
    """Tests for BlackjackResult enum."""

    def test_result_values(self):
        """Test result values."""
        assert BlackjackResult.WIN.value == 1.0
        assert BlackjackResult.BLACKJACK.value == 1.5
        assert BlackjackResult.PUSH.value == 0.0
        assert BlackjackResult.LOSS.value == -1.0
        assert BlackjackResult.BUST.value == -1.0
        assert BlackjackResult.SURRENDER.value == -0.5

    def test_result_names(self):
        """Test result names."""
        assert BlackjackResult.WIN.name == "WIN"
        assert BlackjackResult.BLACKJACK.name == "BLACKJACK"
        assert BlackjackResult.PUSH.name == "PUSH"
        assert BlackjackResult.LOSS.name == "LOSS"
        assert BlackjackResult.BUST.name == "BUST"
        assert BlackjackResult.SURRENDER.name == "SURRENDER"


class TestBlackjackResultData:
    """Tests for BlackjackResultData dataclass."""

    def test_result_data_creation(self):
        """Test creating result data."""
        data = BlackjackResultData(
            outcome=BlackjackResult.WIN,
            bet=10,
            payout=10,
            net_result=10
        )
        assert data.outcome == BlackjackResult.WIN
        assert data.bet == 10
        assert data.payout == 10
        assert data.net_result == 10

    def test_result_data_to_dict(self):
        """Test result data serialization."""
        data = BlackjackResultData(
            outcome=BlackjackResult.WIN,
            bet=10,
            payout=10,
            net_result=10
        )
        data_dict = data.to_dict()
        assert data_dict["outcome"] == "WIN"
        assert data_dict["bet"] == 10
        assert data_dict["payout"] == 10
        assert data_dict["net_result"] == 10


class TestSimulatorStats:
    """Tests for SimulatorStats class."""

    def test_stats_creation(self):
        """Test creating stats."""
        stats = SimulatorStats()
        assert stats.total_episodes == 0
        assert stats.total_wins == 0
        assert stats.total_losses == 0
        assert stats.total_pushes == 0
        assert stats.total_blackjacks == 0
        assert stats.total_busts == 0
        assert stats.total_surrenders == 0

    def test_stats_update(self):
        """Test updating stats with results."""
        stats = SimulatorStats()
        
        stats.update(BlackjackResult.WIN, bet=10)
        stats.update(BlackjackResult.LOSS, bet=10)
        stats.update(BlackjackResult.PUSH, bet=10)
        stats.update(BlackjackResult.BLACKJACK, bet=10)
        stats.update(BlackjackResult.BUST, bet=10)
        stats.update(BlackjackResult.SURRENDER, bet=10)
        
        assert stats.total_episodes == 6
        assert stats.total_wins == 1
        assert stats.total_losses == 1
        assert stats.total_pushes == 1
        assert stats.total_blackjacks == 1
        assert stats.total_busts == 1
        assert stats.total_surrenders == 1

    def test_stats_win_rate(self):
        """Test win rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.WIN, bet=10)
        
        assert stats.win_rate == 1.0

    def test_stats_loss_rate(self):
        """Test loss rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.LOSS, bet=10)
        
        assert stats.loss_rate == 1.0

    def test_stats_push_rate(self):
        """Test push rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.PUSH, bet=10)
        
        assert stats.push_rate == 1.0

    def test_stats_blackjack_rate(self):
        """Test blackjack rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.BLACKJACK, bet=10)
        
        assert stats.blackjack_rate == 1.0

    def test_stats_bust_rate(self):
        """Test bust rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.BUST, bet=10)
        
        assert stats.bust_rate == 1.0

    def test_stats_surrender_rate(self):
        """Test surrender rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.SURRENDER, bet=10)
        
        assert stats.surrender_rate == 1.0

    def test_stats_roi(self):
        """Test ROI calculation."""
        stats = SimulatorStats()
        
        # 100 wins of 10 units each = 1000 profit
        for _ in range(100):
            stats.update(BlackjackResult.WIN, bet=10)
        
        # ROI = 1000 / 1000 = 1.0 = 100%
        assert stats.roi == 1.0

    def test_stats_roi_negative(self):
        """Test negative ROI calculation."""
        stats = SimulatorStats()
        
        # 100 losses of 10 units each = -1000 profit
        for _ in range(100):
            stats.update(BlackjackResult.LOSS, bet=10)
        
        # ROI = -1000 / 1000 = -1.0 = -100%
        assert stats.roi == -1.0

    def test_stats_roi_mixed(self):
        """Test ROI with mixed results."""
        stats = SimulatorStats()
        
        # 50 wins of 10 units = 500 profit
        for _ in range(50):
            stats.update(BlackjackResult.WIN, bet=10)
        # 50 losses of 10 units = -500 profit
        for _ in range(50):
            stats.update(BlackjackResult.LOSS, bet=10)
        
        # ROI = 0 / 1000 = 0
        assert stats.roi == 0.0

    def test_stats_reset(self):
        """Test resetting stats."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.WIN, bet=10)
        
        stats.reset()
        
        assert stats.total_episodes == 0
        assert stats.total_wins == 0
        assert stats.total_losses == 0

    def test_stats_dict(self):
        """Test converting stats to dict."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.update(BlackjackResult.WIN, bet=10)
        
        d = stats.to_dict()
        
        assert d["total_episodes"] == 100
        assert d["total_wins"] == 100
        assert d["win_rate"] == 1.0
        assert d["roi"] == 1.0


class TestBlackjackGame:
    """Tests for BlackjackGame class."""

    @pytest.fixture
    def game(self):
        """Create a game instance."""
        return BlackjackGame()

    def test_game_creation(self, game):
        """Test creating a game."""
        assert game.deck is not None
        assert game.player_hand is not None
        assert game.dealer_hand is not None
        assert game.status == GameStatus.IDLE

    def test_game_reset(self, game):
        """Test resetting the game."""
        game.reset()
        
        assert game.player_hand is not None
        assert game.dealer_hand is not None
        assert game.status == GameStatus.IDLE
        assert len(game.deck._cards) < 52

    def test_game_deal_initial_cards(self, game):
        """Test dealing initial cards."""
        game.reset()
        game.deal_initial_cards()
        
        assert len(game.player_hand.cards) == 2
        assert len(game.dealer_hand.cards) == 2
        assert game.status == GameStatus.PLAYER_TURN

    def test_game_player_total(self, game):
        """Test player total calculation."""
        game.reset()
        game.deal_initial_cards()
        
        assert 4 <= game.player_hand.total <= 21

    def test_game_dealer_upcard(self, game):
        """Test dealer upcard."""
        game.reset()
        game.deal_initial_cards()
        
        assert 1 <= game.dealer_upcard <= 11

    def test_game_player_hit(self, game):
        """Test player hitting."""
        game.reset()
        game.deal_initial_cards()
        initial_total = game.player_hand.total
        
        game.player_hit()
        
        assert game.player_hand.total >= initial_total

    def test_game_player_stand(self, game):
        """Test player standing."""
        game.reset()
        game.deal_initial_cards()
        
        game.player_stand()
        
        assert game.status == GameStatus.DEALER_TURN

    def test_game_player_double(self, game):
        """Test player doubling."""
        game.reset()
        game.deal_initial_cards()
        
        game.player_double()
        
        assert game.status == GameStatus.DEALER_TURN
        assert game.player_hand.double

    def test_game_player_surrender(self, game):
        """Test player surrendering."""
        game.reset()
        game.deal_initial_cards()
        
        game.player_surrender()
        
        assert game.status == GameStatus.FOLD

    def test_game_dealer_play(self, game):
        """Test dealer playing."""
        game.reset()
        game.deal_initial_cards()
        game.player_stand()
        
        game.dealer_play()
        
        assert game.dealer_hand.stood

    def test_game_determine_result_win(self, game):
        """Test determining a win."""
        game.reset()
        game.deal_initial_cards()
        game.player_hand.total = 21
        game.dealer_hand.total = 18
        
        game.determine_result()
        
        assert game.status == GameStatus.WIN

    def test_game_determine_result_loss(self, game):
        """Test determining a loss."""
        game.reset()
        game.deal_initial_cards()
        game.player_hand.total = 18
        game.dealer_hand.total = 21
        
        game.determine_result()
        
        assert game.status == GameStatus.LOSS

    def test_game_determine_result_push(self, game):
        """Test determining a push."""
        game.reset()
        game.deal_initial_cards()
        game.player_hand.total = 20
        game.dealer_hand.total = 20
        
        game.determine_result()
        
        assert game.status == GameStatus.PUSH

    def test_game_determine_result_blackjack(self, game):
        """Test determining a blackjack."""
        game.reset()
        game.deal_initial_cards()
        game.player_hand.total = 21
        game.player_hand.blackjack = True
        game.dealer_hand.total = 18
        
        game.determine_result()
        
        assert game.status == GameStatus.BLACKJACK

    def test_game_determine_result_bust(self, game):
        """Test determining a bust."""
        game.reset()
        game.deal_initial_cards()
        game.player_hand.total = 22
        game.dealer_hand.total = 18
        
        game.determine_result()
        
        assert game.status == GameStatus.BUST

    def test_game_play_round(self, game):
        """Test playing a complete round."""
        game.reset()
        game.play_round()
        
        assert game.status in [GameStatus.WIN, GameStatus.LOSS, GameStatus.PUSH, 
                               GameStatus.BUST, GameStatus.BLACKJACK, GameStatus.FOLD]

    def test_game_play_round_bust(self, game):
        """Test round where player busts."""
        game.reset()
        game.deal_initial_cards()
        
        # Force player to bust
        game.player_hand.cards = [
            Card(rank=10, suit="hearts"),
            Card(rank=10, suit="spades"),
            Card(rank=3, suit="clubs"),
        ]
        game.player_hand._total = 23
        
        game.play_round()
        
        assert game.status == GameStatus.BUST

    def test_game_play_round_surrender(self, game):
        """Test round where player surrenders."""
        game.reset()
        game.deal_initial_cards()
        
        game.player_surrender()
        game.play_round()
        
        assert game.status == GameStatus.FOLD


class TestGameStatus:
    """Tests for GameStatus enum."""

    def test_status_values(self):
        """Test status values."""
        assert GameStatus.IDLE.value == "IDLE"
        assert GameStatus.PLAYER_TURN.value == "PLAYER_TURN"
        assert GameStatus.DEALER_TURN.value == "DEALER_TURN"
        assert GameStatus.WIN.value == "WIN"
        assert GameStatus.LOSS.value == "LOSS"
        assert GameStatus.PUSH.value == "PUSH"
        assert GameStatus.BUST.value == "BUST"
        assert GameStatus.BLACKJACK.value == "BLACKJACK"
        assert GameStatus.FOLD.value == "FOLD"


class TestIntegration:
    """Integration tests for complete game flow."""

    def test_complete_game_flow(self):
        """Test complete game flow from deal to result."""
        game = BlackjackGame()
        
        # Reset and deal
        game.reset()
        game.deal_initial_cards()
        
        assert game.status == GameStatus.PLAYER_TURN
        assert len(game.player_hand.cards) == 2
        assert len(game.dealer_hand.cards) == 2
        
        # Player stands
        game.player_stand()
        assert game.status == GameStatus.DEALER_TURN
        
        # Dealer plays
        game.dealer_play()
        assert game.dealer_hand.stood
        
        # Determine result
        game.determine_result()
        assert game.status in [GameStatus.WIN, GameStatus.LOSS, GameStatus.PUSH,
                               GameStatus.BUST, GameStatus.BLACKJACK, GameStatus.FOLD]

    def test_player_bust_flow(self):
        """Test player busting during their turn."""
        game = BlackjackGame()
        
        game.reset()
        game.deal_initial_cards()
        
        # Force player to have 22
        game.player_hand.cards = [
            Card(rank=10, suit="hearts"),
            Card(rank=10, suit="spades"),
            Card(rank=2, suit="clubs"),
        ]
        game.player_hand._total = 22
        
        # Player hits (should bust)
        game.player_hit()
        
        assert game.player_hand.is_bust is True
        assert game.status == GameStatus.BUST

    def test_blackjack_flow(self):
        """Test natural blackjack flow."""
        game = BlackjackGame()
        
        game.reset()
        game.deal_initial_cards()
        
        # Force player blackjack
        game.player_hand.cards = [
            Card(rank=14, suit="hearts"),  # Ace
            Card(rank=10, suit="spades"),  # 10
        ]
        game.player_hand._total = 21
        game.player_hand.blackjack = True
        
        # Player stands
        game.player_stand()
        
        # Dealer plays
        game.dealer_play()
        
        # Determine result
        game.determine_result()
        
        assert game.status == GameStatus.BLACKJACK

    def test_stats_tracking(self):
        """Test that stats are properly tracked during game."""
        game = BlackjackGame()
        stats = SimulatorStats()
        
        for _ in range(100):
            game.reset()
            game.play_round()
            stats.update(game.result.outcome, bet=10)
        
        assert stats.total_episodes == 100
        assert stats.total_episodes == stats.total_wins + stats.total_losses + \
               stats.total_pushes + stats.total_blackjacks + \
               stats.total_busts + stats.total_surrenders
