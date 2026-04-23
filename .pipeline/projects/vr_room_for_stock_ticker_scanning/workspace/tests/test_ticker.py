"""Tests for the Ticker data model."""

from __future__ import annotations

import pytest
from src.ticker import Ticker


class TestTickerCreation:
    """Tests for Ticker instantiation."""

    def test_create_ticker_with_all_fields(self):
        ticker = Ticker(
            symbol="AAPL",
            name="Apple Inc.",
            price=178.72,
            change=2.34,
            change_percent=1.33,
        )
        assert ticker.symbol == "AAPL"
        assert ticker.name == "Apple Inc."
        assert ticker.price == 178.72
        assert ticker.change == 2.34
        assert ticker.change_percent == 1.33

    def test_create_ticker_with_defaults(self):
        ticker = Ticker(symbol="GOOGL")
        assert ticker.symbol == "GOOGL"
        assert ticker.name == ""
        assert ticker.price == 0.0
        assert ticker.change == 0.0
        assert ticker.change_percent == 0.0

    def test_create_ticker_with_zero_price(self):
        ticker = Ticker(symbol="ZERO", price=0.0)
        assert ticker.price == 0.0
        assert ticker.change == 0.0
        assert ticker.change_percent == 0.0

    def test_create_ticker_with_negative_price(self):
        ticker = Ticker(symbol="NEG", price=-10.0)
        assert ticker.price == -10.0

    def test_create_ticker_with_large_values(self):
        ticker = Ticker(
            symbol="LARGE",
            price=999999.99,
            change=99999.99,
            change_percent=999.99,
        )
        assert ticker.price == 999999.99
        assert ticker.change == 99999.99
        assert ticker.change_percent == 999.99


class TestTickerUpdate:
    """Tests for Ticker update functionality."""

    def test_update_price(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        ticker.update_price(105.0)
        assert ticker.price == 105.0
        assert ticker.change == 5.0
        assert ticker.change_percent == 5.0

    def test_update_price_decrease(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        ticker.update_price(95.0)
        assert ticker.price == 95.0
        assert ticker.change == -5.0
        assert ticker.change_percent == -5.0

    def test_update_price_no_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        ticker.update_price(100.0)
        assert ticker.price == 100.0
        assert ticker.change == 0.0
        assert ticker.change_percent == 0.0

    def test_update_price_with_custom_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        ticker.update_price(110.0, change=10.0, change_percent=10.0)
        assert ticker.price == 110.0
        assert ticker.change == 10.0
        assert ticker.change_percent == 10.0

    def test_update_price_with_negative_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        ticker.update_price(90.0, change=-10.0, change_percent=-10.0)
        assert ticker.price == 90.0
        assert ticker.change == -10.0
        assert ticker.change_percent == -10.0


class TestTickerProperties:
    """Tests for Ticker properties."""

    def test_is_positive_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=5.0, change_percent=5.0)
        assert ticker.is_positive_change is True

    def test_is_negative_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=-5.0, change_percent=-5.0)
        assert ticker.is_negative_change is True

    def test_is_no_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=0.0, change_percent=0.0)
        assert ticker.is_positive_change is False
        assert ticker.is_negative_change is False

    def test_price_color_positive(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=5.0, change_percent=5.0)
        assert ticker.price_color == (0.0, 1.0, 0.0)

    def test_price_color_negative(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=-5.0, change_percent=-5.0)
        assert ticker.price_color == (1.0, 0.0, 0.0)

    def test_price_color_no_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=0.0, change_percent=0.0)
        assert ticker.price_color == (1.0, 1.0, 1.0)

    def test_background_color_positive(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=5.0, change_percent=5.0)
        assert ticker.background_color == (0.0, 0.5, 0.0)

    def test_background_color_negative(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=-5.0, change_percent=-5.0)
        assert ticker.background_color == (0.5, 0.0, 0.0)

    def test_background_color_no_change(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=0.0, change_percent=0.0)
        assert ticker.background_color == (0.2, 0.2, 0.2)


class TestTickerSerialization:
    """Tests for Ticker serialization."""

    def test_to_dict(self):
        ticker = Ticker(
            symbol="AAPL",
            name="Apple Inc.",
            price=178.72,
            change=2.34,
            change_percent=1.33,
        )
        data = ticker.to_dict()
        assert data["symbol"] == "AAPL"
        assert data["name"] == "Apple Inc."
        assert data["price"] == 178.72
        assert data["change"] == 2.34
        assert data["change_percent"] == 1.33

    def test_from_dict(self):
        data = {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "price": 178.72,
            "change": 2.34,
            "change_percent": 1.33,
        }
        ticker = Ticker.from_dict(data)
        assert ticker.symbol == "AAPL"
        assert ticker.name == "Apple Inc."
        assert ticker.price == 178.72
        assert ticker.change == 2.34
        assert ticker.change_percent == 1.33

    def test_round_trip(self):
        ticker = Ticker(
            symbol="AAPL",
            name="Apple Inc.",
            price=178.72,
            change=2.34,
            change_percent=1.33,
        )
        data = ticker.to_dict()
        ticker2 = Ticker.from_dict(data)
        assert ticker.symbol == ticker2.symbol
        assert ticker.name == ticker2.name
        assert ticker.price == ticker2.price
        assert ticker.change == ticker2.change
        assert ticker.change_percent == ticker2.change_percent

    def test_from_dict_with_missing_fields(self):
        data = {"symbol": "AAPL"}
        ticker = Ticker.from_dict(data)
        assert ticker.symbol == "AAPL"
        assert ticker.name == ""
        assert ticker.price == 0.0
        assert ticker.change == 0.0
        assert ticker.change_percent == 0.0


class TestTickerEquality:
    """Tests for Ticker equality."""

    def test_equal_tickers(self):
        t1 = Ticker(symbol="AAPL", price=100.0)
        t2 = Ticker(symbol="AAPL", price=100.0)
        assert t1 == t2

    def test_different_symbols(self):
        t1 = Ticker(symbol="AAPL", price=100.0)
        t2 = Ticker(symbol="GOOGL", price=100.0)
        assert t1 != t2

    def test_different_prices(self):
        t1 = Ticker(symbol="AAPL", price=100.0)
        t2 = Ticker(symbol="AAPL", price=105.0)
        assert t1 != t2

    def test_different_changes(self):
        t1 = Ticker(symbol="AAPL", price=100.0, change=5.0)
        t2 = Ticker(symbol="AAPL", price=100.0, change=-5.0)
        assert t1 != t2
