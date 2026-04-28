"""Abstract Game base class for card game implementations.

Provides:
- Game: abstract base class defining the interface for all game implementations.
  Includes state serialization/deserialization, round management, and outcome tracking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from advantage_cardgames.core.deck import Card, Deck, Shoe
from advantage_cardgames.core.hand import Hand, Outcome


class GameState(Enum):
    """Possible states of a game."""
    IDLE = "IDLE"
    DEALING = "DEALING"
    PLAYING = "PLAYING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


@dataclass
class RoundResult:
    """Result of a single round/hand."""
    outcome: Outcome
    player_total: int
    dealer_total: int
    bet: float = 1.0
    payout: float = 0.0
    details: str = ""

    @property
    def net_result(self) -> float:
        """Net result: positive = win, negative = loss, zero = push."""
        if self.outcome == Outcome.BLACKJACK:
            return self.bet * 1.5
        elif self.outcome == Outcome.WIN:
            return self.bet
        elif self.outcome == Outcome.PUSH:
            return 0.0
        elif self.outcome == Outcome.BUST:
            return -self.bet
        elif self.outcome == Outcome.LOSS:
            return -self.bet
        elif self.outcome == Outcome.FOLD:
            return -self.bet * 0.5
        return 0.0


@dataclass
class GameStats:
    """Aggregated statistics across multiple rounds."""
    total_rounds: int = 0
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    blackjacks: int = 0
    busts: int = 0
    surrenders: int = 0
    total_bet: float = 0.0
    total_payout: float = 0.0
    net_result: float = 0.0

    @property
    def win_rate(self) -> float:
        if self.total_rounds == 0:
            return 0.0
        return self.wins / self.total_rounds

    @property
    def loss_rate(self) -> float:
        if self.total_rounds == 0:
            return 0.0
        return self.losses / self.total_rounds

    @property
    def push_rate(self) -> float:
        if self.total_rounds == 0:
            return 0.0
        return self.pushes / self.total_rounds

    @property
    def ev_per_hand(self) -> float:
        """Expected value per hand."""
        if self.total_rounds == 0:
            return 0.0
        return self.net_result / self.total_rounds

    @property
    def ev_percentage(self) -> float:
        """Expected value as percentage of bet."""
        if self.total_bet == 0:
            return 0.0
        return (self.net_result / self.total_bet) * 100

    @property
    def standard_deviation(self) -> float:
        """Standard deviation of results."""
        if self.total_rounds < 2:
            return 0.0
        mean = self.net_result / self.total_rounds
        # Approximate using win/loss distribution
        p_win = self.wins / self.total_rounds if self.total_rounds > 0 else 0
        p_loss = self.losses / self.total_rounds if self.total_rounds > 0 else 0
        p_push = self.pushes / self.total_rounds if self.total_rounds > 0 else 0
        # Variance = E[X^2] - (E[X])^2
        # For blackjack: win=+1, loss=-1, push=0, blackjack=+1.5, surrender=-0.5
        e_x2 = (self.wins * 1.0 + self.losses * 1.0 +
                self.blackjacks * 2.25 + self.surrenders * 0.25) / self.total_rounds
        e_x = mean
        variance = e_x2 - e_x ** 2
        return max(0.0, variance) ** 0.5

    def to_dict(self) -> dict:
        return {
            "total_rounds": self.total_rounds,
            "wins": self.wins,
            "losses": self.losses,
            "pushes": self.pushes,
            "blackjacks": self.blackjacks,
            "busts": self.busts,
            "surrenders": self.surrenders,
            "total_bet": self.total_bet,
            "total_payout": self.total_payout,
            "net_result": self.net_result,
            "win_rate": self.win_rate,
            "loss_rate": self.loss_rate,
            "push_rate": self.push_rate,
            "ev_per_hand": self.ev_per_hand,
            "ev_percentage": self.ev_percentage,
            "standard_deviation": self.standard_deviation,
        }

    @classmethod
    def from_dict(cls, d: dict) -> GameStats:
        return cls(
            total_rounds=d.get("total_rounds", 0),
            wins=d.get("wins", 0),
            losses=d.get("losses", 0),
            pushes=d.get("pushes", 0),
            blackjacks=d.get("blackjacks", 0),
            busts=d.get("busts", 0),
            surrenders=d.get("surrenders", 0),
            total_bet=d.get("total_bet", 0.0),
            total_payout=d.get("total_payout", 0.0),
            net_result=d.get("net_result", 0.0),
        )


class Game(ABC):
    """Abstract base class for all card game implementations.

    All game implementations must:
    1. Initialize with a deck/shoe
    2. Implement deal_round() to start a new round
    3. Implement player_action() to process player decisions
    4. Implement dealer_play() to process dealer actions
    5. Implement evaluate() to determine outcomes
    6. Provide state serialization/deserialization
    """

    def __init__(self, deck: Optional[Deck] = None, shoe: Optional[Shoe] = None):
        self._deck = deck
        self._shoe = shoe
        self._state: GameState = GameState.IDLE
        self._round_results: List[RoundResult] = []
        self._stats = GameStats()
        self._player_hand: Optional[Hand] = None
        self._dealer_hand: Optional[Hand] = None
        self._current_bet: float = 1.0
        self._round_number: int = 0

    @property
    def state(self) -> GameState:
        return self._state

    @property
    def player_hand(self) -> Optional[Hand]:
        return self._player_hand

    @property
    def dealer_hand(self) -> Optional[Hand]:
        return self._dealer_hand

    @property
    def current_bet(self) -> float:
        return self._current_bet

    @property
    def round_number(self) -> int:
        return self._round_number

    @property
    def stats(self) -> GameStats:
        return self._stats

    @property
    def round_results(self) -> List[RoundResult]:
        return list(self._round_results)

    @abstractmethod
    def deal_round(self, bet: float = 1.0) -> None:
        """Start a new round. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def player_action(self, action: str, **kwargs) -> Optional[Outcome]:
        """Process a player action. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def dealer_play(self) -> None:
        """Process dealer's turn. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def evaluate(self) -> RoundResult:
        """Evaluate the round and return the result. Must be implemented by subclasses."""
        pass

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset the game to initial state."""
        self._state = GameState.IDLE
        self._round_results.clear()
        self._stats = GameStats()
        self._player_hand = None
        self._dealer_hand = None
        self._current_bet = 1.0
        self._round_number = 0
        if self._deck:
            self._deck.reset(seed)
        if self._shoe:
            self._shoe.reset(seed)

    def get_state(self) -> dict:
        """Serialize game state."""
        return {
            "state": self._state.value,
            "player_hand": self._player_hand.to_dict() if self._player_hand else None,
            "dealer_hand": self._dealer_hand.to_dict() if self._dealer_hand else None,
            "current_bet": self._current_bet,
            "round_number": self._round_number,
            "stats": self._stats.to_dict(),
            "round_results": [r.__dict__ for r in self._round_results],
        }

    def set_state(self, state: dict) -> None:
        """Deserialize game state."""
        self._state = GameState(state["state"])
        if state["player_hand"]:
            self._player_hand = Hand.from_dict(state["player_hand"])
        if state["dealer_hand"]:
            self._dealer_hand = Hand.from_dict(state["dealer_hand"])
        self._current_bet = state["current_bet"]
        self._round_number = state["round_number"]
        self._stats = GameStats.from_dict(state["stats"])
        self._round_results = [RoundResult(**r) for r in state["round_results"]]

    def _update_stats(self, result: RoundResult) -> None:
        """Update aggregated statistics after a round."""
        self._stats.total_rounds += 1
        self._stats.total_bet += result.bet
        self._stats.total_payout += result.payout
        self._stats.net_result += result.net_result

        if result.outcome == Outcome.WIN:
            self._stats.wins += 1
        elif result.outcome == Outcome.LOSS:
            self._stats.losses += 1
        elif result.outcome == Outcome.PUSH:
            self._stats.pushes += 1
        elif result.outcome == Outcome.BUST:
            self._stats.busts += 1
        elif result.outcome == Outcome.FOLD:
            self._stats.surrenders += 1

        if result.outcome == Outcome.BLACKJACK:
            self._stats.blackjacks += 1

    def _finalize_round(self, result: RoundResult) -> None:
        """Finalize a round: update stats, record result, reset state."""
        self._update_stats(result)
        self._round_results.append(result)
        self._state = GameState.FINISHED

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(state={self._state.value})"

    def __repr__(self) -> str:
        return self.__str__()
