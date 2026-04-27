"""Ticker data model — represents a single stock ticker with price, change, volume, etc."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Ticker:
    """A single stock ticker with real-time price data."""

    symbol: str
    name: str = ""
    price: float = 0.0
    previous_close: float = 0.0
    open_price: float = 0.0
    high: float = 0.0
    low: float = 0.0
    volume: int = 0
    market_cap: float = 0.0
    pe_ratio: float = 0.0
    dividend_yield: float = 0.0
    change: float = 0.0       # absolute change from previous close
    change_percent: float = 0.0  # percentage change from previous close
    timestamp: float = field(default_factory=time.time)
    currency: str = "USD"
    exchange: str = ""

    @property
    def is_up(self) -> bool:
        """True if price is above previous close."""
        return self.change > 0

    @property
    def is_down(self) -> bool:
        """True if price is below previous close."""
        return self.change < 0

    @property
    def is_flat(self) -> bool:
        """True if price equals previous close."""
        return self.change == 0

    @property
    def is_positive_change(self) -> bool:
        """True if change is positive."""
        return self.change > 0

    @property
    def is_negative_change(self) -> bool:
        """True if change is negative."""
        return self.change < 0

    @property
    def price_color(self) -> tuple:
        """Get RGB color tuple for price text based on change."""
        if self.change > 0:
            return (0.0, 1.0, 0.0)  # Green
        elif self.change < 0:
            return (1.0, 0.0, 0.0)  # Red
        else:
            return (1.0, 1.0, 1.0)  # White

    @property
    def background_color(self) -> tuple:
        """Get RGB color tuple for background based on change."""
        if self.change > 0:
            return (0.0, 0.5, 0.0)  # Dark green
        elif self.change < 0:
            return (0.5, 0.0, 0.0)  # Dark red
        else:
            return (0.2, 0.2, 0.2)  # Gray

    def update_price(self, new_price: float, change: Optional[float] = None, change_percent: Optional[float] = None) -> None:
        """Update the ticker with a new price.
        
        Args:
            new_price: The new price value
            change: Optional explicit change value (overrides calculation)
            change_percent: Optional explicit change percent (overrides calculation)
        """
        self.previous_close = self.price
        self.price = new_price
        
        if change is not None:
            self.change = change
        else:
            self.change = self.price - self.previous_close
        
        if change_percent is not None:
            self.change_percent = change_percent
        elif self.previous_close != 0:
            self.change_percent = (self.change / self.previous_close) * 100
        else:
            self.change_percent = 0.0
        
        self.timestamp = time.time()
        # Update high/low
        if new_price > self.high:
            self.high = new_price
        if new_price < self.low:
            self.low = new_price

    def to_dict(self) -> dict:
        """Convert ticker to dictionary."""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "previous_close": self.previous_close,
            "open_price": self.open_price,
            "high": self.high,
            "low": self.low,
            "volume": self.volume,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "dividend_yield": self.dividend_yield,
            "change": self.change,
            "change_percent": self.change_percent,
            "timestamp": self.timestamp,
            "currency": self.currency,
            "exchange": self.exchange,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Ticker:
        """Create a Ticker from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def __repr__(self) -> str:
        return (
            f"Ticker({self.symbol}: ${self.price:.2f} "
            f"({self.change:+.2f}, {self.change_percent:+.2f}%))"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ticker):
            return NotImplemented
        return (
            self.symbol == other.symbol
            and self.price == other.price
            and self.change == other.change
        )
