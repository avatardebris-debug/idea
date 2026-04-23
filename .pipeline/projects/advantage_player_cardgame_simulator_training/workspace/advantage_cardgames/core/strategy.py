"""Basic strategy table for standard blackjack rules.

Provides:
- BasicStrategy: precomputed strategy table for standard blackjack rules
  (dealer stands on 17, double after split allowed, surrender allowed, 6 decks).
- Strategy maps (player_hand_type, dealer_upcard) -> action.
- Serialization to/from JSON.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Tuple


class Action(Enum):
    """Possible player actions in blackjack."""
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"
    SPLIT = "split"
    SURRENDER = "surrender"
    BLACKJACK_PAYS = "blackjack_pays"
    BUST = "bust"

    def __str__(self) -> str:
        return self.value


@dataclass
class BasicStrategy:
    """Precomputed basic strategy for standard blackjack rules.

    Rules assumed:
    - Dealer stands on 17
    - Double after split allowed
    - Surrender allowed (late surrender)
    - 6 decks
    - Blackjack pays 3:2
    """

    _hard_strategy: Dict[Tuple[str, int], Action] = field(default_factory=dict)
    _soft_strategy: Dict[Tuple[str, int], Action] = field(default_factory=dict)
    _split_strategy: Dict[Tuple[str, int], Action] = field(default_factory=dict)
    _surrender_strategy: Dict[Tuple[str, int], Action] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._init_hard_strategy()
        self._init_soft_strategy()
        self._init_split_strategy()
        self._init_surrender_strategy()

    def _init_hard_strategy(self) -> None:
        hard = {}
        # Hard 8 or less: always hit
        for total in range(4, 9):
            for dealer in range(2, 12):
                hard[(f"hard_{total}", dealer)] = Action.HIT

        # Hard 9: double vs 3-6, hit otherwise
        for dealer in range(2, 12):
            hard[("hard_9", dealer)] = Action.HIT
        for dealer in range(3, 7):
            hard[("hard_9", dealer)] = Action.DOUBLE

        # Hard 10: double vs 2-9, hit vs 10/A
        for dealer in range(2, 10):
            hard[("hard_10", dealer)] = Action.DOUBLE
        for dealer in [10, 11]:
            hard[("hard_10", dealer)] = Action.HIT

        # Hard 11: double vs 2-10, hit vs A
        for dealer in range(2, 11):
            hard[("hard_11", dealer)] = Action.DOUBLE
        hard[("hard_11", 11)] = Action.HIT

        # Hard 12: stand vs 4-6, hit otherwise
        for dealer in range(2, 12):
            hard[("hard_12", dealer)] = Action.HIT
        for dealer in [4, 5, 6]:
            hard[("hard_12", dealer)] = Action.STAND

        # Hard 13-16: stand vs 2-6, hit vs 7-A
        for total in [13, 14, 15, 16]:
            for dealer in range(2, 7):
                hard[(f"hard_{total}", dealer)] = Action.STAND
            for dealer in range(7, 12):
                hard[(f"hard_{total}", dealer)] = Action.HIT

        # Hard 17+: always stand
        for total in range(17, 22):
            for dealer in range(2, 12):
                hard[(f"hard_{total}", dealer)] = Action.STAND

        self._hard_strategy = hard

    def _init_soft_strategy(self) -> None:
        soft = {}
        # Soft 13-14 (A,2-A,3): double vs 5-6, hit otherwise
        for total in [13, 14]:
            for dealer in range(2, 12):
                soft[(f"soft_{total}", dealer)] = Action.HIT
            for dealer in [5, 6]:
                soft[(f"soft_{total}", dealer)] = Action.DOUBLE

        # Soft 15-16 (A,4-A,5): double vs 4-6, hit otherwise
        for total in [15, 16]:
            for dealer in range(2, 12):
                soft[(f"soft_{total}", dealer)] = Action.HIT
            for dealer in [4, 5, 6]:
                soft[(f"soft_{total}", dealer)] = Action.DOUBLE

        # Soft 17-18 (A,5-A,7): double vs 3-6, hit vs 2, stand vs 7,8, hit vs 9,10,A
        for total in [17, 18]:
            for dealer in range(2, 12):
                soft[(f"soft_{total}", dealer)] = Action.HIT
            for dealer in [3, 4, 5, 6]:
                soft[(f"soft_{total}", dealer)] = Action.DOUBLE
            soft[(f"soft_{total}", 7)] = Action.STAND
            soft[(f"soft_{total}", 8)] = Action.STAND

        # Soft 19+ (A,8+): always stand (or double vs 6 if soft 19)
        for total in [19, 20, 21]:
            for dealer in range(2, 12):
                soft[(f"soft_{total}", dealer)] = Action.STAND
            if total == 19:
                soft[(f"soft_{total}", 6)] = Action.DOUBLE

        self._soft_strategy = soft

    def _init_split_strategy(self) -> None:
        split = {}
        # Always split Aces and 8s
        for rank in [1, 8]:
            for dealer in range(2, 12):
                split[(f"pair_{rank}", dealer)] = Action.SPLIT

        # Never split 5s (treat as hard 10)
        for dealer in range(2, 12):
            split[("pair_5", dealer)] = Action.HIT

        # Split 2s, 3s, 7s vs 2-7
        for rank in [2, 3, 7]:
            for dealer in range(2, 8):
                split[(f"pair_{rank}", dealer)] = Action.SPLIT
            for dealer in range(8, 12):
                split[(f"pair_{rank}", dealer)] = Action.HIT

        # Split 4s vs 5-6 (DAS)
        for dealer in [5, 6]:
            split[("pair_4", dealer)] = Action.SPLIT
        for dealer in range(2, 12):
            if dealer not in [5, 6]:
                split[("pair_4", dealer)] = Action.HIT

        # Split 6s vs 2-6
        for dealer in range(2, 7):
            split[("pair_6", dealer)] = Action.SPLIT
        for dealer in range(7, 12):
            split[("pair_6", dealer)] = Action.HIT

        # Split 9s vs 2-6, 8,9; stand vs 7,10,A
        for dealer in [2, 3, 4, 5, 6, 8, 9]:
            split[("pair_9", dealer)] = Action.SPLIT
        for dealer in [7, 10, 11]:
            split[("pair_9", dealer)] = Action.STAND

        # Split 10s never (stand)
        for dealer in range(2, 12):
            split[("pair_10", dealer)] = Action.STAND

        self._split_strategy = split

    def _init_surrender_strategy(self) -> None:
        surrender = {
            ("hard_16", 9): Action.SURRENDER,
            ("hard_16", 10): Action.SURRENDER,
            ("hard_16", 11): Action.SURRENDER,
            ("hard_15", 10): Action.SURRENDER,
        }
        self._surrender_strategy = surrender

    def get_hard_action(self, player_total: int, dealer_upcard: int) -> Action:
        key = (f"hard_{player_total}", dealer_upcard)
        return self._hard_strategy.get(key, Action.HIT)

    def get_soft_action(self, player_total: int, dealer_upcard: int) -> Action:
        key = (f"soft_{player_total}", dealer_upcard)
        return self._soft_strategy.get(key, Action.HIT)

    def get_split_action(self, pair_rank: int, dealer_upcard: int) -> Action:
        key = (f"pair_{pair_rank}", dealer_upcard)
        return self._split_strategy.get(key, Action.HIT)

    def get_surrender_action(self, player_total: int, dealer_upcard: int) -> Optional[Action]:
        key = (f"hard_{player_total}", dealer_upcard)
        return self._surrender_strategy.get(key)

    def get_action(self, player_hand_type: str, player_total: int,
                   dealer_upcard: int, is_pair: bool = False) -> Action:
        if is_pair:
            return self.get_split_action(player_total, dealer_upcard)
        elif player_hand_type == "soft":
            return self.get_soft_action(player_total, dealer_upcard)
        else:
            return self.get_hard_action(player_total, dealer_upcard)

    def to_dict(self) -> dict:
        return {
            "hard_strategy": {
                f"{k[0]},{k[1]}": v.value for k, v in self._hard_strategy.items()
            },
            "soft_strategy": {
                f"{k[0]},{k[1]}": v.value for k, v in self._soft_strategy.items()
            },
            "split_strategy": {
                f"{k[0]},{k[1]}": v.value for k, v in self._split_strategy.items()
            },
            "surrender_strategy": {
                f"{k[0]},{k[1]}": v.value for k, v in self._surrender_strategy.items()
            },
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, d: dict) -> BasicStrategy:
        bs = cls()
        bs._hard_strategy = {
            tuple(k.split(",")): Action(v)
            for k, v in d["hard_strategy"].items()
        }
        bs._soft_strategy = {
            tuple(k.split(",")): Action(v)
            for k, v in d["soft_strategy"].items()
        }
        bs._split_strategy = {
            tuple(k.split(",")): Action(v)
            for k, v in d["split_strategy"].items()
        }
        bs._surrender_strategy = {
            tuple(k.split(",")): Action(v)
            for k, v in d["surrender_strategy"].items()
        }
        return bs

    @classmethod
    def from_json(cls, json_str: str) -> BasicStrategy:
        return cls.from_dict(json.loads(json_str))

    def __str__(self) -> str:
        return f"BasicStrategy(hard={len(self._hard_strategy)}, soft={len(self._soft_strategy)}, split={len(self._split_strategy)}, surrender={len(self._surrender_strategy)})"

    def __repr__(self) -> str:
        return self.__str__()
