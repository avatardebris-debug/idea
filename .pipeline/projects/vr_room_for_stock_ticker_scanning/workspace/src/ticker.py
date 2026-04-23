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

    def update_price(self, new_price: float) -> None:
        """Update the ticker with a new price."""
        self.previous_close = self.price
        self.price = new_price
        self.change = self.price - self.open_price
        self.change_percent = (self.change / self.open_price * 100) if self.open_price != 0 else 0
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
