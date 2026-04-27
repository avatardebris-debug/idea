"""Blackjack simulator implementation.

Provides:
- BlackjackGame: concrete game engine for blackjack
- BlackjackSimulator: simulator for running blackjack hands
- Result aggregation and statistics
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..core.game import GameState, RoundResult, Game
from ..core.hand import Outcome
from ..core.deck import Deck, Shoe, Card
from ..core.hand import Hand, HandType
from ..core.deck import Card, Rank
from ..core.strategy import BasicStrategy, Action


@dataclass
class BlackjackResult(RoundResult):
    """Result of a blackjack round."""
    player_hand: Optional[Hand] = None
    dealer_hand: Optional[Hand] = None
    player_action: Optional[str] = None
    dealer_busted: bool = False
    player_busted: bool = False
    is_blackjack: bool = False
    payout_multiplier: float = 0.0


class BlackjackGame(Game):
    """Concrete game engine for blackjack."""

    def __init__(
        self,
        num_decks: int = 6,
        dealer_stands_on_17: bool = True,
        double_after_split: bool = True,
        surrender_allowed: bool = True,
        blackjack_pays: float = 1.5,
        seed: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.num_decks = num_decks
        self.dealer_stands_on_17 = dealer_stands_on_17
        self.double_after_split = double_after_split
        self.surrender_allowed = surrender_allowed
        self.blackjack_pays = blackjack_pays
        self.seed = seed
        self._shoe: Optional[Shoe] = None
        self._strategy = BasicStrategy()

    def _create_shoe(self) -> Shoe:
        shoe = Shoe(num_decks=self.num_decks)
        shoe.shuffle()
        return shoe

    def _deal_initial_cards(self) -> Tuple[Hand, Hand]:
        """Deal initial cards to player and dealer."""
        player_hand = Hand()
        dealer_hand = Hand()

        # Deal in alternating order: player, dealer, player, dealer
        player_hand.add_card(self._shoe.deal_card())
        dealer_hand.add_card(self._shoe.deal_card())
        player_hand.add_card(self._shoe.deal_card())
        dealer_hand.add_card(self._shoe.deal_card())

        return player_hand, dealer_hand

    def _check_blackjack(self, player_hand: Hand, dealer_hand: Hand) -> Optional[BlackjackResult]:
        """Check for natural blackjack."""
        player_total = player_hand.total
        dealer_total = dealer_hand.total

        player_bj = player_total == 21 and len(player_hand.cards) == 2
        dealer_bj = dealer_total == 21 and len(dealer_hand.cards) == 2

        if player_bj and dealer_bj:
            return BlackjackResult(
                outcome=Outcome.PUSH,
                bet=1.0,
                payout=1.0,
                net_result=0.0,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                is_blackjack=True,
                payout_multiplier=1.0,
            )
        elif player_bj:
            payout = 1.0 + (self.blackjack_pays * 1.0)  # 1:1 return + 3:2 payout
            return BlackjackResult(
                outcome=Outcome.WIN,
                bet=1.0,
                payout=payout,
                net_result=self.blackjack_pays,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                is_blackjack=True,
                payout_multiplier=self.blackjack_pays,
            )
        elif dealer_bj:
            return BlackjackResult(
                outcome=Outcome.LOSS,
                bet=1.0,
                payout=0.0,
                net_result=-1.0,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                is_blackjack=True,
                payout_multiplier=0.0,
            )
        return None

    def _player_turn(self, player_hand: Hand, dealer_upcard: Card) -> Tuple[Hand, str]:
        """Execute player turn using basic strategy."""
        action_taken = "stand"
        hand = player_hand

        while True:
            hand_type = hand.hand_type
            total = hand.total
            is_pair = hand.can_split and len(hand.cards) == 2

            # Check for surrender
            if self.surrender_allowed and len(hand.cards) == 2:
                surrender_action = self._strategy.get_surrender_action(total, dealer_upcard.rank.value)
                if surrender_action == Action.SURRENDER:
                    return hand, "surrender"

            # Get recommended action
            if is_pair and self.double_after_split:
                action = self._strategy.get_split_action(hand.cards[0].rank.value, dealer_upcard.rank.value)
            else:
                action = self._strategy.get_action(
                    hand_type.value, total, dealer_upcard.rank.value, is_pair
                )

            if action == Action.HIT:
                hand.add_card(self._shoe.deal_card())
                action_taken = "hit"
                if hand.is_busted:
                    return hand, "bust"
            elif action == Action.STAND:
                return hand, "stand"
            elif action == Action.DOUBLE:
                if len(hand.cards) == 2:
                    hand.add_card(self._shoe.deal_card())
                    action_taken = "double"
                    if hand.is_busted:
                        return hand, "bust"
                    return hand, "double"
                else:
                    # Can't double after hitting, just hit
                    hand.add_card(self._shoe.deal_card())
                    action_taken = "hit"
                    if hand.is_busted:
                        return hand, "bust"
            elif action == Action.SPLIT:
                if len(hand.cards) == 2 and hand.can_split:
                    return hand, "split"
                else:
                    # Can't split, just hit
                    hand.add_card(self._shoe.deal_card())
                    action_taken = "hit"
                    if hand.is_busted:
                        return hand, "bust"
            else:
                return hand, "stand"

    def _dealer_turn(self, dealer_hand: Hand) -> Tuple[Hand, bool]:
        """Execute dealer turn."""
        dealer_busted = False

        while True:
            total = dealer_hand.total
            if self.dealer_stands_on_17 and total >= 17:
                break
            elif not self.dealer_stands_on_17 and total >= 17 and total < 21:
                # Soft 17: hit
                if dealer_hand.hand_type == HandType.SOFT:
                    dealer_hand.add_card(self._shoe.deal_card())
                    continue
                break
            elif total < 17:
                dealer_hand.add_card(self._shoe.deal_card())
            else:
                break

            if dealer_hand.is_busted:
                dealer_busted = True
                break

        return dealer_hand, dealer_busted

    def _resolve_outcome(
        self,
        player_hand: Hand,
        dealer_hand: Hand,
        player_action: str,
        dealer_busted: bool,
        bet: float = 1.0,
    ) -> BlackjackResult:
        """Resolve the outcome of the round."""
        player_busted = player_hand.is_busted
        player_total = player_hand.total
        dealer_total = dealer_hand.total

        if player_action == "surrender":
            return BlackjackResult(
                outcome=Outcome.LOSS,
                bet=bet,
                payout=bet * 0.5,
                net_result=-bet * 0.5,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                player_action="surrender",
                player_busted=player_busted,
                dealer_busted=dealer_busted,
                payout_multiplier=0.5,
            )

        if player_busted:
            return BlackjackResult(
                outcome=Outcome.BUST,
                bet=bet,
                payout=0.0,
                net_result=-bet,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                player_action=player_action,
                player_busted=True,
                dealer_busted=dealer_busted,
                payout_multiplier=0.0,
            )

        if dealer_busted:
            return BlackjackResult(
                outcome=Outcome.WIN,
                bet=bet,
                payout=bet * 2.0,
                net_result=bet,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                player_action=player_action,
                player_busted=False,
                dealer_busted=True,
                payout_multiplier=2.0,
            )

        if player_total > dealer_total:
            return BlackjackResult(
                outcome=Outcome.WIN,
                bet=bet,
                payout=bet * 2.0,
                net_result=bet,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                player_action=player_action,
                player_busted=False,
                dealer_busted=False,
                payout_multiplier=2.0,
            )
        elif player_total < dealer_total:
            return BlackjackResult(
                outcome=Outcome.LOSS,
                bet=bet,
                payout=0.0,
                net_result=-bet,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                player_action=player_action,
                player_busted=False,
                dealer_busted=False,
                payout_multiplier=0.0,
            )
        else:
            return BlackjackResult(
                outcome=Outcome.PUSH,
                bet=bet,
                payout=bet,
                net_result=0.0,
                player_hand=player_hand,
                dealer_hand=dealer_hand,
                player_action=player_action,
                player_busted=False,
                dealer_busted=False,
                payout_multiplier=1.0,
            )

    def play_round(self, bet: float = 1.0) -> BlackjackResult:
        """Play a single round of blackjack."""
        if self._state != GameState.IDLE:
            raise RuntimeError("Game must be in IDLE state to start a new round")

        self._state = GameState.PLAYING

        # Check if shoe needs reshuffling
        if self._shoe is None or self._shoe.cards_remaining < 20:
            self._shoe = self._create_shoe()

        # Deal initial cards
        player_hand, dealer_hand = self._deal_initial_cards()

        # Check for natural blackjack
        bj_result = self._check_blackjack(player_hand, dealer_hand)
        if bj_result:
            bj_result.player_action = "blackjack"
            self._state = GameState.FINISHED
            return bj_result

        # Get dealer's upcard
        dealer_upcard = dealer_hand.cards[0]

        # Player turn
        player_hand, player_action = self._player_turn(player_hand, dealer_upcard)

        if player_action in ["surrender", "bust"]:
            result = self._resolve_outcome(
                player_hand, dealer_hand, player_action, False, bet
            )
            self._state = GameState.FINISHED
            return result

        # Dealer turn
        dealer_hand, dealer_busted = self._dealer_turn(dealer_hand)

        # Resolve outcome
        result = self._resolve_outcome(
            player_hand, dealer_hand, player_action, dealer_busted, bet
        )
        self._state = GameState.FINISHED
        return result

    def reset(self) -> None:
        """Reset the game state."""
        self._state = GameState.IDLE
        self._shoe = None

    def __str__(self) -> str:
        return f"BlackjackGame(state={self._state.value}, shoe={self._shoe.cards_remaining if self._shoe else 0} cards)"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class SimulatorStats:
    """Statistics from a simulation run."""
    total_rounds: int = 0
    total_bets: float = 0.0
    total_payouts: float = 0.0
    net_result: float = 0.0
    wins: int = 0
    losses: int = 0
    pushes: int = 0
    busts: int = 0
    blackjacks: int = 0
    avg_bet: float = 0.0
    avg_payout: float = 0.0
    avg_net: float = 0.0
    roi: float = 0.0
    win_rate: float = 0.0
    max_winning_streak: int = 0
    max_losing_streak: int = 0
    current_streak: int = 0
    streak_type: str = ""

    def update(self, result: BlackjackResult) -> None:
        """Update statistics with a new result."""
        self.total_rounds += 1
        self.total_bets += result.bet
        self.total_payouts += result.payout
        self.net_result += result.net_result

        if result.outcome == Outcome.WIN:
            self.wins += 1
            self.current_streak += 1
            self.streak_type = "win"
        elif result.outcome == Outcome.LOSS:
            self.losses += 1
            self.current_streak -= 1
            self.streak_type = "loss"
        elif result.outcome == Outcome.PUSH:
            self.pushes += 1
            self.current_streak = 0
            self.streak_type = ""
        elif result.outcome == Outcome.BUST:
            self.busts += 1
            self.current_streak -= 1
            self.streak_type = "loss"
        elif result.outcome == Outcome.BLACKJACK:
            self.blackjacks += 1
            self.wins += 1
            self.current_streak += 1
            self.streak_type = "win"

        if self.current_streak > self.max_winning_streak:
            self.max_winning_streak = self.current_streak
        if self.current_streak < -self.max_losing_streak:
            self.max_losing_streak = -self.current_streak

        # Update averages
        if self.total_rounds > 0:
            self.avg_bet = self.total_bets / self.total_rounds
            self.avg_payout = self.total_payouts / self.total_rounds
            self.avg_net = self.net_result / self.total_rounds
            self.roi = (self.net_result / self.total_bets * 100) if self.total_bets > 0 else 0.0
            self.win_rate = (self.wins / self.total_rounds * 100) if self.total_rounds > 0 else 0.0

    def to_dict(self) -> dict:
        """Convert stats to dictionary."""
        return {
            "total_rounds": self.total_rounds,
            "total_bets": self.total_bets,
            "total_payouts": self.total_payouts,
            "net_result": self.net_result,
            "wins": self.wins,
            "losses": self.losses,
            "pushes": self.pushes,
            "busts": self.busts,
            "blackjacks": self.blackjacks,
            "avg_bet": self.avg_bet,
            "avg_payout": self.avg_payout,
            "avg_net": self.avg_net,
            "roi": self.roi,
            "win_rate": self.win_rate,
            "max_winning_streak": self.max_winning_streak,
            "max_losing_streak": self.max_losing_streak,
        }

    def __str__(self) -> str:
        return (
            f"SimulatorStats(rounds={self.total_rounds}, net={self.net_result:.2f}, "
            f"ROI={self.roi:.2f}%, wins={self.wins}, losses={self.losses}, "
            f"pushes={self.pushes}, busts={self.busts}, BJ={self.blackjacks})"
        )

    def __repr__(self) -> str:
        return self.__str__()


class BlackjackSimulator:
    """Simulator for running blackjack hands."""

    def __init__(
        self,
        num_decks: int = 6,
        dealer_stands_on_17: bool = True,
        double_after_split: bool = True,
        surrender_allowed: bool = True,
        blackjack_pays: float = 1.5,
        seed: Optional[int] = None,
    ) -> None:
        self.game = BlackjackGame(
            num_decks=num_decks,
            dealer_stands_on_17=dealer_stands_on_17,
            double_after_split=double_after_split,
            surrender_allowed=surrender_allowed,
            blackjack_pays=blackjack_pays,
            seed=seed,
        )
        self.stats = SimulatorStats()
        self.results: List[BlackjackResult] = []
        self._bet_strategy = self._fixed_bet_strategy

    def _fixed_bet_strategy(self, stats: SimulatorStats) -> float:
        """Fixed bet strategy: always bet 1.0."""
        return 1.0

    def _flat_bet_strategy(self, stats: SimulatorStats) -> float:
        """Flat bet strategy: always bet 1.0."""
        return 1.0

    def _martingale_strategy(self, stats: SimulatorStats) -> float:
        """Martingale betting strategy: double after loss, reset after win."""
        if stats.current_streak < 0:
            return 2 ** (-stats.current_streak)
        return 1.0

    def _reverse_martingale_strategy(self, stats: SimulatorStats) -> float:
        """Reverse Martingale: double after win, reset after loss."""
        if stats.current_streak > 0:
            return 2 ** stats.current_streak
        return 1.0

    def set_bet_strategy(self, strategy_name: str) -> None:
        """Set the betting strategy."""
        strategies = {
            "fixed": self._fixed_bet_strategy,
            "flat": self._flat_bet_strategy,
            "martingale": self._martingale_strategy,
            "reverse_martingale": self._reverse_martingale_strategy,
        }
        if strategy_name in strategies:
            self._bet_strategy = strategies[strategy_name]
        else:
            raise ValueError(f"Unknown bet strategy: {strategy_name}")

    def run_round(self, bet: Optional[float] = None) -> BlackjackResult:
        """Run a single round of blackjack."""
        if bet is None:
            bet = self._bet_strategy(self.stats)

        result = self.game.play_round(bet)
        self.stats.update(result)
        self.results.append(result)
        return result

    def run_simulation(self, num_rounds: int, bet: Optional[float] = None) -> SimulatorStats:
        """Run a simulation for a specified number of rounds."""
        for _ in range(num_rounds):
            self.run_round(bet)
        return self.stats

    def reset(self) -> None:
        """Reset the simulator."""
        self.game.reset()
        self.stats = SimulatorStats()
        self.results.clear()

    def get_summary(self) -> dict:
        """Get a summary of the simulation."""
        return self.stats.to_dict()

    def __str__(self) -> str:
        return f"BlackjackSimulator(stats={self.stats})"

    def __repr__(self) -> str:
        return self.__str__()
