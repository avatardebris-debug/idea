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
)
from advantage_cardgames.trainers.blackjack_training import (
    BlackjackMonteCarloTrainer,
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
        assert Action.HIT.value == 1
        assert Action.STAND.value == 2
        assert Action.DOUBLE.value == 3
        assert Action.SURRENDER.value == 4


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
        assert estimator.get_action_value(state, Action.HIT) == 1.0

        estimator.update(state, Action.HIT, 2.0)
        assert estimator.get_action_value(state, Action.HIT) == 1.5

    def test_estimator_get_best_action(self):
        """Test best action selection."""
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
        """Test estimator statistics."""
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

    def test_policy_exploration(self):
        """Test policy exploration."""
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

    def test_policy_exploitation(self):
        """Test policy exploitation."""
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
        """Test epsilon decay."""
        policy = EpsilonGreedyPolicy(epsilon=0.5, epsilon_decay=0.9)
        initial_epsilon = policy.epsilon
        policy.decay()
        assert policy.epsilon < initial_epsilon


class TestBlackjackMonteCarloTrainer:
    """Tests for BlackjackMonteCarloTrainer class."""

    def test_trainer_creation(self):
        """Test trainer creation."""
        trainer = BlackjackMonteCarloTrainer(seed=42)
        assert trainer.epsilon == 0.1
        assert trainer.total_episodes == 0

    def test_trainer_train_episode(self):
        """Test single episode training."""
        trainer = BlackjackMonteCarloTrainer(seed=42)
        episode, reward = trainer.train_episode()
        assert isinstance(episode, Episode)
        assert isinstance(reward, float)

    def test_trainer_train(self):
        """Test training loop."""
        trainer = BlackjackMonteCarloTrainer(seed=42)
        stats = trainer.train(num_episodes=10, verbose=False)

        assert stats["total_episodes"] == 10
        assert "avg_reward" in stats
        assert "states_learned" in stats

    def test_trainer_evaluate(self):
        """Test evaluation."""
        trainer = BlackjackMonteCarloTrainer(seed=42)
        trainer.train(num_episodes=100, verbose=False)

        eval_stats = trainer.evaluate(num_episodes=10)
        assert eval_stats["total_episodes"] == 10
        assert "avg_reward" in eval_stats
        assert "win_rate" in eval_stats

    def test_trainer_get_action_values(self):
        """Test action value retrieval."""
        trainer = BlackjackMonteCarloTrainer(seed=42)
        trainer.train(num_episodes=100, verbose=False)

        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )

        action_values = trainer.get_action_values(state)
        assert isinstance(action_values, dict)

    def test_trainer_save_load(self, tmp_path):
        """Test save and load."""
        trainer = BlackjackMonteCarloTrainer(seed=42)
        trainer.train(num_episodes=10, verbose=False)

        filepath = tmp_path / "trainer.json"
        trainer.save(str(filepath))

        loaded_trainer = BlackjackMonteCarloTrainer.load(str(filepath))
        assert loaded_trainer.total_episodes == trainer.total_episodes
        assert abs(loaded_trainer.epsilon - trainer.epsilon) < 0.001

    def test_trainer_get_available_actions(self):
        """Test available actions retrieval."""
        trainer = BlackjackMonteCarloTrainer(seed=42)

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


class TestIntegration:
    """Integration tests for Monte Carlo training."""

    def test_full_training_loop(self):
        """Test complete training and evaluation."""
        trainer = BlackjackMonteCarloTrainer(
            seed=42,
            epsilon=0.1,
            epsilon_decay=0.995,
            epsilon_min=0.01,
        )

        # Train
        train_stats = trainer.train(num_episodes=100, verbose=False)
        assert train_stats["total_episodes"] == 100

        # Evaluate
        eval_stats = trainer.evaluate(num_episodes=50)
        assert eval_stats["total_episodes"] == 50

        # Check that we learned something
        assert train_stats["states_learned"] > 0

    def test_policy_improvement(self):
        """Test that policy improves with training."""
        trainer = BlackjackMonteCarloTrainer(seed=42)

        # Initial evaluation
        initial_stats = trainer.evaluate(num_episodes=100)

        # Train
        trainer.train(num_episodes=500, verbose=False)

        # Final evaluation
        final_stats = trainer.evaluate(num_episodes=100)

        # Check that we learned something
        assert final_stats["states_learned"] > initial_stats["states_learned"]

    def test_epsilon_decay(self):
        """Test that epsilon decays properly."""
        trainer = BlackjackMonteCarloTrainer(
            seed=42,
            epsilon=0.5,
            epsilon_decay=0.9,
            epsilon_min=0.01,
        )

        initial_epsilon = trainer.epsilon
        trainer.train(num_episodes=10, verbose=False)
        final_epsilon = trainer.epsilon

        assert final_epsilon < initial_epsilon
        assert final_epsilon >= trainer.policy.min_epsilon


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
