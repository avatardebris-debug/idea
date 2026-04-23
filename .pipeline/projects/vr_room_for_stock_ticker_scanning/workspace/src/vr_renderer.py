"""VR rendering engine — handles 3D rendering of ticker panels and VR environment."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.vr_scene import VRScene


@dataclass
class RenderObject:
    """Represents a 3D object to be rendered."""
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    size: Tuple[float, float, float]
    color: Tuple[float, float, float]
    background_color: Tuple[float, float, float]
    text_color: Tuple[float, float, float]
    is_selected: bool = False
    is_highlighted: bool = False
    ticker_symbol: str = ""
    ticker_price: float = 0.0
    ticker_change: float = 0.0
    ticker_change_percent: float = 0.0


class VRRenderer:
    """Handles VR rendering of ticker panels and environment."""

    def __init__(self, scene: VRScene):
        """Initialize renderer with VR scene."""
        self.scene = scene
        self._render_objects: List[RenderObject] = []
        self._camera_position: Tuple[float, float, float] = (0.0, 1.6, 0.0)
        self._camera_rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
        self._zoom_level: float = 1.0
        self._is_rendering: bool = False
        self._frame_count: int = 0
        self._last_frame_time: float = 0.0
        self._fps: float = 0.0

    def start_rendering(self) -> None:
        """Start the rendering loop."""
        self._is_rendering = True
        self._last_frame_time = time.time()

    def stop_rendering(self) -> None:
        """Stop the rendering loop."""
        self._is_rendering = False

    def render_frame(self) -> List[RenderObject]:
        """Render a single frame and return render objects."""
        if not self._is_rendering:
            return []

        # Update frame timing
        current_time = time.time()
        frame_time = current_time - self._last_frame_time
        self._last_frame_time = current_time
        self._frame_count += 1

        # Calculate FPS
        if self._frame_count % 60 == 0:
            self._fps = 60.0 / frame_time if frame_time > 0 else 0.0

        # Get current frame data
        frame_data = self.scene.get_frame()
        if not frame_data:
            return []

        # Update camera state
        camera = frame_data.get("camera", {})
        self._camera_position = tuple(camera.get("position", self._camera_position))
        self._camera_rotation = tuple(camera.get("rotation", self._camera_rotation))
        self._zoom_level = camera.get("zoom_level", self._zoom_level)

        # Clear previous render objects
        self._render_objects.clear()

        # Process boards
        for board_data in frame_data.get("boards", []):
            board_position = tuple(board_data.get("position", (0.0, 0.0, 0.0)))
            board_rotation = tuple(board_data.get("rotation", (0.0, 0.0, 0.0)))

            # Process panels
            for panel_data in board_data.get("panels", []):
                ticker_symbol = panel_data.get("ticker", {}).get("symbol", "")
                ticker_price = panel_data.get("ticker", {}).get("price", 0.0)
                ticker_change = panel_data.get("ticker", {}).get("change", 0.0)
                ticker_change_percent = panel_data.get("ticker", {}).get("change_percent", 0.0)

                render_obj = RenderObject(
                    position=tuple(panel_data.get("position", (0.0, 0.0, 0.0))),
                    rotation=tuple(panel_data.get("rotation", (0.0, 0.0, 0.0))),
                    size=tuple(panel_data.get("size", (1.0, 0.6, 0.05))),
                    color=tuple(panel_data.get("color", (0.0, 0.0, 0.0))),
                    background_color=tuple(panel_data.get("background_color", (0.0, 0.0, 0.0))),
                    text_color=tuple(panel_data.get("text_color", (0.0, 0.0, 0.0))),
                    is_selected=panel_data.get("is_selected", False),
                    is_highlighted=panel_data.get("is_highlighted", False),
                    ticker_symbol=ticker_symbol,
                    ticker_price=ticker_price,
                    ticker_change=ticker_change,
                    ticker_change_percent=ticker_change_percent,
                )
                self._render_objects.append(render_obj)

        return self._render_objects

    def get_render_objects(self) -> List[RenderObject]:
        """Get current render objects."""
        return list(self._render_objects)

    def get_camera_state(self) -> dict:
        """Get current camera state."""
        return {
            "position": self._camera_position,
            "rotation": self._camera_rotation,
            "zoom_level": self._zoom_level,
        }

    def get_fps(self) -> float:
        """Get current FPS."""
        return self._fps

    def get_status(self) -> dict:
        """Get renderer status."""
        return {
            "is_rendering": self._is_rendering,
            "frame_count": self._frame_count,
            "fps": self._fps,
            "render_objects_count": len(self._render_objects),
            "camera_position": self._camera_position,
            "camera_rotation": self._camera_rotation,
            "zoom_level": self._zoom_level,
        }

    def to_dict(self) -> dict:
        """Convert renderer to dictionary."""
        return {
            "camera_position": list(self._camera_position),
            "camera_rotation": list(self._camera_rotation),
            "zoom_level": self._zoom_level,
            "frame_count": self._frame_count,
            "fps": self._fps,
            "is_rendering": self._is_rendering,
        }

    @classmethod
    def from_dict(cls, data: dict, scene: VRScene) -> VRRenderer:
        """Create renderer from dictionary."""
        renderer = cls(scene)
        renderer._camera_position = tuple(data["camera_position"])
        renderer._camera_rotation = tuple(data["camera_rotation"])
        renderer._zoom_level = data["zoom_level"]
        renderer._frame_count = data["frame_count"]
        renderer._fps = data["fps"]
        renderer._is_rendering = data["is_rendering"]
        return renderer
