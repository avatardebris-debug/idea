"""VR scene composition — manages the overall VR environment and rendering."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.ticker_display import TickerBoard, TickerPanel
from src.navigation import VRNavigator, CameraState
from src.interaction import VRInputHandler, InputEvent, InputEventType
from src.ticker import Ticker
from src.data_source import MockDataSource


@dataclass
class VRScene:
    """Represents the complete VR scene."""

    navigator: VRNavigator = field(default_factory=VRNavigator)
    input_handler: VRInputHandler = field(default_factory=VRInputHandler)
    data_source: Optional[MockDataSource] = None
    is_running: bool = False
    frame_rate: float = 60.0
    last_update_time: float = 0.0
    tickers: Dict[str, Ticker] = field(default_factory=dict)
    boards: Dict[str, TickerBoard] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize the scene."""
        self._register_input_callbacks()

    def _register_input_callbacks(self) -> None:
        """Register input event callbacks."""
        self.input_handler.register_callback(
            InputEventType.GAZE_END, self._handle_gaze_end
        )
        self.input_handler.register_callback(
            InputEventType.POINTER_CLICK, self._handle_pointer_click
        )
        self.input_handler.register_callback(
            InputEventType.SCROLL_UP, self._handle_scroll
        )
        self.input_handler.register_callback(
            InputEventType.SCROLL_DOWN, self._handle_scroll
        )
        self.input_handler.register_callback(
            InputEventType.NAVIGATE_LEFT, self._handle_navigate
        )
        self.input_handler.register_callback(
            InputEventType.NAVIGATE_RIGHT, self._handle_navigate
        )
        self.input_handler.register_callback(
            InputEventType.ZOOM_IN, self._handle_zoom
        )
        self.input_handler.register_callback(
            InputEventType.ZOOM_OUT, self._handle_zoom
        )
        self.input_handler.register_callback(
            InputEventType.BOARD_SWITCH, self._handle_board_switch
        )

    def _handle_gaze_end(self, event: InputEvent) -> None:
        """Handle gaze end event."""
        if event.target:
            # Select the ticker panel
            board = self.navigator.get_current_board()
            if board:
                board.select_panel(event.target)

    def _handle_pointer_click(self, event: InputEvent) -> None:
        """Handle pointer click event."""
        if event.target:
            # Check if it's a ticker symbol
            if event.target in self.tickers:
                # Zoom to the ticker
                self.navigator.zoom_to_panel(event.target)
            else:
                # Check if it's a board name
                if event.target in self.boards:
                    self.navigator.switch_board(event.target)

    def _handle_scroll(self, event: InputEvent) -> None:
        """Handle scroll event."""
        direction = "up" if event.event_type == InputEventType.SCROLL_UP else "down"
        board = self.navigator.get_current_board()
        if board:
            # Scroll through tickers
            if direction == "up":
                self._scroll_tickers(board, 1)
            else:
                self._scroll_tickers(board, -1)

    def _scroll_tickers(self, board: TickerBoard, direction: int) -> None:
        """Scroll through tickers in a board."""
        panels = board.panels
        if not panels:
            return

        # Find current selected panel
        selected_index = -1
        for i, panel in enumerate(panels):
            if panel.is_selected:
                selected_index = i
                break

        # Calculate new index
        new_index = selected_index + direction
        if new_index < 0:
            new_index = len(panels) - 1
        elif new_index >= len(panels):
            new_index = 0

        # Select the new panel
        if new_index >= 0 and new_index < len(panels):
            board.select_panel(panels[new_index].ticker.symbol)

    def _handle_navigate(self, event: InputEvent) -> None:
        """Handle navigation event."""
        direction = "left" if event.event_type == InputEventType.NAVIGATE_LEFT else "right"
        if direction == "left":
            self.navigator.navigate_left()
        else:
            self.navigator.navigate_right()

    def _handle_zoom(self, event: InputEvent) -> None:
        """Handle zoom event."""
        if event.event_type == InputEventType.ZOOM_IN:
            # Zoom in logic
            pass
        else:
            self.navigator.zoom_out()

    def _handle_board_switch(self, event: InputEvent) -> None:
        """Handle board switch event."""
        if event.target:
            self.navigator.switch_board(event.target)

    def add_ticker(self, ticker: Ticker) -> bool:
        """Add a ticker to the scene."""
        if ticker.symbol in self.tickers:
            return False

        self.tickers[ticker.symbol] = ticker

        # Add to current board
        board = self.navigator.get_current_board()
        if board:
            board.add_panel(ticker)
            self.boards[board.get_status()["position"]] = board

        return True

    def remove_ticker(self, ticker_symbol: str) -> bool:
        """Remove a ticker from the scene."""
        if ticker_symbol not in self.tickers:
            return False

        del self.tickers[ticker_symbol]

        # Remove from all boards
        for board in self.navigator._boards:
            board.remove_panel(ticker_symbol)

        return True

    def update_tickers(self) -> None:
        """Update all tickers with latest data."""
        if not self.data_source:
            return

        # Get updated tickers from data source
        updated_tickers = self.data_source.get_updated_tickers()

        for ticker in updated_tickers:
            if ticker.symbol in self.tickers:
                self.tickers[ticker.symbol] = ticker

                # Update in all boards
                for board in self.navigator._boards:
                    board.update_panel(ticker.symbol, ticker)

    def start(self) -> None:
        """Start the VR scene."""
        self.is_running = True
        self.last_update_time = time.time()

        # Initialize data source if not provided
        if not self.data_source:
            self.data_source = MockDataSource()
            self.data_source.start()

    def stop(self) -> None:
        """Stop the VR scene."""
        self.is_running = False
        if self.data_source:
            self.data_source.stop()

    def get_frame(self) -> dict:
        """Get the current VR frame for rendering."""
        if not self.is_running:
            return {}

        # Update tickers
        self.update_tickers()

        # Get camera state
        camera = self.navigator.get_camera_state()

        # Get current board
        board = self.navigator.get_current_board()

        # Get all panels
        panels = []
        if board:
            for panel in board.panels:
                panels.append({
                    "ticker": panel.ticker.to_dict(),
                    "position": panel.position,
                    "size": panel.size,
                    "rotation": panel.rotation,
                    "color": panel.color.to_tuple(),
                    "background_color": panel.background_color.to_tuple(),
                    "text_color": panel.text_color.to_tuple(),
                    "is_selected": panel.is_selected,
                    "is_highlighted": panel.is_highlighted,
                })

        return {
            "camera": camera.to_dict(),
            "boards": [
                {
                    "position": board.position,
                    "rotation": board.rotation,
                    "panels": panels,
                }
                for board in self.navigator._boards
            ],
            "tickers": {symbol: ticker.to_dict() for symbol, ticker in self.tickers.items()},
            "input_state": self.input_handler.get_status(),
            "timestamp": time.time(),
        }

    def get_status(self) -> dict:
        """Get the current VR scene status."""
        return {
            "is_running": self.is_running,
            "frame_rate": self.frame_rate,
            "ticker_count": len(self.tickers),
            "board_count": len(self.navigator._boards),
            "current_board": self.navigator.get_boards_status()["current_board_name"],
            "camera_position": self.navigator.get_camera_state().position,
            "camera_rotation": self.navigator.get_camera_state().rotation,
            "zoom_level": self.navigator.get_camera_state().zoom_level,
            "input_state": self.input_handler.get_status(),
        }

    def to_dict(self) -> dict:
        """Convert scene to dictionary."""
        return {
            "navigator": self.navigator.to_dict(),
            "input_handler": self.input_handler.get_status(),
            "tickers": {symbol: ticker.to_dict() for symbol, ticker in self.tickers.items()},
            "is_running": self.is_running,
            "frame_rate": self.frame_rate,
            "last_update_time": self.last_update_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> VRScene:
        """Create scene from dictionary."""
        scene = cls()
        scene.navigator = VRNavigator.from_dict(data["navigator"])
        scene.tickers = {
            symbol: Ticker.from_dict(ticker)
            for symbol, ticker in data["tickers"].items()
        }
        scene.is_running = data.get("is_running", False)
        scene.frame_rate = data.get("frame_rate", 60.0)
        scene.last_update_time = data.get("last_update_time", 0.0)
        return scene
