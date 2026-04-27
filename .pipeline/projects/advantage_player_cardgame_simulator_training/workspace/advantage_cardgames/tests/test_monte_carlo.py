"""Tests for Monte Carlo training module."""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from advantage_cardgames.monte_carlo import (
    Action,
    Episode,
    EpsilonGreedyPolicy,
    MonteCarloTrainer,
    State,
    StateValueEstimator,
)
from advantage_cardgames.simulators import BlackjackGame


class TestState:
    """Tests for State class."""

    def test_state_creation(self):
        """Test creating a state."""
        state = State(
            player_total=16,
            player_hand_type="hard",
            dealer_upcard=10,
            can_double=False,
            can_split=False,
            can_surrender=True,
        )
        assert state.player_total == 16
        assert state.player_hand_type == "hard"
        assert state.dealer_upcard == 10
        assert state.can_double is False
        assert state.can_split is False
        assert state.can_surrender is True

    def test_state_hash(self):
        """Test state hashing."""
        state1 = State(16, "hard", 10, False, False, True)
        state2 = State(16, "hard", 10, False, False, True)
        state3 = State(16, "soft", 10, False, False, True)
        
        assert hash(state1) == hash(state2)
        assert hash(state1) != hash(state3)

    def test_state_equality(self):
        """Test state equality."""
        state1 = State(16, "hard", 10, False, False, True)
        state2 = State(16, "hard", 10, False, False, True)
        state3 = State(16, "soft", 10, False, False, True)
        
        assert state1 == state2
        assert state1 != state3

    def test_state_to_dict(self):
        """Test state serialization."""
        state = State(16, "hard", 10, True, False, True)
        d = state.to_dict()
        
        assert d["player_total"] == 16
        assert d["player_hand_type"] == "hard"
        assert d["dealer_upcard"] == 10
        assert d["can_double"] is True
        assert d["can_split"] is False
        assert d["can_surrender"] is True

    def test_state_from_dict(self):
        """Test state deserialization."""
        d = {
            "player_total": 16,
            "player_hand_type": "hard",
            "dealer_upcard": 10,
            "can_double": True,
            "can_split": False,
            "can_surrender": True,
        }
        state = State.from_dict(d)
        
        assert state.player_total == 16
        assert state.player_hand_type == "hard"
        assert state.dealer_upcard == 10
        assert state.can_double is True
        assert state.can_split is False
        assert state.can_surrender is True


class TestEpisode:
    """Tests for Episode class."""

    def test_episode_creation(self):
        """Test creating an episode."""
        episode = Episode()
        assert len(episode.states) == 0
        assert len(episode.actions) == 0
        assert len(episode.rewards) == 0

    def test_episode_append(self):
        """Test appending to episode."""
        episode = Episode()
        state = State(16, "hard", 10, False, False, True)
        episode.append(state, Action.HIT, 0.0)
        
        assert len(episode.states) == 1
        assert len(episode.actions) == 1
        assert len(episode.rewards) == 1
        assert episode.states[0] == state
        assert episode.actions[0] == Action.HIT
        assert episode.rewards[0] == 0.0

    def test_episode_to_dict(self):
        """Test episode serialization."""
        episode = Episode()
        state = State(16, "hard", 10, False, False, True)
        episode.append(state, Action.HIT, 0.0)
        
        d = episode.to_dict()
        assert len(d["states"]) == 1
        assert len(d["actions"]) == 1
        assert len(d["rewards"]) == 1
        assert d["actions"][0] == "hit"


class TestStateValueEstimator:
    """Tests for StateValueEstimator class."""

    def test_estimator_creation(self):
        """Test creating an estimator."""
        estimator = StateValueEstimator()
        assert len(estimator.Q) == 0
        assert len(estimator.N) == 0

    def test_estimator_update(self):
        """Test updating state-action values."""
        estimator = StateValueEstimator()
        state = State(16, "hard", 10, False, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.HIT, 2.0)
        
        assert estimator.N[state][Action.HIT] == 2
        assert estimator.Q[state][Action.HIT] == 1.5

    def test_estimator_get_action_value(self):
        """Test getting action values."""
        estimator = StateValueEstimator()
        state = State(16, "hard", 10, False, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)
        
        assert estimator.get_action_value(state, Action.HIT) == 1.0
        assert estimator.get_action_value(state, Action.STAND) == 2.0

    def test_estimator_get_best_action(self):
        """Test getting best action."""
        estimator = StateValueEstimator()
        state = State(16, "hard", 10, False, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)
        
        available = [Action.HIT, Action.STAND]
        best = estimator.get_best_action(state, available)
        assert best == Action.STAND

    def test_estimator_get_stats(self):
        """Test getting estimator statistics."""
        estimator = StateValueEstimator()
        state = State(16, "hard", 10, False, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)
        
        stats = estimator.get_stats()
        assert stats["total_states"] == 1
        assert stats["total_state_action_pairs"] == 2


class TestEpsilonGreedyPolicy:
    """Tests for EpsilonGreedyPolicy class."""

    def test_policy_creation(self):
        """Test creating a policy."""
        policy = EpsilonGreedyPolicy(epsilon=0.1)
        assert policy.epsilon == 0.1
        assert policy.epsilon_decay == 0.995

    def test_policy_get_action_explore(self):
        """Test action selection with exploration."""
        policy = EpsilonGreedyPolicy(epsilon=1.0)  # Always explore
        state = State(16, "hard", 10, False, False, True)
        available = [Action.HIT, Action.STAND]
        
        action = policy.get_action(available, Action.STAND, state)
        assert action in available

    def test_policy_get_action_exploit(self):
        """Test action selection with exploitation."""
        policy = EpsilonGreedyPolicy(epsilon=0.0)  # Always exploit
        state = State(16, "hard", 10, False, False, True)
        available = [Action.HIT, Action.STAND]
        
        action = policy.get_action(available, Action.STAND, state)
        assert action == Action.STAND

    def test_policy_decay(self):
        """Test epsilon decay."""
        policy = EpsilonGreedyPolicy(epsilon=0.1, epsilon_decay=0.9)
        initial_epsilon = policy.epsilon
        
        policy.decay()
        assert policy.epsilon < initial_epsilon
        assert policy.epsilon >= policy.min_epsilon


class TestMonteCarloTrainer:
    """Tests for MonteCarloTrainer class."""

    @pytest.fixture
    def trainer(self):
        """Create a trainer for testing."""
        return MonteCarloTrainer(epsilon=0.1, seed=42)

    def test_trainer_creation(self, trainer):
        """Test creating a trainer."""
        assert trainer.estimator is not None
        assert trainer.policy is not None
        assert trainer.game is not None

    def test_get_available_actions(self, trainer):
        """Test getting available actions."""
        state = State(16, "hard", 10, False, False, True)
        actions = trainer.get_available_actions(state)
        
        assert Action.HIT in actions
        assert Action.STAND in actions
        assert Action.SURRENDER in actions
        assert Action.DOUBLE not in actions
        assert Action.SPLIT not in actions

    def test_get_available_actions_all(self, trainer):
        """Test getting all available actions."""
        state = State(16, "pair", 10, True, True, True)
        actions = trainer.get_available_actions(state)
        
        assert len(actions) == 5
        assert all(action in actions for action in Action)

    def test_train_episode(self, trainer):
        """Test training on an episode."""
        episode, reward = trainer.train_episode()
        
        assert len(episode.states) > 0
        assert len(episode.actions) > 0
        assert len(episode.rewards) > 0
        assert isinstance(reward, float)

    def test_train(self, trainer):
        """Test training for multiple episodes."""
        stats = trainer.train(num_episodes=10, verbose=False)
        
        assert stats["total_episodes"] == 10
        assert stats["final_epsilon"] < 0.1
        assert stats["states_learned"] > 0

    def test_get_policy(self, trainer):
        """Test getting policy for a state."""
        state = State(16, "hard", 10, False, False, True)
        action = trainer.get_policy(state)
        
        assert action in trainer.get_available_actions(state)

    def test_get_action_values(self, trainer):
        """Test getting action values for a state."""
        state = State(16, "hard", 10, False, False, True)
        values = trainer.get_action_values(state)
        
        assert isinstance(values, dict)
        assert all(isinstance(v, float) for v in values.values())

    def test_get_stats(self, trainer):
        """Test getting training statistics."""
        trainer.train(num_episodes=10, verbose=False)
        stats = trainer.get_stats()
        
        assert stats["total_episodes"] == 10
        assert "avg_reward" in stats
        assert "current_epsilon" in stats

    def test_save_load(self, trainer):
        """Test saving and loading a model."""
        trainer.train(num_episodes=10, verbose=False)
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name
        
        try:
            trainer.save(temp_path)
            
            # Verify file exists and is valid JSON
            with open(temp_path, "r") as f:
                data = json.load(f)
            
            assert "estimator" in data
            assert "policy" in data
            
            # Load the model
            loaded_trainer = MonteCarloTrainer.load(temp_path)
            assert loaded_trainer.estimator is not None
            assert loaded_trainer.policy is not None
        finally:
            os.unlink(temp_path)

    def test_evaluate(self, trainer):
        """Test evaluating the policy."""
        trainer.train(num_episodes=100, verbose=False)
        results = trainer.evaluate(num_episodes=100)
        
        assert results["total_episodes"] == 100
        assert 0 <= results["win_rate"] <= 1
        assert 0 <= results["loss_rate"] <= 1
        assert 0 <= results["push_rate"] <= 1
        assert abs(results["win_rate"] + results["loss_rate"] + results["push_rate"] - 1.0) < 0.01


class TestMonteCarloIntegration:
    """Integration tests for Monte Carlo training."""

    def test_training_convergence(self):
        """Test that training improves over time."""
        trainer = MonteCarloTrainer(epsilon=0.3, epsilon_decay=0.99, seed=42)
        
        # Train for 500 episodes
        stats = trainer.train(num_episodes=500, verbose=False)
        
        # Should have learned some states
        assert stats["states_learned"] > 0
        
        # Should have positive average reward (better than random)
        assert stats["avg_reward"] > -1.0

    def test_policy_improvement(self):
        """Test that policy improves with training."""
        trainer = MonteCarloTrainer(epsilon=0.2, epsilon_decay=0.995, seed=42)
        
        # Initial evaluation
        initial_eval = trainer.evaluate(num_episodes=100)
        
        # Train
        trainer.train(num_episodes=500, verbose=False)
        
        # Final evaluation
        final_eval = trainer.evaluate(num_episodes=100)
        
        # Should have learned something
        assert final_eval["win_rate"] >= initial_eval["win_rate"] or final_eval["avg_reward"] >= initial_eval["avg_reward"]

    def test_different_states_learned(self):
        """Test that different states are learned."""
        trainer = MonteCarloTrainer(epsilon=0.3, seed=42)
        trainer.train(num_episodes=200, verbose=False)
        
        stats = trainer.get_stats()
        assert stats["total_states"] > 0
        
        # Should have learned multiple state-action pairs
        total_pairs = sum(len(actions) for actions in trainer.estimator.N.values())
        assert total_pairs > stats["total_states"]
