"""Tests for the TickerPanel and TickerBoard display components."""

from __future__ import annotations

import pytest
from src.ticker_display import TickerPanel, TickerBoard
from src.ticker import Ticker


class TestTickerPanel:
    """Tests for TickerPanel creation and properties."""

    def test_create_panel_with_ticker(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        assert panel.ticker == ticker
        assert panel.is_selected is False
        assert panel.is_highlighted is False
        assert panel.position == (0.0, 0.0, 0.0)
        assert panel.size == (1.0, 0.6, 0.05)

    def test_create_panel_with_custom_position(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, position=(1.0, 2.0, 3.0))
        assert panel.position == (1.0, 2.0, 3.0)

    def test_create_panel_with_custom_size(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, size=(2.0, 1.0, 0.1))
        assert panel.size == (2.0, 1.0, 0.1)

    def test_create_panel_with_custom_rotation(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, rotation=(0.0, 45.0, 0.0))
        assert panel.rotation == (0.0, 45.0, 0.0)

    def test_create_panel_with_custom_colors(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(
            ticker,
            color=(1.0, 0.0, 0.0),
            background_color=(0.0, 1.0, 0.0),
            text_color=(0.0, 0.0, 1.0),
        )
        assert panel.color == (1.0, 0.0, 0.0)
        assert panel.background_color == (0.0, 1.0, 0.0)
        assert panel.text_color == (0.0, 0.0, 1.0)

    def test_panel_gets_colors_from_ticker(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=5.0, change_percent=5.0)
        panel = TickerPanel(ticker)
        assert panel.color == (0.0, 1.0, 0.0)  # Green for positive
        assert panel.background_color == (0.0, 0.5, 0.0)  # Dark green

    def test_panel_gets_colors_from_ticker_negative(self):
        ticker = Ticker(symbol="AAPL", price=100.0, change=-5.0, change_percent=-5.0)
        panel = TickerPanel(ticker)
        assert panel.color == (1.0, 0.0, 0.0)  # Red for negative
        assert panel.background_color == (0.5, 0.0, 0.0)  # Dark red


class TestTickerPanelState:
    """Tests for TickerPanel state management."""

    def test_select_panel(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        panel.select()
        assert panel.is_selected is True
        assert panel.is_highlighted is True

    def test_deselect_panel(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        panel.select()
        panel.deselect()
        assert panel.is_selected is False
        assert panel.is_highlighted is False

    def test_toggle_panel(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        panel.toggle()
        assert panel.is_selected is True
        panel.toggle()
        assert panel.is_selected is False

    def test_highlight_panel(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        panel.highlight()
        assert panel.is_highlighted is True
        panel.unhighlight()
        assert panel.is_highlighted is False

    def test_panel_update_with_new_ticker(self):
        ticker1 = Ticker(symbol="AAPL", price=100.0)
        ticker2 = Ticker(symbol="AAPL", price=105.0)
        panel = TickerPanel(ticker1)
        panel.update_ticker(ticker2)
        assert panel.ticker == ticker2
        assert panel.ticker.price == 105.0

    def test_panel_update_with_same_ticker(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        panel.update_ticker(ticker)
        assert panel.ticker == ticker
        assert panel.ticker.price == 100.0


class TestTickerPanelSerialization:
    """Tests for TickerPanel serialization."""

    def test_to_dict(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, position=(1.0, 2.0, 3.0))
        data = panel.to_dict()
        assert data["ticker"]["symbol"] == "AAPL"
        assert data["position"] == [1.0, 2.0, 3.0]
        assert data["size"] == [1.0, 0.6, 0.05]
        assert data["rotation"] == [0.0, 0.0, 0.0]
        assert data["is_selected"] is False
        assert data["is_highlighted"] is False

    def test_from_dict(self):
        data = {
            "ticker": {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 100.0,
                "change": 5.0,
                "change_percent": 5.0,
            },
            "position": [1.0, 2.0, 3.0],
            "size": [2.0, 1.0, 0.1],
            "rotation": [0.0, 45.0, 0.0],
            "is_selected": True,
            "is_highlighted": False,
        }
        panel = TickerPanel.from_dict(data)
        assert panel.ticker.symbol == "AAPL"
        assert panel.position == (1.0, 2.0, 3.0)
        assert panel.size == (2.0, 1.0, 0.1)
        assert panel.rotation == (0.0, 45.0, 0.0)
        assert panel.is_selected is True
        assert panel.is_highlighted is False

    def test_round_trip(self):
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, position=(1.0, 2.0, 3.0))
        data = panel.to_dict()
        panel2 = TickerPanel.from_dict(data)
        assert panel.ticker.symbol == panel2.ticker.symbol
        assert panel.position == panel2.position
        assert panel.size == panel2.size
        assert panel.rotation == panel2.rotation
        assert panel.is_selected == panel2.is_selected
        assert panel.is_highlighted == panel2.is_highlighted


class TestTickerBoard:
    """Tests for TickerBoard creation and management."""

    def test_create_board(self):
        board = TickerBoard()
        assert board.name == "Board 1"
        assert board.size == (10.0, 6.0, 0.05)
        assert board.position == (0.0, 1.6, 0.0)
        assert board.rotation == (0.0, 0.0, 0.0)
        assert len(board.panels) == 0

    def test_create_board_with_custom_name(self):
        board = TickerBoard(name="My Board")
        assert board.name == "My Board"

    def test_create_board_with_custom_size(self):
        board = TickerBoard(size=(20.0, 10.0, 0.1))
        assert board.size == (20.0, 10.0, 0.1)

    def test_add_panel(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        board.add_panel(panel)
        assert len(board.panels) == 1
        assert board.panels[0] == panel

    def test_add_multiple_panels(self):
        board = TickerBoard()
        for i in range(5):
            ticker = Ticker(symbol=f"SYM{i}", price=100.0)
            panel = TickerPanel(ticker)
            board.add_panel(panel)
        assert len(board.panels) == 5

    def test_remove_panel(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        board.add_panel(panel)
        board.remove_panel("AAPL")
        assert len(board.panels) == 0

    def test_remove_nonexistent_panel(self):
        board = TickerBoard()
        result = board.remove_panel("AAPL")
        assert result is False

    def test_get_panel(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        board.add_panel(panel)
        result = board.get_panel("AAPL")
        assert result == panel

    def test_get_nonexistent_panel(self):
        board = TickerBoard()
        result = board.get_panel("AAPL")
        assert result is None

    def test_update_panels_with_ticker(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        board.add_panel(panel)
        new_ticker = Ticker(symbol="AAPL", price=105.0)
        board.update_panel("AAPL", new_ticker)
        assert panel.ticker.price == 105.0

    def test_update_nonexistent_panel(self):
        board = TickerBoard()
        result = board.update_panel("AAPL", Ticker(symbol="AAPL", price=105.0))
        assert result is False

    def test_get_all_ticker_symbols(self):
        board = TickerBoard()
        for i in range(3):
            ticker = Ticker(symbol=f"SYM{i}", price=100.0)
            panel = TickerPanel(ticker)
            board.add_panel(panel)
        symbols = board.get_all_ticker_symbols()
        assert len(symbols) == 3
        assert "SYM0" in symbols
        assert "SYM1" in symbols
        assert "SYM2" in symbols

    def test_get_panel_at_position(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, position=(1.0, 1.0, 0.0))
        board.add_panel(panel)
        result = board.get_panel_at_position((1.0, 1.0, 0.0))
        assert result == panel

    def test_get_panel_at_position_not_found(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker, position=(1.0, 1.0, 0.0))
        board.add_panel(panel)
        result = board.get_panel_at_position((2.0, 2.0, 0.0))
        assert result is None

    def test_get_selected_panel(self):
        board = TickerBoard()
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        panel.select()
        board.add_panel(panel)
        result = board.get_selected_panel()
        assert result == panel

    def test_get_selected_panel_none(self):
        board = TickerBoard()
        result = board.get_selected_panel()
        assert result is None

    def test_clear_panels(self):
        board = TickerBoard()
        for i in range(3):
            ticker = Ticker(symbol=f"SYM{i}", price=100.0)
            panel = TickerPanel(ticker)
            board.add_panel(panel)
        board.clear_panels()
        assert len(board.panels) == 0

    def test_board_to_dict(self):
        board = TickerBoard(name="Test Board")
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        board.add_panel(panel)
        data = board.to_dict()
        assert data["name"] == "Test Board"
        assert len(data["panels"]) == 1
        assert data["panels"][0]["ticker"]["symbol"] == "AAPL"

    def test_board_from_dict(self):
        data = {
            "name": "Test Board",
            "size": [20.0, 10.0, 0.1],
            "position": [1.0, 2.0, 3.0],
            "rotation": [0.0, 45.0, 0.0],
            "panels": [
                {
                    "ticker": {
                        "symbol": "AAPL",
                        "name": "Apple Inc.",
                        "price": 100.0,
                        "change": 5.0,
                        "change_percent": 5.0,
                    },
                    "position": [0.0, 0.0, 0.0],
                    "size": [1.0, 0.6, 0.05],
                    "rotation": [0.0, 0.0, 0.0],
                    "is_selected": True,
                    "is_highlighted": False,
                }
            ],
        }
        board = TickerBoard.from_dict(data)
        assert board.name == "Test Board"
        assert board.size == (20.0, 10.0, 0.1)
        assert board.position == (1.0, 2.0, 3.0)
        assert board.rotation == (0.0, 45.0, 0.0)
        assert len(board.panels) == 1
        assert board.panels[0].ticker.symbol == "AAPL"
        assert board.panels[0].is_selected is True

    def test_board_round_trip(self):
        board = TickerBoard(name="Test Board")
        ticker = Ticker(symbol="AAPL", price=100.0)
        panel = TickerPanel(ticker)
        board.add_panel(panel)
        data = board.to_dict()
        board2 = TickerBoard.from_dict(data)
        assert board.name == board2.name
        assert board.size == board2.size
        assert board.position == board2.position
        assert board.rotation == board2.rotation
        assert len(board.panels) == len(board2.panels)
        assert board.panels[0].ticker.symbol == board2.panels[0].ticker.symbol
