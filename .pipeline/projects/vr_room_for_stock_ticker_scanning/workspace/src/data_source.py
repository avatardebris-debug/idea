"""Abstract data source interface for stock ticker data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.ticker import Ticker


class DataSource(ABC):
    """Abstract base class for stock ticker data sources."""

    @abstractmethod
    def get_tickers(self, symbols: Optional[List[str]] = None) -> List[Ticker]:
        """Fetch ticker data for given symbols (or all if None)."""
        ...

    @abstractmethod
    def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Fetch a single ticker by symbol."""
        ...

    @abstractmethod
    def update_ticker(self, ticker: Ticker) -> None:
        """Update a ticker with new data."""
        ...

    @abstractmethod
    def subscribe(self, callback: callable) -> None:
        """Subscribe to real-time updates."""
        ...

    @abstractmethod
    def unsubscribe(self, callback: callable) -> None:
        """Unsubscribe from real-time updates."""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if data source is connected."""
        ...

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the data source."""
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the data source."""
        ...
