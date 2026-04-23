"""
Input Handler Module for PC Agent

This module handles mouse and keyboard input processing,
converting touch and keyboard events from the iOS client
into PC input commands.
"""

import logging
import time

import pyautogui

from config import InputConfig

logger = logging.getLogger(__name__)


class InputHandler:
    """
    Handles input from the iOS client and executes corresponding
    PC input commands.
    
    Features:
    - Mouse movement and click handling
    - Keyboard input and text typing
    - Touch-to-mouse coordinate mapping
    - Input event logging
    - Error handling for failed operations
    """
    
    def __init__(self, config: InputConfig):
        """
        Initialize input handler.
        
        Args:
            config: InputConfig with input settings
        """
        self.config = config
        self._last_mouse_move = 0
        self._mouse_sensitivity = config.mouse_sensitivity
        self._keyboard_delay = config.keyboard_delay
        self._log_enabled = config.log_input_events
        
        # Setup pyautogui
        pyautogui.FAILSAFE = True
        logger.info("InputHandler initialized")
    
    def mouse_move(self, x: int, y: int):
        """
        Move mouse cursor to specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        try:
            # Apply sensitivity
            x = int(x * self._mouse_sensitivity)
            y = int(y * self._mouse_sensitivity)
            
            # Move mouse
            pyautogui.moveTo(x, y, duration=0.1)
            
            if self._log_enabled:
                logger.debug(f"Mouse moved to ({x}, {y})")
            
            # Update last move time
            self._last_mouse_move = time.time()
            
        except Exception as e:
            logger.error(f"Mouse move failed: {e}")
    
    def mouse_click(self, button: str = 'left'):
        """
        Click mouse button.
        
        Args:
            button: Mouse button to click ('left', 'right', 'middle')
        """
        try:
            # Map button string to pyautogui constant
            button_map = {
                'left': 'left',
                'right': 'right',
                'middle': 'middle'
            }
            
            if button not in button_map:
                logger.warning(f"Unknown button: {button}, defaulting to left")
                button = 'left'
            
            pyautogui.click(button=button)
            
            if self._log_enabled:
                logger.debug(f"Mouse {button} click")
            
        except Exception as e:
            logger.error(f"Mouse click failed: {e}")
    
    def mouse_drag(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """
        Drag mouse from one point to another.
        
        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
        """
        try:
            # Apply sensitivity
            start_x = int(start_x * self._mouse_sensitivity)
            start_y = int(start_y * self._mouse_sensitivity)
            end_x = int(end_x * self._mouse_sensitivity)
            end_y = int(end_y * self._mouse_sensitivity)
            
            # Drag mouse
            pyautogui.dragTo(end_x, end_y, duration=0.5, button='left')
            
            if self._log_enabled:
                logger.debug(f"Mouse dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            
        except Exception as e:
            logger.error(f"Mouse drag failed: {e}")
    
    def mouse_scroll(self, x: int, y: int, delta_y: int):
        """
        Scroll mouse wheel.
        
        Args:
            x: X coordinate to scroll from
            y: Y coordinate to scroll from
            delta_y: Scroll amount (positive = up, negative = down)
        """
        try:
            # Move to position first
            pyautogui.moveTo(x, y, duration=0.1)
            
            # Scroll
            pyautogui.scroll(delta_y)
            
            if self._log_enabled:
                logger.debug(f"Mouse scrolled {delta_y} units at ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Mouse scroll failed: {e}")
    
    def key_press(self, key: str):
        """
        Press and release a key.
        
        Args:
            key: Key to press (e.g., 'a', 'enter', 'ctrl', 'shift')
        """
        try:
            pyautogui.press(key)
            
            if self._log_enabled:
                logger.debug(f"Key pressed: {key}")
            
        except Exception as e:
            logger.error(f"Key press failed: {e}")
    
    def key_down(self, key: str):
        """
        Press and hold a key.
        
        Args:
            key: Key to press
        """
        try:
            pyautogui.keyDown(key)
            
            if self._log_enabled:
                logger.debug(f"Key held down: {key}")
            
        except Exception as e:
            logger.error(f"Key down failed: {e}")
    
    def key_up(self, key: str):
        """
        Release a held key.
        
        Args:
            key: Key to release
        """
        try:
            pyautogui.keyUp(key)
            
            if self._log_enabled:
                logger.debug(f"Key released: {key}")
            
        except Exception as e:
            logger.error(f"Key up failed: {e}")
    
    def type_text(self, text: str):
        """
        Type text character by character.
        
        Args:
            text: Text to type
        """
        try:
            pyautogui.write(text, interval=self._keyboard_delay)
            
            if self._log_enabled:
                logger.debug(f"Typed text: {text}")
            
        except Exception as e:
            logger.error(f"Text typing failed: {e}")
    
    def hotkey(self, *keys: str):
        """
        Press a keyboard hotkey combination.
        
        Args:
            keys: Keys to press simultaneously (e.g., 'ctrl', 'c')
        """
        try:
            pyautogui.hotkey(*keys)
            
            if self._log_enabled:
                logger.debug(f"Hotkey pressed: {', '.join(keys)}")
            
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
    
    def set_sensitivity(self, sensitivity: float):
        """
        Set mouse sensitivity.
        
        Args:
            sensitivity: Sensitivity value (0.1 to 5.0)
        """
        try:
            if sensitivity < 0.1 or sensitivity > 5.0:
                logger.warning(f"Invalid sensitivity: {sensitivity}, clamping to range 0.1-5.0")
                sensitivity = max(0.1, min(5.0, sensitivity))
            
            self._mouse_sensitivity = sensitivity
            logger.info(f"Mouse sensitivity set to {sensitivity}")
            
        except Exception as e:
            logger.error(f"Failed to set sensitivity: {e}")
    
    def handle_input(self, input_type: str, **kwargs):
        """
        Handle incoming input command.
        
        Args:
            input_type: Type of input command
            **kwargs: Command parameters
        """
        try:
            if input_type == 'mouse_move':
                self.mouse_move(kwargs.get('x', 0), kwargs.get('y', 0))
            
            elif input_type == 'mouse_click':
                self.mouse_click(kwargs.get('button', 'left'))
            
            elif input_type == 'mouse_drag':
                self.mouse_drag(
                    kwargs.get('start_x', 0),
                    kwargs.get('start_y', 0),
                    kwargs.get('end_x', 0),
                    kwargs.get('end_y', 0)
                )
            
            elif input_type == 'mouse_scroll':
                self.mouse_scroll(
                    kwargs.get('x', 0),
                    kwargs.get('y', 0),
                    kwargs.get('delta_y', 0)
                )
            
            elif input_type == 'key_press':
                self.key_press(kwargs.get('key', ''))
            
            elif input_type == 'key_down':
                self.key_down(kwargs.get('key', ''))
            
            elif input_type == 'key_up':
                self.key_up(kwargs.get('key', ''))
            
            elif input_type == 'type_text':
                self.type_text(kwargs.get('text', ''))
            
            elif input_type == 'hotkey':
                self.hotkey(*kwargs.get('keys', []))
            
            else:
                logger.warning(f"Unknown input type: {input_type}")
            
        except Exception as e:
            logger.error(f"Failed to handle input: {e}")
    
    def get_last_mouse_move_time(self) -> float:
        """
        Get the timestamp of the last mouse move.
        
        Returns:
            Timestamp of last mouse move
        """
        return self._last_mouse_move
