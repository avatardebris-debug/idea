"""Tests for simulator module."""

import pytest

from advantage_cardgames.simulators import (
    BlackjackGame,
    BlackjackResult,
    SimulatorStats,
)


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
        assert game.result is None

    def test_reset(self, game):
        """Test resetting the game."""
        game.reset()
        
        assert game.player_hand is not None
        assert game.dealer_hand is not None
        assert game.result is None
        assert len(game.deck.cards) < 52

    def test_deal_initial_cards(self, game):
        """Test dealing initial cards."""
        game.reset()
        
        assert len(game.player_hand.cards) == 2
        assert len(game.dealer_hand.cards) == 2

    def test_player_total(self, game):
        """Test player total calculation."""
        game.reset()
        
        assert 4 <= game.player_hand.total <= 21

    def test_dealer_upcard(self, game):
        """Test dealer upcard."""
        game.reset()
        
        assert 1 <= game.dealer_upcard <= 11

    def test_play_player_turn_hit(self, game):
        """Test player hitting."""
        game.reset()
        initial_total = game.player_hand.total
        
        game.player_hit()
        
        assert game.player_hand.total >= initial_total

    def test_play_player_turn_stand(self, game):
        """Test player standing."""
        game.reset()
        
        game.player_stand()
        
        assert game.player_hand.stood

    def test_play_player_turn_double(self, game):
        """Test player doubling."""
        game.reset()
        
        game.player_double()
        
        assert game.player_hand.stood
        assert game.player_hand.double

    def test_play_player_turn_surrender(self, game):
        """Test player surrendering."""
        game.reset()
        
        game.player_surrender()
        
        assert game.player_hand.surrendered

    def test_play_player_turn_split(self, game):
        """Test player splitting."""
        game.reset()
        
        # Create a pair
        game.player_hand.cards = [game.deck.draw(), game.deck.draw()]
        while game.player_hand.cards[0].rank != game.player_hand.cards[1].rank:
            game.reset()
            game.player_hand.cards = [game.deck.draw(), game.deck.draw()]
        
        game.player_split()
        
        assert game.player_hand.stood
        assert game.player_hand.split

    def test_play_dealer_turn(self, game):
        """Test dealer playing."""
        game.reset()
        
        game.player_stand()
        game.dealer_play()
        
        assert game.dealer_hand.stood

    def test_determine_result_win(self, game):
        """Test determining a win."""
        game.reset()
        game.player_hand.total = 21
        game.dealer_hand.total = 18
        
        result = game.determine_result()
        
        assert result == BlackjackResult.WIN

    def test_determine_result_loss(self, game):
        """Test determining a loss."""
        game.reset()
        game.player_hand.total = 18
        game.dealer_hand.total = 21
        
        result = game.determine_result()
        
        assert result == BlackjackResult.LOSS

    def test_determine_result_push(self, game):
        """Test determining a push."""
        game.reset()
        game.player_hand.total = 20
        game.dealer_hand.total = 20
        
        result = game.determine_result()
        
        assert result == BlackjackResult.PUSH

    def test_determine_result_blackjack(self, game):
        """Test determining a blackjack."""
        game.reset()
        game.player_hand.total = 21
        game.player_hand.blackjack = True
        game.dealer_hand.total = 18
        
        result = game.determine_result()
        
        assert result == BlackjackResult.BLACKJACK

    def test_determine_result_bust(self, game):
        """Test determining a bust."""
        game.reset()
        game.player_hand.total = 22
        game.dealer_hand.total = 18
        
        result = game.determine_result()
        
        assert result == BlackjackResult.BUST

    def test_play_round(self, game):
        """Test playing a complete round."""
        game.reset()
        game.play_round()
        
        assert game.result is not None
        assert game.result in BlackjackResult

    def test_play_round_bust(self, game):
        """Test round where player busts."""
        game.reset()
        
        # Force player to bust
        game.player_hand.cards = [
            type("Card", (), {"rank": 10, "suit": "hearts"})(),
            type("Card", (), {"rank": 10, "suit": "spades"})(),
            type("Card", (), {"rank": 3, "suit": "clubs"})(),
        ]
        game.player_hand._total = 23
        
        game.play_round()
        
        assert game.result == BlackjackResult.BUST

    def test_play_round_surrender(self, game):
        """Test round where player surrenders."""
        game.reset()
        
        game.player_surrender()
        game.play_round()
        
        assert game.result == BlackjackResult.SURRENDER


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

    def test_stats_add(self):
        """Test adding results to stats."""
        stats = SimulatorStats()
        
        stats.add(BlackjackResult.WIN)
        stats.add(BlackjackResult.LOSS)
        stats.add(BlackjackResult.PUSH)
        stats.add(BlackjackResult.BLACKJACK)
        stats.add(BlackjackResult.BUST)
        stats.add(BlackjackResult.SURRENDER)
        
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
            stats.add(BlackjackResult.WIN)
        
        assert stats.win_rate == 1.0

    def test_stats_loss_rate(self):
        """Test loss rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.LOSS)
        
        assert stats.loss_rate == 1.0

    def test_stats_push_rate(self):
        """Test push rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.PUSH)
        
        assert stats.push_rate == 1.0

    def test_stats_blackjack_rate(self):
        """Test blackjack rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.BLACKJACK)
        
        assert stats.blackjack_rate == 1.0

    def test_stats_bust_rate(self):
        """Test bust rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.BUST)
        
        assert stats.bust_rate == 1.0

    def test_stats_surrender_rate(self):
        """Test surrender rate calculation."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.SURRENDER)
        
        assert stats.surrender_rate == 1.0

    def test_stats_avg_reward(self):
        """Test average reward calculation."""
        stats = SimulatorStats()
        
        for _ in range(50):
            stats.add(BlackjackResult.WIN)
        for _ in range(50):
            stats.add(BlackjackResult.LOSS)
        
        # Expected: (50 * 1.0 + 50 * -1.0) / 100 = 0.0
        assert abs(stats.avg_reward) < 0.01

    def test_stats_avg_reward_blackjack(self):
        """Test average reward with blackjacks."""
        stats = SimulatorStats()
        
        for _ in range(50):
            stats.add(BlackjackResult.BLACKJACK)
        for _ in range(50):
            stats.add(BlackjackResult.LOSS)
        
        # Expected: (50 * 1.5 + 50 * -1.0) / 100 = 0.25
        assert abs(stats.avg_reward - 0.25) < 0.01

    def test_stats_reset(self):
        """Test resetting stats."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.WIN)
        
        stats.reset()
        
        assert stats.total_episodes == 0
        assert stats.total_wins == 0

    def test_stats_dict(self):
        """Test converting stats to dict."""
        stats = SimulatorStats()
        
        for _ in range(100):
            stats.add(BlackjackResult.WIN)
        
        d = stats.to_dict()
        
        assert d["total_episodes"] == 100
        assert d["total_wins"] == 100
        assert d["win_rate"] == 1.0
        assert d["avg_reward"] == 1.0
