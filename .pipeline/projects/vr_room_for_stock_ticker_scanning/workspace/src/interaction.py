"""VR input handling — gaze and pointer interaction for ticker selection."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional, Tuple


class InputEventType(Enum):
    """Types of VR input events."""
    GAZE_START = "gaze_start"
    GAZE_END = "gaze_end"
    POINTER_CLICK = "pointer_click"
    POINTER_RELEASE = "pointer_release"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    NAVIGATE_LEFT = "navigate_left"
    NAVIGATE_RIGHT = "navigate_right"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"
    BOARD_SWITCH = "board_switch"


@dataclass
class InputEvent:
    """Represents a single VR input event."""
    event_type: InputEventType
    timestamp: float = field(default_factory=time.time)
    source: str = "unknown"  # "gaze", "controller", "keyboard", "voice"
    target: Optional[str] = None  # ticker symbol, board name, etc.
    value: float = 0.0  # magnitude (e.g., scroll amount)
    position: Optional[Tuple[float, float, float]] = None  # 3D position in VR space

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "target": self.target,
            "value": self.value,
            "position": list(self.position) if self.position else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> InputEvent:
        """Create event from dictionary."""
        return cls(
            event_type=InputEventType(data["event_type"]),
            timestamp=data["timestamp"],
            source=data["source"],
            target=data["target"],
            value=data["value"],
            position=tuple(data["position"]) if data.get("position") else None,
        )


class VRInputHandler:
    """Handles VR input events from various sources."""

    def __init__(self):
        """Initialize input handler."""
        self._callbacks: dict[InputEventType, List[Callable]] = {}
        self._gaze_target: Optional[str] = None
        self._gaze_start_time: float = 0.0
        self._gaze_duration_threshold: float = 1.0  # seconds to trigger action
        self._is_gazing: bool = False
        self._event_history: List[InputEvent] = []
        self._max_history: int = 100

    def register_callback(self, event_type: InputEventType, callback: Callable) -> None:
        """Register a callback for a specific event type."""
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

    def unregister_callback(self, event_type: InputEventType, callback: Callable) -> None:
        """Unregister a callback for a specific event type."""
        if event_type in self._callbacks:
            if callback in self._callbacks[event_type]:
                self._callbacks[event_type].remove(callback)

    def emit_event(self, event: InputEvent) -> None:
        """Emit an input event to all registered callbacks."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        if event.event_type in self._callbacks:
            for callback in self._callbacks[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    pass  # Ignore callback errors

    def start_gaze(self, target: str, position: Tuple[float, float, float]) -> None:
        """Start gazing at a target."""
        self._gaze_target = target
        self._gaze_start_time = time.time()
        self._is_gazing = True
        self.emit_event(InputEvent(
            event_type=InputEventType.GAZE_START,
            source="gaze",
            target=target,
            position=position,
        ))

    def end_gaze(self) -> None:
        """End current gaze."""
        if self._is_gazing:
            gaze_duration = time.time() - self._gaze_start_time
            if gaze_duration >= self._gaze_duration_threshold:
                # Gaze was long enough to trigger action
                self.emit_event(InputEvent(
                    event_type=InputEventType.GAZE_END,
                    source="gaze",
                    target=self._gaze_target,
                    value=gaze_duration,
                ))
            self._gaze_target = None
            self._is_gazing = False

    def is_gazing(self) -> bool:
        """Check if currently gazing at something."""
        return self._is_gazing

    def get_gaze_target(self) -> Optional[str]:
        """Get current gaze target."""
        return self._gaze_target

    def get_gaze_duration(self) -> float:
        """Get current gaze duration."""
        if self._is_gazing:
            return time.time() - self._gaze_start_time
        return 0.0

    def handle_pointer_click(self, target: str, position: Tuple[float, float, float]) -> None:
        """Handle pointer click event."""
        self.emit_event(InputEvent(
            event_type=InputEventType.POINTER_CLICK,
            source="controller",
            target=target,
            position=position,
        ))

    def handle_scroll(self, direction: str, magnitude: float = 1.0) -> None:
        """Handle scroll event."""
        event_type = InputEventType.SCROLL_UP if direction == "up" else InputEventType.SCROLL_DOWN
        self.emit_event(InputEvent(
            event_type=event_type,
            source="controller",
            value=magnitude,
        ))

    def handle_navigation(self, direction: str) -> None:
        """Handle navigation event."""
        event_type = InputEventType.NAVIGATE_LEFT if direction == "left" else InputEventType.NAVIGATE_RIGHT
        self.emit_event(InputEvent(
            event_type=event_type,
            source="controller",
        ))

    def handle_zoom(self, direction: str) -> None:
        """Handle zoom event."""
        event_type = InputEventType.ZOOM_IN if direction == "in" else InputEventType.ZOOM_OUT
        self.emit_event(InputEvent(
            event_type=event_type,
            source="controller",
        ))

    def handle_board_switch(self, board_name: str) -> None:
        """Handle board switch event."""
        self.emit_event(InputEvent(
            event_type=InputEventType.BOARD_SWITCH,
            source="controller",
            target=board_name,
        ))

    def get_event_history(self) -> List[InputEvent]:
        """Get recent input event history."""
        return list(self._event_history)

    def clear_history(self) -> None:
        """Clear input event history."""
        self._event_history.clear()

    def get_status(self) -> dict:
        """Get input handler status."""
        return {
            "is_gazing": self._is_gazing,
            "gaze_target": self._gaze_target,
            "gaze_duration": self.get_gaze_duration(),
            "registered_events": list(self._callbacks.keys()),
            "event_history_length": len(self._event_history),
        }
