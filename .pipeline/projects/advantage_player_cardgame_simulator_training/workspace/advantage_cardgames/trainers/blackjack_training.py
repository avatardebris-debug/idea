"""Blackjack Monte Carlo training module.

This module provides Monte Carlo training for blackjack using:
- Epsilon-greedy exploration
- First-visit Monte Carlo estimation
- State-action value tracking
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional
from enum import Enum, auto
import json
import random
from collections import defaultdict

from ..simulators.blackjack import (
    BlackjackGame,
    BlackjackResult,
    GameStatus,
)
from ..monte_carlo import (
    State,
    Action,
    Episode,
    StateValueEstimator,
    EpsilonGreedyPolicy,
)


class BlackjackMonteCarloTrainer:
    """Monte Carlo trainer for blackjack strategy."""

    def __init__(
        self,
        seed: Optional[int] = None,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01,
    ):
        """Initialize trainer.

        Args:
            seed: Random seed for reproducibility
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon value
        """
        self._rng = random.Random(seed)
        self.estimator = StateValueEstimator()
        self.policy = EpsilonGreedyPolicy(
            epsilon=epsilon,
            epsilon_decay=epsilon_decay,
            epsilon_min=epsilon_min,
        )
        self._total_episodes: int = 0
        self._game: Optional[BlackjackGame] = None

    @property
    def epsilon(self) -> float:
        """Get current epsilon value."""
        return self.policy.epsilon

    @property
    def total_episodes(self) -> int:
        """Get total episodes trained."""
        return self._total_episodes

    @total_episodes.setter
    def total_episodes(self, value: int) -> None:
        """Set total episodes."""
        self._total_episodes = value

    def get_available_actions(self, state: State) -> List[Action]:
        """Get available actions for state.

        Args:
            state: Current state

        Returns:
            List of available actions
        """
        available = [Action.HIT, Action.STAND]

        if state.can_double:
            available.append(Action.DOUBLE)

        if state.can_surrender:
            available.append(Action.SURRENDER)

        # Note: SPLIT is not supported in this implementation
        # if state.can_split:
        #     available.append(Action.SPLIT)

        return available

    def get_policy(self, state: State) -> Action:
        """Get policy action for state.

        Args:
            state: Current state

        Returns:
            Selected action
        """
        available_actions = self.get_available_actions(state)
        best_action = self.estimator.get_best_action(state, available_actions)
        return self.policy.get_action(available_actions, best_action, state)

    def train_episode(self) -> Tuple[Episode, float]:
        """Train on a single episode.

        Returns:
            Tuple of (episode, total reward)
        """
        self._game = BlackjackGame(
            num_decks=6,
            dealer_stands_soft_17=True,
        )

        episode = Episode()
        total_reward = 0.0

        # Deal initial cards
        self._game.deal_initial_cards()
        total_reward += self._game.get_result().net_result if self._game.get_result() else 0.0

        if self._game.get_status() != GameStatus.PLAYER_TURN:
            return episode, total_reward

        # Create initial state
        player_hand = self._game.get_player_hand()
        dealer_upcard = self._game.get_dealer_upcard()

        state = State(
            player_total=player_hand.total,
            player_hand_type="soft" if player_hand.is_soft else "hard",
            dealer_upcard=dealer_upcard,
            can_double=player_hand.is_pair,
            can_split=player_hand.is_pair,
            can_surrender=True,
        )

        # Play episode
        while self._game.get_status() == GameStatus.PLAYER_TURN:
            available_actions = self.get_available_actions(state)
            best_action = self.estimator.get_best_action(state, available_actions)
            action = self.policy.get_action(available_actions, best_action, state)

            # Execute action
            if action == Action.HIT:
                self._game.player_hit()
            elif action == Action.STAND:
                self._game.player_stand()
            elif action == Action.DOUBLE:
                self._game.player_double()
            elif action == Action.SURRENDER:
                self._game.player_surrender()
            else:
                raise ValueError(f"Unknown action: {action}")

            # Get result if game ended
            result = self._game.get_result()
            if result:
                total_reward += result.net_result

            # Record state-action-reward
            episode.append(state, action, result.net_result if result else 0.0)

            # Check if episode ended
            if self._game.get_status() in [
                GameStatus.WIN,
                GameStatus.LOSS,
                GameStatus.PUSH,
                GameStatus.BUST,
                GameStatus.BLACKJACK,
                GameStatus.FOLD,
            ]:
                break

            # Update state
            player_hand = self._game.get_player_hand()
            dealer_upcard = self._game.get_dealer_upcard()

            state = State(
                player_total=player_hand.total,
                player_hand_type="soft" if player_hand.is_soft else "hard",
                dealer_upcard=dealer_upcard,
                can_double=player_hand.is_pair,
                can_split=player_hand.is_pair,
                can_surrender=False,
            )

        # Update estimator with episode returns
        self._update_estimator(episode, total_reward)

        return episode, total_reward

    def _update_estimator(self, episode: Episode, total_reward: float) -> None:
        """Update estimator with episode returns.

        Args:
            episode: Episode to process
            total_reward: Total reward from episode
        """
        seen_states: Dict[State, float] = {}

        for state, action, reward in episode.state_action_pairs:
            if state not in seen_states:
                seen_states[state] = 0.0
            seen_states[state] += reward

        for state, action, reward in episode.state_action_pairs:
            if state in seen_states:
                self.estimator.update(state, action, seen_states[state])

    def train(
        self,
        num_episodes: int,
        verbose: bool = True,
    ) -> dict:
        """Train for specified number of episodes.

        Args:
            num_episodes: Number of episodes to train
            verbose: Whether to print progress

        Returns:
            Dictionary of training statistics
        """
        initial_epsilon = self.epsilon
        total_reward = 0.0

        for i in range(num_episodes):
            episode, reward = self.train_episode()
            self.total_episodes += 1
            total_reward += reward

            if verbose and (i + 1) % 100 == 0:
                print(f"Episode {i + 1}/{num_episodes}, "
                      f"Reward: {reward:.2f}, "
                      f"Epsilon: {self.epsilon:.4f}")

            self.policy.decay()

        stats = self.estimator.get_stats()
        stats["total_episodes"] = self.total_episodes
        stats["initial_epsilon"] = initial_epsilon
        stats["final_epsilon"] = self.epsilon
        stats["states_learned"] = stats["total_states"]
        stats["avg_reward"] = total_reward / num_episodes

        return stats

    def evaluate(self, num_episodes: int = 100) -> dict:
        """Evaluate current policy.

        Args:
            num_episodes: Number of episodes to evaluate

        Returns:
            Dictionary of evaluation statistics
        """
        total_reward = 0.0
        wins = 0
        losses = 0
        pushes = 0

        for _ in range(num_episodes):
            episode, reward = self.train_episode()
            total_reward += reward

            # Count outcomes
            if reward > 0:
                wins += 1
            elif reward < 0:
                losses += 1
            else:
                pushes += 1

        return {
            "total_episodes": num_episodes,
            "total_reward": total_reward,
            "avg_reward": total_reward / num_episodes,
            "win_rate": wins / num_episodes,
            "loss_rate": losses / num_episodes,
            "push_rate": pushes / num_episodes,
        }

    def get_action_values(self, state: State) -> Dict[Action, float]:
        """Get action values for state.

        Args:
            state: State to get values for

        Returns:
            Dictionary of action values
        """
        available_actions = self.get_available_actions(state)
        return {
            action: self.estimator.get_action_value(state, action)
            for action in available_actions
        }

    def get_stats(self) -> dict:
        """Get trainer statistics.

        Returns:
            Dictionary of statistics
        """
        estimator_stats = self.estimator.get_stats()
        return {
            **estimator_stats,
            "total_episodes": self.total_episodes,
            "current_epsilon": self.epsilon,
            "avg_reward": 0.0,
        }

    def save(self, filepath: str) -> None:
        """Save trainer to file.

        Args:
            filepath: Path to save file
        """
        data = {
            "total_episodes": self.total_episodes,
            "epsilon": self.epsilon,
            "epsilon_decay": self.policy.epsilon_decay,
            "epsilon_min": self.policy.epsilon_min,
            "policy": {
                "epsilon": self.epsilon,
                "epsilon_decay": self.policy.epsilon_decay,
                "epsilon_min": self.policy.epsilon_min,
            },
            "estimator": {
                "N": {
                    state.to_dict(): {
                        action.value: count
                        for action, count in actions.items()
                    }
                    for state, actions in self.estimator.N.items()
                },
                "Q": {
                    state.to_dict(): {
                        action.value: value
                        for action, value in actions.items()
                    }
                    for state, actions in self.estimator.Q.items()
                },
            },
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "BlackjackMonteCarloTrainer":
        """Load trainer from file.

        Args:
            filepath: Path to load file

        Returns:
            Loaded BlackjackMonteCarloTrainer
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        trainer = cls(
            epsilon=data["epsilon"],
            epsilon_decay=data["epsilon_decay"],
            epsilon_min=data["epsilon_min"],
        )
        trainer.total_episodes = data["total_episodes"]

        # Load estimator
        for state_dict, actions in data["estimator"]["N"].items():
            state = State.from_dict(state_dict)
            trainer.estimator.N[state] = {}
            trainer.estimator.Q[state] = {}

            for action_value, count in actions.items():
                action = Action(action_value)
                trainer.estimator.N[state][action] = count
                trainer.estimator.Q[state][action] = data["estimator"]["Q"][state_dict][action_value]

        return trainer