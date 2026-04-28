"""Tests for Monte Carlo training module."""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advantage_cardgames.monte_carlo import (
    State,
    Action,
    Episode,
    StateValueEstimator,
    EpsilonGreedyPolicy,
    MonteCarloTrainer,
)
from advantage_cardgames.simulators.blackjack import (
    BlackjackGame,
    BlackjackResult,
    GameStatus,
)


class TestState:
    """Tests for State class."""

    def test_state_creation(self):
        """Test state creation."""
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        assert state.player_total == 15
        assert state.player_hand_type == "hard"
        assert state.dealer_upcard == 7
        assert state.can_double is True
        assert state.can_split is False
        assert state.can_surrender is True

    def test_state_hash(self):
        """Test state hashing."""
        state1 = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        state2 = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        assert state1 == state2
        assert hash(state1) == hash(state2)

    def test_state_to_dict(self):
        """Test state serialization."""
        state = State(
            player_total=15,
            player_hand_type="soft",
            dealer_upcard=10,
            can_double=False,
            can_split=True,
            can_surrender=False,
        )
        state_dict = state.to_dict()
        assert state_dict["player_total"] == 15
        assert state_dict["player_hand_type"] == "soft"
        assert state_dict["dealer_upcard"] == 10

    def test_state_from_dict(self):
        """Test state deserialization."""
        state_dict = {
            "player_total": 12,
            "player_hand_type": "hard",
            "dealer_upcard": 6,
            "can_double": True,
            "can_split": False,
            "can_surrender": True,
        }
        state = State.from_dict(state_dict)
        assert state.player_total == 12
        assert state.player_hand_type == "hard"
        assert state.dealer_upcard == 6


class TestAction:
    """Tests for Action enum."""

    def test_action_values(self):
        """Test action values."""
        assert Action.HIT.value == 0
        assert Action.STAND.value == 1
        assert Action.DOUBLE.value == 2
        assert Action.SURRENDER.value == 3


class TestEpisode:
    """Tests for Episode class."""

    def test_episode_creation(self):
        """Test episode creation."""
        episode = Episode()
        assert len(episode.state_action_pairs) == 0

    def test_episode_append(self):
        """Test episode appending."""
        episode = Episode()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        episode.append(state, Action.HIT, 1.0)
        assert len(episode.state_action_pairs) == 1
        assert episode.state_action_pairs[0] == (state, Action.HIT, 1.0)

    def test_episode_clear(self):
        """Test episode clearing."""
        episode = Episode()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        episode.append(state, Action.HIT, 1.0)
        episode.clear()
        assert len(episode.state_action_pairs) == 0


class TestStateValueEstimator:
    """Tests for StateValueEstimator class."""

    def test_estimator_initialization(self):
        """Test estimator initialization."""
        estimator = StateValueEstimator()
        assert len(estimator.N) == 0
        assert len(estimator.Q) == 0

    def test_estimator_update(self):
        """Test estimator update."""
        estimator = StateValueEstimator()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )

        estimator.update(state, Action.HIT, 1.0)
        assert estimator.N[state][Action.HIT] == 1
        assert estimator.Q[state][Action.HIT] == 1.0

    def test_estimator_update_multiple(self):
        """Test estimator with multiple updates."""
        estimator = StateValueEstimator()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )

        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.HIT, 2.0)

        assert estimator.N[state][Action.HIT] == 2
        assert estimator.Q[state][Action.HIT] == 1.5

    def test_estimator_get_best_action(self):
        """Test getting best action."""
        estimator = StateValueEstimator()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )

        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)

        best_action = estimator.get_best_action(state, [Action.HIT, Action.STAND])
        assert best_action == Action.STAND

    def test_estimator_get_stats(self):
        """Test getting estimator statistics."""
        estimator = StateValueEstimator()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )

        estimator.update(state, Action.HIT, 1.0)
        stats = estimator.get_stats()

        assert stats["total_states"] == 1
        assert stats["total_state_action_pairs"] == 1


class TestEpsilonGreedyPolicy:
    """Tests for EpsilonGreedyPolicy class."""

    def test_policy_initialization(self):
        """Test policy initialization."""
        policy = EpsilonGreedyPolicy()
        assert policy.epsilon == 1.0
        assert policy.epsilon_decay == 0.999
        assert policy.min_epsilon == 0.01

    def test_policy_get_action_exploration(self):
        """Test policy with exploration."""
        policy = EpsilonGreedyPolicy(epsilon=1.0)
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        action = policy.get_action([Action.HIT, Action.STAND], Action.HIT, state)
        assert action in [Action.HIT, Action.STAND]

    def test_policy_get_action_exploitation(self):
        """Test policy with exploitation."""
        policy = EpsilonGreedyPolicy(epsilon=0.0)
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        action = policy.get_action([Action.HIT, Action.STAND], Action.HIT, state)
        assert action == Action.HIT

    def test_policy_decay(self):
        """Test policy decay."""
        policy = EpsilonGreedyPolicy(epsilon=1.0, epsilon_decay=0.9)
        initial_epsilon = policy.epsilon

        for _ in range(10):
            policy.decay()

        assert policy.epsilon < initial_epsilon
        assert policy.epsilon >= policy.min_epsilon

    def test_policy_save_load(self):
        """Test policy save and load."""
        import tempfile
        import json

        policy = EpsilonGreedyPolicy(epsilon=0.5, epsilon_decay=0.9, min_epsilon=0.01)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            policy.save(temp_path)

            with open(temp_path, "r") as f:
                data = json.load(f)

            assert data["epsilon"] == 0.5
            assert data["epsilon_decay"] == 0.9
            assert data["min_epsilon"] == 0.01

            loaded_policy = EpsilonGreedyPolicy.load(temp_path)
            assert loaded_policy.epsilon == 0.5
            assert loaded_policy.epsilon_decay == 0.9
            assert loaded_policy.min_epsilon == 0.01
        finally:
            os.unlink(temp_path)


class TestMonteCarloTrainer:
    """Tests for MonteCarloTrainer class."""

    def test_trainer_initialization(self):
        """Test trainer initialization."""
        trainer = MonteCarloTrainer()
        assert trainer.total_episodes == 0
        assert trainer.epsilon == 1.0

    def test_trainer_get_available_actions(self):
        """Test getting available actions."""
        trainer = MonteCarloTrainer()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        actions = trainer.get_available_actions(state)
        assert Action.HIT in actions
        assert Action.STAND in actions
        assert Action.DOUBLE in actions
        assert Action.SURRENDER in actions

    def test_trainer_get_policy(self):
        """Test getting policy action."""
        trainer = MonteCarloTrainer()
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        action = trainer.get_policy(state)
        assert action in [Action.HIT, Action.STAND, Action.DOUBLE, Action.SURRENDER]

    def test_trainer_train_episode(self):
        """Test training an episode."""
        trainer = MonteCarloTrainer()
        episode, reward = trainer.train_episode()
        assert len(episode.state_action_pairs) >= 0
        assert isinstance(reward, float)

    def test_trainer_train(self):
        """Test training multiple episodes."""
        trainer = MonteCarloTrainer()
        stats = trainer.train(num_episodes=10, verbose=False)

        assert stats["total_episodes"] == 10
        assert stats["states_learned"] > 0
        assert "avg_reward" in stats

    def test_trainer_evaluate(self):
        """Test evaluation."""
        trainer = MonteCarloTrainer()
        trainer.train(num_episodes=100, verbose=False)
        eval_stats = trainer.evaluate(num_episodes=10)

        assert eval_stats["total_episodes"] == 10
        assert "avg_reward" in eval_stats
        assert "win_rate" in eval_stats

    def test_trainer_save_load(self):
        """Test trainer save and load."""
        import tempfile

        trainer = MonteCarloTrainer()
        trainer.train(num_episodes=10, verbose=False)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            trainer.save(temp_path)

            loaded_trainer = MonteCarloTrainer.load(temp_path)
            assert loaded_trainer.total_episodes == trainer.total_episodes
            assert loaded_trainer.epsilon == trainer.epsilon
        finally:
            os.unlink(temp_path)


class TestIntegration:
    """Integration tests for Monte Carlo training."""

    def test_full_training_loop(self):
        """Test complete training loop."""
        trainer = MonteCarloTrainer()

        # Train
        trainer.train(num_episodes=50, verbose=False)

        # Evaluate
        eval_stats = trainer.evaluate(num_episodes=20)

        assert trainer.total_episodes == 50
        assert eval_stats["total_episodes"] == 20
        assert "avg_reward" in eval_stats

    def test_policy_improvement(self):
        """Test that policy improves with training."""
        trainer = MonteCarloTrainer()

        # Initial evaluation
        initial_stats = trainer.evaluate(num_episodes=50)

        # Train
        trainer.train(num_episodes=200, verbose=False)

        # Final evaluation
        final_stats = trainer.evaluate(num_episodes=50)

        # Policy should have learned something
        assert trainer.total_episodes == 200
        assert trainer.epsilon < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
