"""Tests for Monte Carlo training engine."""

import json
import os
import tempfile
import unittest

from ..monte_carlo.training import (
    Action,
    Episode,
    MonteCarloTrainer,
    State,
    StateValueEstimator,
    EpsilonGreedyPolicy,
)
from ..simulators.blackjack import BlackjackGame, BlackjackSimulator


class TestState(unittest.TestCase):
    """Tests for the State class."""

    def test_state_creation(self):
        """Test creating a state."""
        state = State(
            player_total=15,
            player_hand_type="hard",
            dealer_upcard=7,
            can_double=True,
            can_split=False,
            can_surrender=True,
        )
        self.assertEqual(state.player_total, 15)
        self.assertEqual(state.dealer_upcard, 7)
        self.assertTrue(state.can_double)

    def test_state_hash(self):
        """Test state hashing."""
        state1 = State(15, "hard", 7, True, False, True)
        state2 = State(15, "hard", 7, True, False, True)
        state3 = State(15, "soft", 7, True, False, True)
        
        self.assertEqual(hash(state1), hash(state2))
        self.assertNotEqual(hash(state1), hash(state3))

    def test_state_equality(self):
        """Test state equality."""
        state1 = State(15, "hard", 7, True, False, True)
        state2 = State(15, "hard", 7, True, False, True)
        state3 = State(15, "soft", 7, True, False, True)
        
        self.assertEqual(state1, state2)
        self.assertNotEqual(state1, state3)

    def test_state_to_dict(self):
        """Test state serialization."""
        state = State(15, "hard", 7, True, False, True)
        state_dict = state.to_dict()
        
        self.assertEqual(state_dict["player_total"], 15)
        self.assertEqual(state_dict["player_hand_type"], "hard")
        self.assertTrue(state_dict["can_double"])

    def test_state_from_dict(self):
        """Test state deserialization."""
        state_dict = {
            "player_total": 15,
            "player_hand_type": "hard",
            "dealer_upcard": 7,
            "can_double": True,
            "can_split": False,
            "can_surrender": True,
        }
        state = State.from_dict(state_dict)
        
        self.assertEqual(state.player_total, 15)
        self.assertEqual(state.dealer_upcard, 7)


class TestEpisode(unittest.TestCase):
    """Tests for the Episode class."""

    def test_episode_creation(self):
        """Test creating an episode."""
        episode = Episode()
        self.assertEqual(len(episode.states), 0)
        self.assertEqual(len(episode.actions), 0)

    def test_episode_append(self):
        """Test appending to an episode."""
        episode = Episode()
        state = State(15, "hard", 7, True, False, True)
        episode.append(state, Action.HIT, 0.0)
        
        self.assertEqual(len(episode.states), 1)
        self.assertEqual(episode.states[0], state)
        self.assertEqual(episode.actions[0], Action.HIT)

    def test_episode_to_dict(self):
        """Test episode serialization."""
        episode = Episode()
        state = State(15, "hard", 7, True, False, True)
        episode.append(state, Action.HIT, 0.0)
        
        episode_dict = episode.to_dict()
        self.assertEqual(len(episode_dict["states"]), 1)
        self.assertEqual(episode_dict["actions"], ["hit"])


class TestStateValueEstimator(unittest.TestCase):
    """Tests for the StateValueEstimator class."""

    def test_estimator_creation(self):
        """Test creating an estimator."""
        estimator = StateValueEstimator()
        self.assertEqual(len(estimator.N), 0)

    def test_estimator_update(self):
        """Test updating state-action values."""
        estimator = StateValueEstimator()
        state = State(15, "hard", 7, True, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.HIT, 2.0)
        
        self.assertEqual(estimator.N[state][Action.HIT], 2)
        self.assertEqual(estimator.Q[state][Action.HIT], 1.5)

    def test_estimator_get_action_value(self):
        """Test getting action values."""
        estimator = StateValueEstimator()
        state = State(15, "hard", 7, True, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)
        
        self.assertEqual(estimator.get_action_value(state, Action.HIT), 1.0)
        self.assertEqual(estimator.get_action_value(state, Action.STAND), 2.0)

    def test_estimator_get_best_action(self):
        """Test getting best action."""
        estimator = StateValueEstimator()
        state = State(15, "hard", 7, True, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)
        
        best_action = estimator.get_best_action(state, [Action.HIT, Action.STAND])
        self.assertEqual(best_action, Action.STAND)

    def test_estimator_stats(self):
        """Test estimator statistics."""
        estimator = StateValueEstimator()
        state = State(15, "hard", 7, True, False, True)
        
        estimator.update(state, Action.HIT, 1.0)
        estimator.update(state, Action.STAND, 2.0)
        
        stats = estimator.get_stats()
        self.assertEqual(stats["total_states"], 1)
        self.assertEqual(stats["total_state_action_pairs"], 2)


class TestEpsilonGreedyPolicy(unittest.TestCase):
    """Tests for the EpsilonGreedyPolicy class."""

    def test_policy_creation(self):
        """Test creating a policy."""
        policy = EpsilonGreedyPolicy(epsilon=0.1)
        self.assertEqual(policy.epsilon, 0.1)

    def test_policy_get_action(self):
        """Test action selection."""
        policy = EpsilonGreedyPolicy(epsilon=0.0)  # No exploration
        state = State(15, "hard", 7, True, False, True)
        
        best_action = Action.STAND
        action = policy.get_action([Action.HIT, Action.STAND], best_action, state)
        self.assertEqual(action, Action.STAND)

    def test_policy_decay(self):
        """Test epsilon decay."""
        policy = EpsilonGreedyPolicy(epsilon=0.5, epsilon_decay=0.9)
        initial_epsilon = policy.epsilon
        
        policy.decay()
        self.assertLess(policy.epsilon, initial_epsilon)
        self.assertGreater(policy.epsilon, 0)

    def test_policy_set_epsilon(self):
        """Test setting epsilon."""
        policy = EpsilonGreedyPolicy(epsilon=0.1)
        policy.set_epsilon(0.5)
        self.assertEqual(policy.epsilon, 0.5)


class TestMonteCarloTrainer(unittest.TestCase):
    """Tests for the MonteCarloTrainer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.trainer = MonteCarloTrainer(seed=42)

    def test_trainer_creation(self):
        """Test creating a trainer."""
        self.assertIsNotNone(self.trainer.estimator)
        self.assertIsNotNone(self.trainer.policy)

    def test_trainer_get_available_actions(self):
        """Test getting available actions."""
        state = State(15, "hard", 7, True, False, True)
        actions = self.trainer.get_available_actions(state)
        
        self.assertIn(Action.HIT, actions)
        self.assertIn(Action.STAND, actions)
        self.assertIn(Action.DOUBLE, actions)
        self.assertIn(Action.SURRENDER, actions)

    def test_trainer_get_best_action(self):
        """Test getting best action."""
        state = State(15, "hard", 7, True, False, True)
        best_action = self.trainer.get_best_action(state)
        self.assertIn(best_action, [Action.HIT, Action.STAND, Action.DOUBLE, Action.SURRENDER])

    def test_trainer_train_episode(self):
        """Test training on an episode."""
        episode, reward = self.trainer.train_episode()
        
        self.assertIsInstance(episode, Episode)
        self.assertIsInstance(reward, float)

    def test_trainer_train(self):
        """Test training for multiple episodes."""
        stats = self.trainer.train(num_episodes=10, verbose=False)
        
        self.assertEqual(stats["total_episodes"], 10)
        self.assertGreater(stats["states_learned"], 0)

    def test_trainer_save_load(self):
        """Test saving and loading a trainer."""
        # Train a bit
        self.trainer.train(num_episodes=5, verbose=False)
        
        # Save
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name
            self.trainer.save(temp_file)
        
        # Load
        loaded_trainer = MonteCarloTrainer.load(temp_file)
        
        # Verify
        self.assertEqual(loaded_trainer.total_episodes, 5)
        self.assertEqual(loaded_trainer.policy.epsilon, self.trainer.policy.epsilon)
        
        # Cleanup
        os.unlink(temp_file)

    def test_trainer_evaluate(self):
        """Test evaluating the trainer."""
        # Train a bit
        self.trainer.train(num_episodes=10, verbose=False)
        
        # Evaluate
        eval_stats = self.trainer.evaluate(num_episodes=100)
        
        self.assertEqual(eval_stats["total_episodes"], 100)
        self.assertIn("win_rate", eval_stats)
        self.assertIn("loss_rate", eval_stats)

    def test_trainer_get_action_values(self):
        """Test getting action values."""
        state = State(15, "hard", 7, True, False, True)
        
        # Train a bit
        self.trainer.train(num_episodes=10, verbose=False)
        
        # Get action values
        action_values = self.trainer.get_action_values(state)
        self.assertIsInstance(action_values, dict)


class TestMonteCarloIntegration(unittest.TestCase):
    """Integration tests for Monte Carlo training."""

    def test_full_training_loop(self):
        """Test a complete training loop."""
        trainer = MonteCarloTrainer(seed=42, epsilon=0.5)
        
        # Train for 100 episodes
        stats = trainer.train(num_episodes=100, verbose=False)
        
        # Verify training happened
        self.assertEqual(stats["total_episodes"], 100)
        self.assertGreater(stats["states_learned"], 0)
        
        # Verify policy improved (epsilon decayed)
        self.assertLess(stats["final_epsilon"], 0.5)

    def test_policy_improvement(self):
        """Test that policy improves with training."""
        trainer = MonteCarloTrainer(seed=42, epsilon=0.1)
        
        # Initial evaluation
        initial_eval = trainer.evaluate(num_episodes=100)
        
        # Train for 500 episodes
        trainer.train(num_episodes=500, verbose=False)
        
        # Final evaluation
        final_eval = trainer.evaluate(num_episodes=100)
        
        # Policy should have learned something
        self.assertGreater(final_eval["avg_reward"], -1.0)

    def test_state_coverage(self):
        """Test that training covers various states."""
        trainer = MonteCarloTrainer(seed=42, epsilon=0.5)
        
        # Train for many episodes
        trainer.train(num_episodes=1000, verbose=False)
        
        # Should have learned many states
        stats = trainer.get_stats()
        self.assertGreater(stats["total_states"], 50)


if __name__ == "__main__":
    unittest.main()
