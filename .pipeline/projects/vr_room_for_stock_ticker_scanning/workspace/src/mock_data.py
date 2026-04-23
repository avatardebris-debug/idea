"""Mock data source — simulates real-time stock ticker data with realistic price movements."""

from __future__ import annotations

import math
import random
import time
from typing import Callable, List, Optional

from src.data_source import DataSource
from src.ticker import Ticker


class MockDataSource(DataSource):
    """Simulates real-time stock ticker data with realistic price movements."""

    def __init__(self, update_interval: float = 1.0, volatility: float = 0.02):
        """
        Initialize mock data source.

        Args:
            update_interval: Seconds between price updates
            volatility: Price volatility (higher = more movement)
        """
        self._tickers: dict[str, Ticker] = {}
        self._callbacks: List[Callable] = []
        self._update_interval = update_interval
        self._volatility = volatility
        self._connected = False
        self._last_update = 0.0
        self._running = False
        self._thread = None

    def _generate_initial_ticker(self, symbol: str) -> Ticker:
        """Generate a realistic initial ticker."""
        # Base price between 10 and 1000
        base_price = random.uniform(10, 1000)
        # Generate realistic-looking name
        prefixes = ["Tech", "Global", "United", "Pacific", "Atlantic", "Nova", "Apex", "Zenith"]
        suffixes = ["Corp", "Industries", "Systems", "Solutions", "Capital", "Holdings", "Group"]
        name = f"{random.choice(prefixes)} {random.choice(suffixes)}"

        return Ticker(
            symbol=symbol,
            name=name,
            price=base_price,
            previous_close=base_price * random.uniform(0.95, 1.05),
            open_price=base_price,
            high=base_price * random.uniform(1.0, 1.1),
            low=base_price * random.uniform(0.9, 1.0),
            volume=random.randint(100000, 10000000),
            market_cap=base_price * random.randint(1000000, 100000000),
            pe_ratio=random.uniform(10, 50),
            dividend_yield=random.uniform(0, 5),
            currency="USD",
            exchange="NASDAQ",
        )

    def add_ticker(self, symbol: str) -> Ticker:
        """Add a ticker to the mock data source."""
        if symbol not in self._tickers:
            self._tickers[symbol] = self._generate_initial_ticker(symbol)
        return self._tickers[symbol]

    def remove_ticker(self, symbol: str) -> bool:
        """Remove a ticker from the mock data source."""
        if symbol in self._tickers:
            del self._tickers[symbol]
            return True
        return False

    def get_tickers(self, symbols: Optional[List[str]] = None) -> List[Ticker]:
        """Fetch ticker data for given symbols (or all if None)."""
        if symbols:
            return [self._tickers[s] for s in symbols if s in self._tickers]
        return list(self._tickers.values())

    def get_ticker(self, symbol: str) -> Optional[Ticker]:
        """Fetch a single ticker by symbol."""
        return self._tickers.get(symbol)

    def update_ticker(self, ticker: Ticker) -> None:
        """Update a ticker with new data."""
        self._tickers[ticker.symbol] = ticker
        self._notify_subscribers(ticker)

    def subscribe(self, callback: Callable) -> None:
        """Subscribe to real-time updates."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable) -> None:
        """Unsubscribe from real-time updates."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_subscribers(self, ticker: Ticker) -> None:
        """Notify all subscribers of a ticker update."""
        for callback in self._callbacks:
            try:
                callback(ticker)
            except Exception:
                pass  # Ignore subscriber errors

    def _simulate_price_movement(self, ticker: Ticker) -> None:
        """Simulate realistic price movement for a ticker."""
        # Random walk with mean reversion
        drift = random.gauss(0, self._volatility)
        # Mean reversion to open price
        mean_reversion = (ticker.open_price - ticker.price) * 0.01
        # Trend component (slow drift)
        trend = math.sin(time.time() / 1000) * 0.001

        new_price = ticker.price * (1 + drift + mean_reversion + trend)
        new_price = max(0.01, new_price)  # Price can't be negative

        # Update volume
        new_volume = ticker.volume + random.randint(100, 10000)

        ticker.update_price(new_price)
        ticker.volume = new_volume

    def update_prices(self) -> List[Ticker]:
        """Update all ticker prices and return updated tickers."""
        updated = []
        for symbol, ticker in self._tickers.items():
            self._simulate_price_movement(ticker)
            updated.append(ticker)
            self._notify_subscribers(ticker)
        return updated

    def is_connected(self) -> bool:
        """Check if data source is connected."""
        return self._connected

    def connect(self) -> bool:
        """Connect to the mock data source."""
        self._connected = True
        self._running = True
        self._last_update = time.time()
        return True

    def disconnect(self) -> None:
        """Disconnect from the mock data source."""
        self._connected = False
        self._running = False

    def start(self) -> None:
        """Start the mock data source (simulates real-time updates)."""
        if self._running:
            return
        self._running = True
        self._last_update = time.time()

    def stop(self) -> None:
        """Stop the mock data source."""
        self._running = False

    def tick(self) -> List[Ticker]:
        """Simulate one tick of price updates (respects update_interval)."""
        if not self._running:
            return []

        now = time.time()
        if now - self._last_update < self._update_interval:
            return []

        self._last_update = now
        return self.update_prices()

    def force_update(self) -> List[Ticker]:
        """Force update all ticker prices (bypasses time throttling). Useful for testing."""
        self._last_update = time.time() - self._update_interval  # Allow immediate update
        return self.update_prices()

    def get_status(self) -> dict:
        """Get mock data source status."""
        return {
            "connected": self._connected,
            "running": self._running,
            "ticker_count": len(self._tickers),
            "tickers": list(self._tickers.keys()),
            "update_interval": self._update_interval,
            "volatility": self._volatility,
        }
