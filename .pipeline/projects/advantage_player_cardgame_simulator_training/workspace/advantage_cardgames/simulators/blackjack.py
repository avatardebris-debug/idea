"""Blackjack simulator module.

Provides:
- Card: Represents a playing card with rank and suit
- Deck: Manages a deck of cards with shuffling and dealing
- Hand: Represents a player's or dealer's hand of cards
- GameStatus: Enum for game state
- BlackjackResult: Enum for game outcomes
- BlackjackResultData: Dataclass for result tracking
- SimulatorStats: Statistics tracking for simulations
- BlackjackGame: Main game class for playing blackjack
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Card:
    """Represents a playing card."""

    SUITS = ["♥", "♦", "♣", "♠"]
    RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]  # 11=J, 12=Q, 13=K, 14=A

    def __init__(self, rank: int, suit: str):
        """Initialize a card.
        
        Args:
            rank: Card rank (2-14, where 11=J, 12=Q, 13=K, 14=A)
            suit: Card suit (♥, ♦, ♣, or ♠)
        """
        self.rank = rank
        self.suit = suit

    @property
    def value(self) -> int:
        """Get card value for hand calculation."""
        if self.rank >= 11 and self.rank <= 13:
            return 10
        return self.rank

    @property
    def is_ace(self) -> bool:
        """Check if card is an ace."""
        return self.rank == 14

    @property
    def is_face(self) -> bool:
        """Check if card is a face card."""
        return self.rank >= 11 and self.rank <= 13

    def to_dict(self) -> dict:
        """Convert card to dictionary."""
        return {"rank": self.rank, "suit": self.suit}

    @classmethod
    def from_dict(cls, d: dict) -> "Card":
        """Create card from dictionary."""
        return cls(rank=d["rank"], suit=d["suit"])

    def __repr__(self) -> str:
        return f"Card(rank={self.rank}, suit='{self.suit}')"


class Deck:
    """Manages a deck or shoe of cards."""

    def __init__(self, num_decks: int = 1):
        """Initialize a deck.
        
        Args:
            num_decks: Number of decks in the shoe (default: 1)
        """
        self._cards: List[Card] = []
        self.num_decks = num_decks
        self.reset()

    def reset(self) -> None:
        """Reset and shuffle the deck."""
        self._cards = []
        for _ in range(self.num_decks):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self._cards.append(Card(rank=rank, suit=suit))
        random.shuffle(self._cards)

    def draw(self) -> Card:
        """Draw a card from the deck.
        
        Returns:
            The drawn card
            
        Raises:
            IndexError: If deck is empty
        """
        if not self._cards:
            self.reset()
        return self._cards.pop()

    @property
    def remaining_cards(self) -> int:
        """Get number of cards remaining in the deck."""
        return len(self._cards)

    def __len__(self) -> int:
        """Get number of cards in deck."""
        return len(self._cards)


class Hand:
    """Represents a player's or dealer's hand of cards."""

    def __init__(self):
        """Initialize an empty hand."""
        self.cards: List[Card] = []
        self.stood: bool = False
        self.double: bool = False
        self.split: bool = False
        self.surrendered: bool = False
        self._total: Optional[int] = None
        self._is_soft: Optional[bool] = None

    @property
    def total(self) -> int:
        """Calculate hand total with optimal ace counting."""
        if self._total is not None:
            return self._total

        total = 0
        aces = 0

        for card in self.cards:
            total += card.value
            if card.is_ace:
                aces += 1

        # Count aces as 11 if it doesn't bust, otherwise 1
        while total <= 21 and aces > 0:
            if total + 10 <= 21:
                total += 10
                aces -= 1

        self._total = total
        return total

    @property
    def is_soft(self) -> bool:
        """Check if hand is soft (has an ace counted as 11)."""
        if not any(card.is_ace for card in self.cards):
            return False
        
        # Calculate if ace is being counted as 11
        total = sum(card.value for card in self.cards)
        aces = sum(1 for card in self.cards if card.is_ace)
        
        # Count aces as 11 if it doesn't bust
        while total <= 21 and aces > 0:
            if total + 10 <= 21:
                return True
            aces -= 1
        
        return False

    @property
    def is_blackjack(self) -> bool:
        """Check if hand is a natural blackjack."""
        return len(self.cards) == 2 and self.total == 21

    @property
    def is_bust(self) -> bool:
        """Check if hand has busted."""
        return self.total > 21

    @property
    def is_pair(self) -> bool:
        """Check if hand is a pair."""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    @property
    def pair_rank(self) -> Optional[int]:
        """Get the rank of the pair if hand is a pair."""
        if self.is_pair:
            return self.cards[0].rank
        return None

    @property
    def can_double(self) -> bool:
        """Check if hand can be doubled (only 2 cards and not already doubled)."""
        return len(self.cards) == 2 and not self.double

    @property
    def can_split(self) -> bool:
        """Check if hand can be split (only 2 cards and is a pair)."""
        return self.is_pair

    def add_card(self, card: Card) -> None:
        """Add a card to the hand.
        
        Args:
            card: The card to add
        """
        self.cards.append(card)
        self._total = None  # Reset cached total
        self._is_soft = None  # Reset cached soft status

    def reset(self) -> None:
        """Reset the hand to empty state."""
        self.cards = []
        self.stood = False
        self.double = False
        self.split = False
        self.surrendered = False
        self._total = None
        self._is_soft = None

    def to_dict(self) -> dict:
        """Convert hand to dictionary."""
        return {
            "cards": [card.to_dict() for card in self.cards],
            "total": self.total,
            "soft": self.is_soft,
            "blackjack": self.is_blackjack,
            "bust": self.is_bust,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Hand":
        """Create hand from dictionary."""
        hand = cls()
        hand.cards = [Card.from_dict(cd) for cd in d["cards"]]
        hand._total = d["total"]
        return hand


class GameStatus(Enum):
    """Possible game states."""

    IDLE = "IDLE"
    PLAYER_TURN = "PLAYER_TURN"
    DEALER_TURN = "DEALER_TURN"
    WIN = "WIN"
    LOSS = "LOSS"
    PUSH = "PUSH"
    BUST = "BUST"
    BLACKJACK = "BLACKJACK"
    FOLD = "FOLD"


class BlackjackResult(Enum):
    """Possible blackjack game outcomes."""

    WIN = 1.0
    BLACKJACK = 1.5
    PUSH = 0.0
    LOSS = -1.0
    BUST = -1.0
    SURRENDER = -0.5


@dataclass
class BlackjackResultData:
    """Data class for tracking individual game results."""

    outcome: BlackjackResult
    bet: float
    payout: float
    net_result: float

    def to_dict(self) -> dict:
        """Convert result data to dictionary."""
        return {
            "outcome": self.outcome.name,
            "bet": self.bet,
            "payout": self.payout,
            "net_result": self.net_result,
        }


class SimulatorStats:
    """Statistics tracking for blackjack simulations."""

    def __init__(self):
        """Initialize statistics tracker."""
        self.total_episodes: int = 0
        self.total_wins: int = 0
        self.total_losses: int = 0
        self.total_pushes: int = 0
        self.total_blackjacks: int = 0
        self.total_busts: int = 0
        self.total_surrenders: int = 0
        self.total_bet: float = 0.0
        self.total_payout: float = 0.0

    def update(self, outcome: BlackjackResult, bet: float = 1.0) -> None:
        """Update statistics with a new result.
        
        Args:
            outcome: The game outcome
            bet: The bet amount for this game
        """
        self.total_episodes += 1
        self.total_bet += bet

        if outcome == BlackjackResult.WIN:
            self.total_wins += 1
            self.total_payout += bet * outcome.value
        elif outcome == BlackjackResult.BLACKJACK:
            self.total_blackjacks += 1
            self.total_payout += bet * outcome.value
        elif outcome == BlackjackResult.PUSH:
            self.total_pushes += 1
            self.total_payout += bet
        elif outcome == BlackjackResult.LOSS:
            self.total_losses += 1
        elif outcome == BlackjackResult.BUST:
            self.total_busts += 1
        elif outcome == BlackjackResult.SURRENDER:
            self.total_surrenders += 1
            self.total_payout += bet * outcome.value

    @property
    def win_rate(self) -> float:
        """Get win rate."""
        if self.total_episodes == 0:
            return 0.0
        return self.total_wins / self.total_episodes

    @property
    def loss_rate(self) -> float:
        """Get loss rate."""
        if self.total_episodes == 0:
            return 0.0
        return self.total_losses / self.total_episodes

    @property
    def push_rate(self) -> float:
        """Get push rate."""
        if self.total_episodes == 0:
            return 0.0
        return self.total_pushes / self.total_episodes

    @property
    def blackjack_rate(self) -> float:
        """Get blackjack rate."""
        if self.total_episodes == 0:
            return 0.0
        return self.total_blackjacks / self.total_episodes

    @property
    def bust_rate(self) -> float:
        """Get bust rate."""
        if self.total_episodes == 0:
            return 0.0
        return self.total_busts / self.total_episodes

    @property
    def surrender_rate(self) -> float:
        """Get surrender rate."""
        if self.total_episodes == 0:
            return 0.0
        return self.total_surrenders / self.total_episodes

    @property
    def roi(self) -> float:
        """Get return on investment."""
        if self.total_bet == 0:
            return 0.0
        return (self.total_payout - self.total_bet) / self.total_bet

    def reset(self) -> None:
        """Reset all statistics."""
        self.total_episodes = 0
        self.total_wins = 0
        self.total_losses = 0
        self.total_pushes = 0
        self.total_blackjacks = 0
        self.total_busts = 0
        self.total_surrenders = 0
        self.total_bet = 0.0
        self.total_payout = 0.0

    def to_dict(self) -> dict:
        """Convert statistics to dictionary."""
        return {
            "total_episodes": self.total_episodes,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "total_pushes": self.total_pushes,
            "total_blackjacks": self.total_blackjacks,
            "total_busts": self.total_busts,
            "total_surrenders": self.total_surrenders,
            "win_rate": self.win_rate,
            "loss_rate": self.loss_rate,
            "push_rate": self.push_rate,
            "blackjack_rate": self.blackjack_rate,
            "bust_rate": self.bust_rate,
            "surrender_rate": self.surrender_rate,
            "roi": self.roi,
            "total_bet": self.total_bet,
            "total_payout": self.total_payout,
        }


class BlackjackGame:
    """Main blackjack game class."""

    def __init__(self, num_decks: int = 6, dealer_stands_soft_17: bool = True):
        """Initialize a blackjack game.
        
        Args:
            num_decks: Number of decks in the shoe (default: 6)
            dealer_stands_soft_17: Whether dealer stands on soft 17 (default: True)
        """
        self.deck = Deck(num_decks=num_decks)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.status = GameStatus.IDLE
        self.result: Optional[BlackjackResultData] = None
        self.dealer_stands_soft_17 = dealer_stands_soft_17
        self.dealer_upcard: Optional[Card] = None

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.player_hand.reset()
        self.dealer_hand.reset()
        self.status = GameStatus.IDLE
        self.result = None
        self.dealer_upcard = None

    def deal_initial_cards(self) -> BlackjackResultData:
        """Deal initial cards to player and dealer.
        
        Returns:
            BlackjackResultData with the result of the initial deal
        """
        self.reset()
        
        # Deal 2 cards to each
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        self.player_hand.add_card(self.deck.draw())
        self.dealer_hand.add_card(self.deck.draw())
        
        # Set dealer upcard
        self.dealer_upcard = self.dealer_hand.cards[0]
        
        # Check for player blackjack
        if self.player_hand.is_blackjack:
            self.status = GameStatus.BLACKJACK
            bet = 1.0
            self.result = BlackjackResultData(
                outcome=BlackjackResult.BLACKJACK,
                bet=bet,
                payout=bet * 1.5,
                net_result=bet * 0.5
            )
            return self.result
        else:
            self.status = GameStatus.PLAYER_TURN
            # Return push for initial deal if no blackjack
            bet = 1.0
            self.result = BlackjackResultData(
                outcome=BlackjackResult.PUSH,
                bet=bet,
                payout=bet,
                net_result=0.0
            )
            return self.result

    def player_hit(self) -> None:
        """Player hits (takes another card)."""
        if self.status != GameStatus.PLAYER_TURN:
            raise ValueError("Cannot hit - not player's turn")
        
        self.player_hand.add_card(self.deck.draw())
        
        if self.player_hand.is_bust:
            self.status = GameStatus.BUST
        elif self.player_hand.is_blackjack:
            self.status = GameStatus.BLACKJACK
        else:
            self.status = GameStatus.PLAYER_TURN

    def player_stand(self) -> None:
        """Player stands (ends their turn)."""
        if self.status != GameStatus.PLAYER_TURN:
            raise ValueError("Cannot stand - not player's turn")
        
        self.player_hand.stood = True
        self.status = GameStatus.DEALER_TURN

    def player_double(self) -> None:
        """Player doubles their bet and takes one card."""
        if self.status != GameStatus.PLAYER_TURN:
            raise ValueError("Cannot double - not player's turn")
        
        self.player_hand.double = True
        self.player_hit()
        self.status = GameStatus.DEALER_TURN

    def player_surrender(self) -> None:
        """Player surrenders (gives up half their bet)."""
        if self.status != GameStatus.PLAYER_TURN:
            raise ValueError("Cannot surrender - not player's turn")
        
        self.player_hand.surrendered = True
        self.status = GameStatus.FOLD

    def dealer_play(self) -> None:
        """Dealer plays their hand."""
        if self.status != GameStatus.DEALER_TURN:
            raise ValueError("Cannot dealer play - not dealer's turn")
        
        while True:
            # Check if dealer should hit
            should_hit = False
            
            if self.dealer_hand.total < 17:
                should_hit = True
            elif self.dealer_hand.total == 17:
                if self.dealer_stands_soft_17:
                    if self.dealer_hand.is_soft:
                        should_hit = False
                    else:
                        should_hit = False
                else:
                    should_hit = True
            else:
                should_hit = False
            
            if should_hit:
                self.dealer_hand.add_card(self.deck.draw())
            else:
                self.dealer_hand.stood = True
                break

    def determine_result(self) -> None:
        """Determine the game result."""
        if self.status in [GameStatus.BUST, GameStatus.FOLD]:
            return
        
        if self.player_hand.is_blackjack:
            if self.dealer_hand.is_blackjack:
                self.status = GameStatus.PUSH
            else:
                self.status = GameStatus.BLACKJACK
        elif self.player_hand.is_bust:
            self.status = GameStatus.BUST
        elif self.dealer_hand.is_bust:
            self.status = GameStatus.WIN
        elif self.player_hand.total > self.dealer_hand.total:
            self.status = GameStatus.WIN
        elif self.player_hand.total < self.dealer_hand.total:
            self.status = GameStatus.LOSS
        else:
            self.status = GameStatus.PUSH

    def play_round(self) -> BlackjackResult:
        """Play a complete round of blackjack.
        
        Returns:
            The game result
        """
        self.deal_initial_cards()
        
        # Player turn
        while self.status == GameStatus.PLAYER_TURN:
            # Simple strategy: hit on soft 17 or less, stand on hard 17 or more
            if self.player_hand.total < 17:
                self.player_hit()
            else:
                self.player_stand()
        
        # Dealer turn
        if self.status == GameStatus.DEALER_TURN:
            self.dealer_play()
        
        # Determine result
        self.determine_result()
        
        # Calculate result data
        bet = 1.0
        if self.status == GameStatus.WIN:
            self.result = BlackjackResultData(
                outcome=BlackjackResult.WIN,
                bet=bet,
                payout=bet,
                net_result=bet
            )
        elif self.status == GameStatus.BLACKJACK:
            self.result = BlackjackResultData(
                outcome=BlackjackResult.BLACKJACK,
                bet=bet,
                payout=bet * 1.5,
                net_result=bet * 0.5
            )
        elif self.status == GameStatus.PUSH:
            self.result = BlackjackResultData(
                outcome=BlackjackResult.PUSH,
                bet=bet,
                payout=bet,
                net_result=0.0
            )
        elif self.status == GameStatus.LOSS:
            self.result = BlackjackResultData(
                outcome=BlackjackResult.LOSS,
                bet=bet,
                payout=0.0,
                net_result=-bet
            )
        elif self.status == GameStatus.BUST:
            self.result = BlackjackResultData(
                outcome=BlackjackResult.BUST,
                bet=bet,
                payout=0.0,
                net_result=-bet
            )
        elif self.status == GameStatus.FOLD:
            self.result = BlackjackResultData(
                outcome=BlackjackResult.SURRENDER,
                bet=bet,
                payout=bet * 0.5,
                net_result=-bet * 0.5
            )
        
        return self.result.outcome

    def get_player_hand(self) -> Hand:
        """Get player's hand."""
        return self.player_hand

    def get_dealer_hand(self) -> Hand:
        """Get dealer's hand."""
        return self.dealer_hand

    def get_dealer_upcard(self) -> Optional[Card]:
        """Get dealer's upcard."""
        return self.dealer_upcard

    def get_status(self) -> GameStatus:
        """Get current game status."""
        return self.status

    def get_result(self) -> Optional[BlackjackResultData]:
        """Get game result."""
        return self.result
