"""VR navigation system — camera movement, panel zoom/pan, and multi-board management."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.ticker_display import TickerBoard


@dataclass
class CameraState:
    """Represents the VR camera state."""
    position: Tuple[float, float, float] = (0.0, 1.6, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    zoom_level: float = 1.0
    is_focused: bool = False
    focus_target: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "position": list(self.position),
            "rotation": list(self.rotation),
            "zoom_level": self.zoom_level,
            "is_focused": self.is_focused,
            "focus_target": self.focus_target,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CameraState:
        """Create from dictionary."""
        return cls(
            position=tuple(data["position"]),
            rotation=tuple(data["rotation"]),
            zoom_level=data.get("zoom_level", 1.0),
            is_focused=data.get("is_focused", False),
            focus_target=data.get("focus_target"),
        )


class VRNavigator:
    """Handles VR navigation — camera movement, board switching, and panel zoom."""

    def __init__(self):
        """Initialize navigator."""
        self._boards: List[TickerBoard] = []
        self._current_board_index: int = 0
        self._camera = CameraState()
        self._is_zoomed: bool = False
        self._zoom_target: Optional[str] = None
        self._max_boards: int = 10
        self._board_names: List[str] = []

    def add_board(self, board: TickerBoard, name: str = "") -> bool:
        """Add a ticker board to the navigator."""
        if len(self._boards) >= self._max_boards:
            return False

        if not name:
            name = f"Board {len(self._board_names) + 1}"
        if name in self._board_names:
            name = f"{name} ({len(self._board_names)})"

        self._boards.append(board)
        self._board_names.append(name)
        return True

    def remove_board(self, name: str) -> bool:
        """Remove a ticker board by name."""
        if name in self._board_names:
            index = self._board_names.index(name)
            self._boards.pop(index)
            self._board_names.pop(index)
            if self._current_board_index >= len(self._boards):
                self._current_board_index = max(0, len(self._boards) - 1)
            return True
        return False

    def get_board(self, name: str) -> Optional[TickerBoard]:
        """Get a board by name."""
        if name in self._board_names:
            index = self._board_names.index(name)
            return self._boards[index]
        return None

    def get_current_board(self) -> Optional[TickerBoard]:
        """Get the currently active board."""
        if 0 <= self._current_board_index < len(self._boards):
            return self._boards[self._current_board_index]
        return None

    def switch_board(self, name: str) -> bool:
        """Switch to a different board."""
        if name in self._board_names:
            self._current_board_index = self._board_names.index(name)
            self._camera.focus_target = None
            self._camera.is_focused = False
            self._is_zoomed = False
            self._zoom_target = None
            return True
        return False

    def switch_board_by_index(self, index: int) -> bool:
        """Switch to a board by index."""
        if 0 <= index < len(self._boards):
            self._current_board_index = index
            self._camera.focus_target = None
            self._camera.is_focused = False
            self._is_zoomed = False
            self._zoom_target = None
            return True
        return False

    def zoom_to_panel(self, ticker_symbol: str) -> bool:
        """Zoom camera to a specific panel."""
        board = self.get_current_board()
        if not board:
            return False

        panel = board.get_panel(ticker_symbol)
        if not panel:
            return False

        # Calculate zoom position (panel position + offset)
        panel_pos = panel.position
        zoom_distance = 0.5  # Distance to zoom in

        self._camera.position = (
            panel_pos[0],
            panel_pos[1] + 0.2,
            panel_pos[2] - zoom_distance,
        )
        self._camera.rotation = (0.0, 0.0, 0.0)
        self._camera.zoom_level = 2.0
        self._camera.is_focused = True
        self._camera.focus_target = ticker_symbol
        self._is_zoomed = True
        self._zoom_target = ticker_symbol

        return True

    def zoom_out(self) -> bool:
        """Zoom out from current panel."""
        if not self._is_zoomed:
            return False

        self._camera.zoom_level = 1.0
        self._camera.is_focused = False
        self._camera.focus_target = None
        self._is_zoomed = False
        self._zoom_target = None

        return True

    def navigate_left(self, distance: float = 1.0) -> None:
        """Navigate camera left."""
        x, y, z = self._camera.position
        self._camera.position = (x - distance, y, z)

    def navigate_right(self, distance: float = 1.0) -> None:
        """Navigate camera right."""
        x, y, z = self._camera.position
        self._camera.position = (x + distance, y, z)

    def navigate_up(self, distance: float = 1.0) -> None:
        """Navigate camera up."""
        x, y, z = self._camera.position
        self._camera.position = (x, y + distance, z)

    def navigate_down(self, distance: float = 1.0) -> None:
        """Navigate camera down."""
        x, y, z = self._camera.position
        self._camera.position = (x, y - distance, z)

    def rotate_camera(self, yaw: float, pitch: float) -> None:
        """Rotate camera by yaw and pitch angles."""
        y, p, r = self._camera.rotation
        self._camera.rotation = (
            max(-89, min(89, p + pitch)),  # Clamp pitch
            y + yaw,
            r,
        )

    def get_camera_state(self) -> CameraState:
        """Get current camera state."""
        return self._camera

    def get_boards_status(self) -> dict:
        """Get status of all boards."""
        return {
            "board_count": len(self._boards),
            "board_names": self._board_names,
            "current_board_index": self._current_board_index,
            "current_board_name": self._board_names[self._current_board_index] if self._board_names else None,
        }

    def to_dict(self) -> dict:
        """Convert navigator to dictionary."""
        return {
            "boards": [board.to_dict() for board in self._boards],
            "board_names": self._board_names,
            "current_board_index": self._current_board_index,
            "camera": self._camera.to_dict(),
            "is_zoomed": self._is_zoomed,
            "zoom_target": self._zoom_target,
        }

    @classmethod
    def from_dict(cls, data: dict) -> VRNavigator:
        """Create navigator from dictionary."""
        navigator = cls()
        navigator._boards = [TickerBoard.from_dict(b) for b in data["boards"]]
        navigator._board_names = data["board_names"]
        navigator._current_board_index = data["current_board_index"]
        navigator._camera = CameraState.from_dict(data["camera"])
        navigator._is_zoomed = data.get("is_zoomed", False)
        navigator._zoom_target = data.get("zoom_target")
        return navigator

    def get_status(self) -> dict:
        """Get navigator status."""
        return {
            **self.get_boards_status(),
            "camera_position": self._camera.position,
            "camera_rotation": self._camera.rotation,
            "zoom_level": self._camera.zoom_level,
            "is_zoomed": self._is_zoomed,
            "zoom_target": self._zoom_target,
        }
