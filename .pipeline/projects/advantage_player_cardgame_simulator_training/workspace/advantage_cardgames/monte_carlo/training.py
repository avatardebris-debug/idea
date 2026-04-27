"""Monte Carlo training engine for blackjack.

Provides:
- MonteCarloTrainer: Monte Carlo control algorithm for learning optimal blackjack strategy
- StateValueEstimator: Tracks state-action values for policy improvement
- Exploration strategies for balancing exploration vs exploitation
"""

from __future__ import annotations

import random
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..core.deck import Card
from ..core.hand import Hand, HandType
from ..simulators.blackjack import BlackjackGame, BlackjackResult, SimulatorStats


class Action(Enum):
    """Possible player actions in blackjack."""
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"


@dataclass
class State:
    """Represents a blackjack game state for Monte Carlo learning."""
    player_total: int
    player_hand_type: str  # 'hard', 'soft', 'pair'
    dealer_upcard: int  # 1-11 (ace=11)
    can_double: bool = False
    can_split: bool = False
    can_surrender: bool = False

    def __hash__(self) -> int:
        return hash((
            self.player_total,
            self.player_hand_type,
            self.dealer_upcard,
            self.can_double,
            self.can_split,
            self.can_surrender,
        ))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, State):
            return False
        return (
            self.player_total == other.player_total and
            self.player_hand_type == other.player_hand_type and
            self.dealer_upcard == other.dealer_upcard and
            self.can_double == other.can_double and
            self.can_split == other.can_split and
            self.can_surrender == other.can_surrender
        )

    def to_dict(self) -> dict:
        return {
            "player_total": self.player_total,
            "player_hand_type": self.player_hand_type,
            "dealer_upcard": self.dealer_upcard,
            "can_double": self.can_double,
            "can_split": self.can_split,
            "can_surrender": self.can_surrender,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "State":
        return cls(
            player_total=d["player_total"],
            player_hand_type=d["player_hand_type"],
            dealer_upcard=d["dealer_upcard"],
            can_double=d.get("can_double", False),
            can_split=d.get("can_split", False),
            can_surrender=d.get("can_surrender", False),
        )

    @classmethod
    def from_hand(cls, player_hand: Hand, dealer_upcard: Card, game: BlackjackGame) -> "State":
        """Create a State from current game state."""
        player_total = player_hand.total
        hand_type = player_hand.hand_type.value if isinstance(player_hand.hand_type, HandType) else player_hand.hand_type
        
        # Determine if hand is a pair
        can_split = (
            len(player_hand.cards) == 2 and
            player_hand.cards[0].rank == player_hand.cards[1].rank and
            not player_hand.is_split
        )
        
        can_double = len(player_hand.cards) == 2 and not player_hand.is_split
        
        can_surrender = (
            len(player_hand.cards) == 2 and
            not player_hand.is_bust and
            not player_hand.is_blackjack
        )
        
        return cls(
            player_total=player_total,
            player_hand_type=hand_type,
            dealer_upcard=dealer_upcard.rank.value,
            can_double=can_double,
            can_split=can_split,
            can_surrender=can_surrender,
        )


@dataclass
class Episode:
    """Represents a single episode (round) for Monte Carlo learning."""
    states: List[State] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)
    rewards: List[float] = field(default_factory=list)

    def append(self, state: State, action: Action, reward: float) -> None:
        """Add a transition to the episode."""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)

    def to_dict(self) -> dict:
        return {
            "states": [s.to_dict() for s in self.states],
            "actions": [a.value for a in self.actions],
            "rewards": self.rewards,
        }


class StateValueEstimator:
    """Tracks state-action values for Monte Carlo control."""

    def __init__(self) -> None:
        # Q[s, a] = average return for state s and action a
        self.Q: Dict[State, Dict[Action, float]] = defaultdict(lambda: defaultdict(float))
        # N[s, a] = number of times state s and action a have been visited
        self.N: Dict[State, Dict[Action, int]] = defaultdict(lambda: defaultdict(int))
        # Returns[s, a] = list of returns for state s and action a (for first-visit MC)
        self.returns: Dict[State, Dict[Action, List[float]]] = defaultdict(lambda: defaultdict(list))

    def update(self, state: State, action: Action, return_value: float) -> None:
        """Update the state-action value estimate."""
        self.N[state][action] += 1
        self.returns[state][action].append(return_value)
        
        # Incremental average update
        n = self.N[state][action]
        old_avg = self.Q[state][action]
        self.Q[state][action] = old_avg + (return_value - old_avg) / n

    def get_action_value(self, state: State, action: Action) -> float:
        """Get the estimated value of taking action in state."""
        return self.Q[state][action]

    def get_best_action(self, state: State, available_actions: List[Action]) -> Action:
        """Get the best action for a state based on current estimates."""
        if not available_actions:
            return Action.STAND
        
        best_action = max(available_actions, key=lambda a: self.get_action_value(state, a))
        return best_action

    def get_all_actions(self, state: State) -> List[Action]:
        """Get all actions that have been visited for a state."""
        return list(self.N[state].keys())

    def get_stats(self) -> dict:
        """Get statistics about the learned values."""
        total_states = len(self.N)
        total_state_action_pairs = sum(len(actions) for actions in self.N.values())
        
        return {
            "total_states": total_states,
            "total_state_action_pairs": total_state_action_pairs,
            "avg_visits_per_pair": (
                total_state_action_pairs / total_states if total_states > 0 else 0
            ),
        }

    def to_dict(self) -> dict:
        """Serialize the estimator to a dictionary."""
        return {
            "Q": {
                state.to_dict(): {
                    action.value: value
                    for action, value in actions.items()
                }
                for state, actions in self.Q.items()
            },
            "N": {
                state.to_dict(): {
                    action.value: count
                    for action, count in actions.items()
                }
                for state, actions in self.N.items()
            },
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StateValueEstimator":
        """Deserialize the estimator from a dictionary."""
        estimator = cls()
        for state_dict, actions_dict in d.get("Q", {}).items():
            state = State.from_dict(state_dict)
            for action_str, value in actions_dict.items():
                action = Action(action_str)
                estimator.Q[state][action] = value
        for state_dict, actions_dict in d.get("N", {}).items():
            state = State.from_dict(state_dict)
            for action_str, count in actions_dict.items():
                action = Action(action_str)
                estimator.N[state][action] = count
        return estimator


class EpsilonGreedyPolicy:
    """Epsilon-greedy policy for exploration vs exploitation."""

    def __init__(self, epsilon: float = 0.1, epsilon_decay: float = 0.995) -> None:
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = 0.01

    def get_action(
        self,
        available_actions: List[Action],
        best_action: Action,
        state: State,
    ) -> Action:
        """Select an action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            # Explore: choose random action
            return random.choice(available_actions)
        else:
            # Exploit: choose best known action
            return best_action

    def decay(self) -> None:
        """Decay epsilon."""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def set_epsilon(self, epsilon: float) -> None:
        """Set epsilon to a specific value."""
        self.epsilon = max(self.min_epsilon, min(1.0, epsilon))


class MonteCarloTrainer:
    """Monte Carlo control trainer for blackjack."""

    def __init__(
        self,
        game: Optional[BlackjackGame] = None,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        seed: Optional[int] = None,
        learning_rate: float = 1.0,
    ) -> None:
        self.game = game or BlackjackGame()
        self.estimator = StateValueEstimator()
        self.policy = EpsilonGreedyPolicy(epsilon=epsilon, epsilon_decay=epsilon_decay)
        self.seed = seed
        self.learning_rate = learning_rate
        
        if seed is not None:
            random.seed(seed)
            self.game.seed = seed

        self.episodes: List[Episode] = []
        self.total_episodes = 0
        self.total_rounds = 0
        self.total_reward = 0.0

    def get_available_actions(self, state: State) -> List[Action]:
        """Get all valid actions for a state."""
        actions = [Action.STAND, Action.HIT]
        
        if state.can_double:
            actions.append(Action.DOUBLE)
        if state.can_split:
            actions.append(Action.SPLIT)
        if state.can_surrender:
            actions.append(Action.SURRENDER)
        
        return actions

    def select_action(
        self,
        state: State,
        available_actions: List[Action],
    ) -> Action:
        """Select an action using epsilon-greedy policy."""
        best_action = self.estimator.get_best_action(state, available_actions)
        return self.policy.get_action(available_actions, best_action, state)

    def run_episode(self) -> Episode:
        """Run a single episode and return the episode data."""
        episode = Episode()
        state = None
        action = None
        reward = 0.0

        # Reset game
        self.game.reset()

        # Play until game ends
        while True:
            # Get dealer upcard
            dealer_upcard = self.game.dealer_hand.cards[0] if hasattr(self.game, 'dealer_hand') else Card(11, "Hearts")
            
            # Create state
            if state is None:
                state = State.from_hand(
                    self.game.player_hand,
                    dealer_upcard,
                    self.game,
                )
            else:
                hand_type = self.game.player_hand.hand_type.value if isinstance(self.game.player_hand.hand_type, HandType) else self.game.player_hand.hand_type
                state = State(
                    player_total=self.game.player_hand.total,
                    player_hand_type=hand_type,
                    dealer_upcard=dealer_upcard.rank.value,
                    can_double=len(self.game.player_hand.cards) == 2,
                    can_split=(
                        len(self.game.player_hand.cards) == 2 and
                        self.game.player_hand.cards[0].rank == self.game.player_hand.cards[1].rank
                    ),
                    can_surrender=(
                        len(self.game.player_hand.cards) == 2 and
                        not self.game.player_hand.is_bust and
                        not self.game.player_hand.is_blackjack
                    ),
                )

            # Get available actions
            available_actions = self.get_available_actions(state)

            # Select action
            action = self.select_action(state, available_actions)

            # Execute action
            if action == Action.HIT:
                self.game.player_hand.add_card(self.game._shoe.deal_card())
                reward = 0.0
                if self.game.player_hand.is_bust:
                    reward = -1.0
                    break
            elif action == Action.STAND:
                # Dealer turn
                while self.game.dealer_hand.total < 17:
                    self.game.dealer_hand.add_card(self.game._shoe.deal_card())
                
                # Resolve outcome
                player_total = self.game.player_hand.total
                dealer_total = self.game.dealer_hand.total
                
                if self.game.player_hand.is_bust:
                    reward = -1.0
                    break
                elif dealer_total > 21:
                    reward = 1.0
                    break
                elif player_total > dealer_total:
                    reward = 1.0
                    break
                elif player_total < dealer_total:
                    reward = -1.0
                    break
                else:
                    reward = 0.0
                    break
            elif action == Action.DOUBLE:
                self.game.player_hand.add_card(self.game._shoe.deal_card())
                
                # Dealer turn
                while self.game.dealer_hand.total < 17:
                    self.game.dealer_hand.add_card(self.game._shoe.deal_card())
                
                # Resolve outcome
                player_total = self.game.player_hand.total
                dealer_total = self.game.dealer_hand.total
                
                if self.game.player_hand.is_bust:
                    reward = -2.0
                    break
                elif dealer_total > 21:
                    reward = 2.0
                    break
                elif player_total > dealer_total:
                    reward = 2.0
                    break
                elif player_total < dealer_total:
                    reward = -2.0
                    break
                else:
                    reward = 0.0
                    break
            elif action == Action.SPLIT:
                # Simplified split handling
                reward = 0.0
                # Continue with single hand for simplicity
            elif action == Action.SURRENDER:
                reward = -0.5
                break

            # Add to episode
            episode.append(state, action, reward)

        self.episodes.append(episode)
        self.total_episodes += 1
        return episode

    def update_values(self, episode: Episode) -> None:
        """Update state-action values using Monte Carlo returns."""
        returns = defaultdict(list)
        cumulative_return = 0.0

        # Calculate returns from end to start
        for state, action, reward in zip(
            reversed(episode.states),
            reversed(episode.actions),
            reversed(episode.rewards),
        ):
            cumulative_return = reward + cumulative_return
            returns[state][action].append(cumulative_return)

        # Update Q values
        for state, action_returns in returns.items():
            for action, return_values in action_returns.items():
                avg_return = sum(return_values) / len(return_values)
                self.estimator.update(state, action, avg_return)

    def train_episode(self) -> Tuple[Episode, float]:
        """Train on a single episode and return the episode and total reward."""
        episode = self.run_episode()
        self.update_values(episode)
        total_reward = sum(episode.rewards)
        self.total_reward += total_reward
        self.total_rounds += 1
        return episode, total_reward

    def train(
        self,
        num_episodes: int,
        verbose: bool = True,
        save_interval: int = 100,
    ) -> dict:
        """Train the Monte Carlo controller for a number of episodes."""
        rewards = []
        episode_rewards = []

        for i in range(num_episodes):
            episode, total_reward = self.train_episode()
            episode_rewards.append(total_reward)
            rewards.append(total_reward)

            # Decay exploration
            self.policy.decay()

            # Progress reporting
            if verbose and (i + 1) % save_interval == 0:
                avg_reward = sum(episode_rewards[-save_interval:]) / save_interval
                print(
                    f"Episode {i + 1}/{num_episodes}, "
                    f"Avg Reward: {avg_reward:.3f}, "
                    f"Epsilon: {self.policy.epsilon:.4f}"
                )

        # Calculate final statistics
        stats = {
            "total_episodes": num_episodes,
            "total_reward": self.total_reward,
            "avg_reward": self.total_reward / num_episodes,
            "final_epsilon": self.policy.epsilon,
            "states_learned": len(self.estimator.N),
            "avg_visits_per_state_action": sum(
                sum(actions.values()) for actions in self.estimator.N.values()
            ) / max(len(self.estimator.N), 1),
        }

        return stats

    def get_policy(self, state: State) -> Action:
        """Get the best action for a state based on learned values."""
        available_actions = self.get_available_actions(state)
        return self.estimator.get_best_action(state, available_actions)

    def get_action_values(self, state: State) -> Dict[str, float]:
        """Get action values for a state."""
        return {
            action.value: self.estimator.get_action_value(state, action)
            for action in self.get_available_actions(state)
        }

    def get_stats(self) -> dict:
        """Get training statistics."""
        estimator_stats = self.estimator.get_stats()
        return {
            **estimator_stats,
            "total_episodes": self.total_episodes,
            "total_reward": self.total_reward,
            "avg_reward": self.total_reward / max(self.total_episodes, 1),
            "current_epsilon": self.policy.epsilon,
        }

    def save(self, filepath: str) -> None:
        """Save the trained model to a file."""
        import json
        data = {
            "estimator": self.estimator.to_dict(),
            "policy": {
                "epsilon": self.policy.epsilon,
                "epsilon_decay": self.policy.epsilon_decay,
            },
            "stats": self.get_stats(),
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str, game: Optional[BlackjackGame] = None) -> "MonteCarloTrainer":
        """Load a trained model from a file."""
        import json
        with open(filepath, "r") as f:
            data = json.load(f)

        trainer = cls(game=game)
        trainer.estimator = StateValueEstimator.from_dict(data["estimator"])
        trainer.policy.epsilon = data["policy"]["epsilon"]
        trainer.policy.epsilon_decay = data["policy"]["epsilon_decay"]
        return trainer

    def evaluate(self, num_episodes: int = 1000) -> dict:
        """Evaluate the current policy without exploration."""
        original_epsilon = self.policy.epsilon
        self.policy.epsilon = 0.0  # No exploration

        total_reward = 0.0
        wins = 0
        losses = 0
        pushes = 0

        for _ in range(num_episodes):
            episode, reward = self.train_episode()
            total_reward += reward
            if reward > 0:
                wins += 1
            elif reward < 0:
                losses += 1
            else:
                pushes += 1

        self.policy.epsilon = original_epsilon  # Restore exploration

        return {
            "total_episodes": num_episodes,
            "total_reward": total_reward,
            "avg_reward": total_reward / num_episodes,
            "win_rate": wins / num_episodes,
            "loss_rate": losses / num_episodes,
            "push_rate": pushes / num_episodes,
        }
