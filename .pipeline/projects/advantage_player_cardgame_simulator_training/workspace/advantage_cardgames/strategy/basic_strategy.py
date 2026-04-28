"""Basic strategy implementation for blackjack.

Provides:
- Action: enumeration of possible player actions
- BasicStrategy: optimal strategy table for blackjack
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple


class Action(Enum):
    """Possible player actions in blackjack."""
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"
    NONE = "none"


@dataclass
class StrategyTable:
    """A strategy table mapping (hand_total, dealer_upcard) -> action."""
    table: Dict[Tuple[int, int], Action]

    def get(self, hand_total: int, dealer_upcard: int) -> Action:
        """Get action for given hand total and dealer upcard."""
        return self.table.get((hand_total, dealer_upcard), Action.STAND)


class BasicStrategy:
    """Optimal basic strategy for blackjack."""

    def __init__(self) -> None:
        self._hard_strategy = self._build_hard_strategy()
        self._soft_strategy = self._build_soft_strategy()
        self._split_strategy = self._build_split_strategy()
        self._surrender_strategy = self._build_surrender_strategy()

    def _build_hard_strategy(self) -> Dict[Tuple[int, int], Action]:
        """Build hard hand strategy table."""
        table: Dict[Tuple[int, int], Action] = {}

        # Hard 8 or less: always hit
        for total in range(4, 9):
            for dealer in range(2, 12):
                table[(total, dealer)] = Action.HIT

        # Hard 9: double vs 3-6, otherwise hit
        for dealer in range(3, 7):
            table[(9, dealer)] = Action.DOUBLE
        for dealer in range(2, 12):
            if table.get((9, dealer)) is None:
                table[(9, dealer)] = Action.HIT

        # Hard 10: double vs 2-9, otherwise hit
        for dealer in range(2, 10):
            table[(10, dealer)] = Action.DOUBLE
        for dealer in range(10, 12):
            table[(10, dealer)] = Action.HIT

        # Hard 11: always double
        for dealer in range(2, 12):
            table[(11, dealer)] = Action.DOUBLE

        # Hard 12: stand vs 4-6, otherwise hit
        for dealer in range(4, 7):
            table[(12, dealer)] = Action.STAND
        for dealer in range(2, 12):
            if table.get((12, dealer)) is None:
                table[(12, dealer)] = Action.HIT

        # Hard 13-16: stand vs 2-6, otherwise hit
        for total in range(13, 17):
            for dealer in range(2, 7):
                table[(total, dealer)] = Action.STAND
            for dealer in range(7, 12):
                table[(total, dealer)] = Action.HIT

        # Hard 17+: always stand
        for total in range(17, 22):
            for dealer in range(2, 12):
                table[(total, dealer)] = Action.STAND

        return table

    def _build_soft_strategy(self) -> Dict[Tuple[int, int], Action]:
        """Build soft hand strategy table."""
        table: Dict[Tuple[int, int], Action] = {}

        # Soft 13-15: double vs 5-6, otherwise hit
        for total in range(13, 16):
            for dealer in range(5, 7):
                table[(total, dealer)] = Action.DOUBLE
            for dealer in range(2, 12):
                if table.get((total, dealer)) is None:
                    table[(total, dealer)] = Action.HIT

        # Soft 16-18: double vs 3-6, otherwise hit
        for total in range(16, 19):
            for dealer in range(3, 7):
                table[(total, dealer)] = Action.DOUBLE
            for dealer in range(2, 12):
                if table.get((total, dealer)) is None:
                    table[(total, dealer)] = Action.HIT

        # Soft 19-21: stand
        for total in range(19, 22):
            for dealer in range(2, 12):
                table[(total, dealer)] = Action.STAND

        return table

    def _build_split_strategy(self) -> Dict[Tuple[int, int], Action]:
        """Build split strategy table."""
        table: Dict[Tuple[int, int], Action] = {}

        # Always split Aces and 8s
        for dealer in range(2, 12):
            table[(1, dealer)] = Action.SPLIT  # Aces
            table[(8, dealer)] = Action.SPLIT  # 8s

        # Never split 10s and 5s
        for dealer in range(2, 12):
            table[(10, dealer)] = Action.STAND  # 10s
            table[(5, dealer)] = Action.STAND   # 5s

        # Split 2s and 3s vs 2-7
        for dealer in range(2, 8):
            table[(2, dealer)] = Action.SPLIT  # 2s
            table[(3, dealer)] = Action.SPLIT  # 3s

        # Split 4s only vs 5-6 (rare)
        for dealer in range(5, 7):
            table[(4, dealer)] = Action.SPLIT

        # Split 6s vs 2-6
        for dealer in range(2, 7):
            table[(6, dealer)] = Action.SPLIT

        # Split 7s vs 2-7
        for dealer in range(2, 8):
            table[(7, dealer)] = Action.SPLIT

        # Split 9s vs 2-6, 8-9 (not 7, 10, 11)
        for dealer in [2, 3, 4, 5, 6, 8, 9]:
            table[(9, dealer)] = Action.SPLIT

        return table

    def _build_surrender_strategy(self) -> Dict[Tuple[int, int], Action]:
        """Build surrender strategy table."""
        table: Dict[Tuple[int, int], Action] = {}

        # Surrender 16 vs 9, 10, A
        table[(16, 9)] = Action.SURRENDER
        table[(16, 10)] = Action.SURRENDER
        table[(16, 11)] = Action.SURRENDER

        # Surrender 15 vs 10
        table[(15, 10)] = Action.SURRENDER

        return table

    def get_hard_action(self, total: int, dealer_upcard: int) -> Action:
        """Get action for hard hand."""
        return self._hard_strategy.get((total, dealer_upcard), Action.STAND)

    def get_soft_action(self, total: int, dealer_upcard: int) -> Action:
        """Get action for soft hand."""
        return self._soft_strategy.get((total, dealer_upcard), Action.STAND)

    def get_split_action(self, player_rank: int, dealer_upcard: int) -> Action:
        """Get action for split decision."""
        return self._split_strategy.get((player_rank, dealer_upcard), Action.STAND)

    def get_surrender_action(self, total: int, dealer_upcard: int) -> Action:
        """Get surrender decision."""
        return self._surrender_strategy.get((total, dealer_upcard), Action.NONE)

    def get_action(
        self,
        hand_type: str,
        total: int,
        dealer_upcard: int,
        is_pair: bool = False,
    ) -> Action:
        """Get action based on hand type."""
        if hand_type == "hard":
            return self.get_hard_action(total, dealer_upcard)
        elif hand_type == "soft":
            return self.get_soft_action(total, dealer_upcard)
        elif hand_type == "pair" and is_pair:
            return self.get_split_action(total, dealer_upcard)
        return Action.STAND

    def to_json(self) -> str:
        """Convert strategy to JSON format."""
        import json

        return json.dumps({
            "hard": {
                f"{total}-{dealer}": action.value
                for (total, dealer), action in self._hard_strategy.items()
            },
            "soft": {
                f"{total}-{dealer}": action.value
                for (total, dealer), action in self._soft_strategy.items()
            },
            "split": {
                f"{rank}-{dealer}": action.value
                for (rank, dealer), action in self._split_strategy.items()
            },
            "surrender": {
                f"{total}-{dealer}": action.value
                for (total, dealer), action in self._surrender_strategy.items()
            },
        }, indent=2)

    def __str__(self) -> str:
        return "BasicStrategy (optimal blackjack strategy)"

    def __repr__(self) -> str:
        return self.__str__()
