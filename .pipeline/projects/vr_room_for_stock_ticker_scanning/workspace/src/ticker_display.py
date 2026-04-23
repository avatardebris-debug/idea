"""Ticker display system — renders stock tickers as 3D panels in VR."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional

from src.ticker import Ticker
from src.color_scheme import TickerColorScheme


@dataclass
class TickerPanel:
    """A 3D panel displaying a single ticker."""

    ticker: Ticker
    position: tuple = (0.0, 0.0, 0.0)
    size: tuple = (1.0, 0.6, 0.05)
    rotation: tuple = (0.0, 0.0, 0.0)
    is_selected: bool = False
    is_highlighted: bool = False

    @property
    def color(self) -> TickerColorScheme:
        """Get the display color for this panel."""
        return TickerColorScheme.get_price_color(self.ticker.change_percent)

    @property
    def background_color(self) -> TickerColorScheme:
        """Get the background color for this panel."""
        return TickerColorScheme.get_background_color(self.ticker.change_percent)

    @property
    def text_color(self) -> TickerColorScheme:
        """Get the text color for this panel."""
        return TickerColorScheme.get_text_color(self.ticker.change_percent)

    def update(self, ticker: Ticker) -> None:
        """Update the panel with new ticker data."""
        self.ticker = ticker

    def to_dict(self) -> dict:
        """Convert panel to dictionary for serialization."""
        return {
            "ticker": self.ticker.to_dict(),
            "position": self.position,
            "size": self.size,
            "rotation": self.rotation,
            "is_selected": self.is_selected,
            "is_highlighted": self.is_highlighted,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TickerPanel:
        """Create a panel from a dictionary."""
        ticker = Ticker.from_dict(data["ticker"])
        return cls(
            ticker=ticker,
            position=tuple(data["position"]),
            size=tuple(data["size"]),
            rotation=tuple(data["rotation"]),
            is_selected=data.get("is_selected", False),
            is_highlighted=data.get("is_highlighted", False),
        )


@dataclass
class TickerBoard:
    """A board containing multiple ticker panels."""

    panels: List[TickerPanel] = field(default_factory=list)
    position: tuple = (0.0, 1.6, -2.0)
    rotation: tuple = (0.0, 0.0, 0.0)
    panel_spacing: float = 1.2
    panel_size: tuple = (1.0, 0.6, 0.05)
    is_visible: bool = True
    is_locked: bool = False

    def add_panel(self, ticker: Ticker, index: Optional[int] = None) -> TickerPanel:
        """Add a ticker panel to the board."""
        panel = TickerPanel(
            ticker=ticker,
            size=self.panel_size,
            position=self._calculate_panel_position(len(self.panels)),
        )
        if index is not None:
            self.panels.insert(index, panel)
        else:
            self.panels.append(panel)
        return panel

    def remove_panel(self, ticker_symbol: str) -> bool:
        """Remove a panel by ticker symbol."""
        for i, panel in enumerate(self.panels):
            if panel.ticker.symbol == ticker_symbol:
                self.panels.pop(i)
                return True
        return False

    def update_panel(self, ticker_symbol: str, ticker: Ticker) -> bool:
        """Update a panel with new ticker data."""
        for panel in self.panels:
            if panel.ticker.symbol == ticker_symbol:
                panel.update(ticker)
                return True
        return False

    def get_panel(self, ticker_symbol: str) -> Optional[TickerPanel]:
        """Get a panel by ticker symbol."""
        for panel in self.panels:
            if panel.ticker.symbol == ticker_symbol:
                return panel
        return None

    def get_selected_panel(self) -> Optional[TickerPanel]:
        """Get the currently selected panel."""
        for panel in self.panels:
            if panel.is_selected:
                return panel
        return None

    def select_panel(self, ticker_symbol: str) -> bool:
        """Select a panel by ticker symbol."""
        for panel in self.panels:
            panel.is_selected = False
        for panel in self.panels:
            if panel.ticker.symbol == ticker_symbol:
                panel.is_selected = True
                return True
        return False

    def highlight_panel(self, ticker_symbol: str, duration: float = 2.0) -> bool:
        """Highlight a panel for a duration."""
        for panel in self.panels:
            if panel.ticker.symbol == ticker_symbol:
                panel.is_highlighted = True
                return True
        return False

    def clear_highlights(self) -> None:
        """Clear all panel highlights."""
        for panel in self.panels:
            panel.is_highlighted = False

    def _calculate_panel_position(self, index: int) -> tuple:
        """Calculate the position for a panel based on its index."""
        x = (index - (len(self.panels) - 1) / 2) * self.panel_spacing
        return (x, 0.0, 0.0)

    def to_dict(self) -> dict:
        """Convert board to dictionary for serialization."""
        return {
            "panels": [panel.to_dict() for panel in self.panels],
            "position": self.position,
            "rotation": self.rotation,
            "panel_spacing": self.panel_spacing,
            "panel_size": self.panel_size,
            "is_visible": self.is_visible,
            "is_locked": self.is_locked,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TickerBoard:
        """Create a board from a dictionary."""
        board = cls(
            position=tuple(data["position"]),
            rotation=tuple(data["rotation"]),
            panel_spacing=data.get("panel_spacing", 1.2),
            panel_size=tuple(data.get("panel_size", (1.0, 0.6, 0.05))),
            is_visible=data.get("is_visible", True),
            is_locked=data.get("is_locked", False),
        )
        board.panels = [TickerPanel.from_dict(p) for p in data["panels"]]
        return board

    def get_status(self) -> dict:
        """Get board status."""
        return {
            "panel_count": len(self.panels),
            "position": self.position,
            "rotation": self.rotation,
            "is_visible": self.is_visible,
            "is_locked": self.is_locked,
            "tickers": [panel.ticker.symbol for panel in self.panels],
        }
