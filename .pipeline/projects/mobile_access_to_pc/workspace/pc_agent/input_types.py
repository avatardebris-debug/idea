"""
Input Types Module for PC Agent

This module defines input command types and data structures
for handling mouse and keyboard input from the iOS client.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class InputType(Enum):
    """Types of input commands."""
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    KEY_PRESS = "key_press"
    KEYBOARD_TEXT = "keyboard_text"
    HEARTBEAT = "heartbeat"
    SCROLL = "scroll"


class MouseButton(Enum):
    """Mouse button types."""
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


@dataclass
class MouseInput:
    """Mouse input data structure."""
    x: int
    y: int
    button: Optional[MouseButton] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'type': InputType.MOUSE_MOVE.value,
            'x': self.x,
            'y': self.y,
            'button': self.button.value if self.button else None
        }


@dataclass
class KeyboardInput:
    """Keyboard input data structure."""
    key: str
    modifiers: List[str] = None
    
    def __post_init__(self):
        """Initialize modifiers if None."""
        if self.modifiers is None:
            self.modifiers = []
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'type': InputType.KEY_PRESS.value,
            'key': self.key,
            'modifiers': self.modifiers
        }


@dataclass
class TouchInput:
    """Touch input data structure."""
    x: int
    y: int
    screen_width: int
    screen_height: int
    touch_type: str = "tap"
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'type': 'touch',
            'x': self.x,
            'y': self.y,
            'screen_width': self.screen_width,
            'screen_height': self.screen_height,
            'touch_type': self.touch_type
        }
    
    def screen_coordinates(self) -> tuple:
        """
        Convert touch coordinates to screen coordinates.
        
        Returns:
            Tuple of (x, y) in screen coordinates
        """
        # Map touch coordinates to screen coordinates
        x = int(self.x / self.screen_width * self.screen_width)
        y = int(self.y / self.screen_height * self.screen_height)
        return (x, y)


@dataclass
class ScrollInput:
    """Scroll input data structure."""
    x: int
    y: int
    delta_y: int
    delta_x: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'type': InputType.SCROLL.value,
            'x': self.x,
            'y': self.y,
            'delta_y': self.delta_y,
            'delta_x': self.delta_x
        }


class InputParser:
    """
    Parser for input commands from WebSocket messages.
    
    Converts incoming JSON messages into typed input objects.
    """
    
    @staticmethod
    def parse_mouse(data: dict) -> MouseInput:
        """
        Parse mouse input from dictionary.
        
        Args:
            data: Dictionary with mouse input data
            
        Returns:
            MouseInput object
        """
        return MouseInput(
            x=int(data.get('x', 0)),
            y=int(data.get('y', 0)),
            button=MouseButton(data.get('button', 'left')) if data.get('button') else None
        )
    
    @staticmethod
    def parse_keyboard(data: dict) -> KeyboardInput:
        """
        Parse keyboard input from dictionary.
        
        Args:
            data: Dictionary with keyboard input data
            
        Returns:
            KeyboardInput object
        """
        return KeyboardInput(
            key=str(data.get('key', '')),
            modifiers=data.get('modifiers', [])
        )
    
    @staticmethod
    def parse_touch(data: dict) -> TouchInput:
        """
        Parse touch input from dictionary.
        
        Args:
            data: Dictionary with touch input data
            
        Returns:
            TouchInput object
        """
        return TouchInput(
            x=int(data.get('x', 0)),
            y=int(data.get('y', 0)),
            screen_width=int(data.get('screen_width', 0)),
            screen_height=int(data.get('screen_height', 0)),
            touch_type=data.get('touch_type', 'tap')
        )
    
    @staticmethod
    def parse_scroll(data: dict) -> ScrollInput:
        """
        Parse scroll input from dictionary.
        
        Args:
            data: Dictionary with scroll input data
            
        Returns:
            ScrollInput object
        """
        return ScrollInput(
            x=int(data.get('x', 0)),
            y=int(data.get('y', 0)),
            delta_y=int(data.get('delta_y', 0)),
            delta_x=int(data.get('delta_x', 0))
        )
    
    @staticmethod
    def parse(data: dict):
        """
        Parse any input from dictionary.
        
        Args:
            data: Dictionary with input data
            
        Returns:
            Parsed input object or None
        """
        input_type = data.get('type')
        
        if input_type == 'mouse_move':
            return InputParser.parse_mouse(data)
        elif input_type == 'key_press':
            return InputParser.parse_keyboard(data)
        elif input_type == 'touch':
            return InputParser.parse_touch(data)
        elif input_type == 'scroll':
            return InputParser.parse_scroll(data)
        
        return None
