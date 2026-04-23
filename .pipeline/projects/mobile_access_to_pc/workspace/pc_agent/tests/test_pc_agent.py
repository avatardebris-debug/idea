#!/usr/bin/env python3
"""
Test suite for Mobile Access to PC - PC Agent

Tests for screen capture, WebSocket server, connection management,
and input handling.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock display-dependent modules BEFORE importing anything else
sys.modules['pyautogui'] = MagicMock()
sys.modules['pynput'] = MagicMock()
sys.modules['pynput.mouse'] = MagicMock()
sys.modules['pynput.keyboard'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['keyboard'] = MagicMock()
sys.modules['Xlib'] = MagicMock()
sys.modules['mouseinfo'] = MagicMock()

# Mock OpenCV
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()

from config import Config, ConfigLoader, ScreenConfig, ServerConfig, InputConfig
from screen_capture import ScreenCapture
from websocket_server import WebSocketServer
from connection_manager import ConnectionManager
from input_handler import InputHandler
from input_types import InputParser, MouseInput, KeyboardInput


class TestConfig(unittest.TestCase):
    """Test configuration loading and validation."""
    
    def test_server_config_defaults(self):
        """Test default server configuration."""
        config = ServerConfig()
        self.assertEqual(config.host, "0.0.0.0")
        self.assertEqual(config.port, 8765)
        self.assertEqual(config.max_connections, 5)
    
    def test_screen_config_defaults(self):
        """Test default screen configuration."""
        config = ScreenConfig()
        self.assertEqual(config.capture_fps, 15)
        self.assertEqual(config.quality, 75)
        self.assertEqual(config.scale_factor, 1.0)
    
    def test_config_validation(self):
        """Test Config class validation."""
        # Test invalid FPS in main Config
        with self.assertRaises(ValueError):
            Config(screen_config=ScreenConfig(capture_fps=0))
        
        with self.assertRaises(ValueError):
            Config(screen_config=ScreenConfig(capture_fps=100))
        
        # Test invalid quality
        with self.assertRaises(ValueError):
            Config(screen_config=ScreenConfig(quality=0))
        
        with self.assertRaises(ValueError):
            Config(screen_config=ScreenConfig(quality=101))
        
        # Test invalid scale factor
        with self.assertRaises(ValueError):
            Config(screen_config=ScreenConfig(scale_factor=0.3))
        
        with self.assertRaises(ValueError):
            Config(screen_config=ScreenConfig(scale_factor=1.5))
        
        # Test invalid mouse sensitivity
        with self.assertRaises(ValueError):
            Config(input_config=InputConfig(mouse_sensitivity=0.05))
        
        with self.assertRaises(ValueError):
            Config(input_config=InputConfig(mouse_sensitivity=10.0))


class TestScreenCapture(unittest.TestCase):
    """Test screen capture functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = ScreenConfig(
            capture_fps=10,
            quality=80,
            scale_factor=1.0
        )
        self.capture = ScreenCapture(self.config)
    
    def test_initialization(self):
        """Test screen capture initialization."""
        self.assertEqual(self.capture.width, 0)
        self.assertEqual(self.capture.height, 0)
        self.assertFalse(self.capture.is_running)
    
    def test_start_capture(self):
        """Test starting screen capture."""
        # Mock cv2.VideoCapture
        with patch('screen_capture.cv2') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.get.return_value = 1920
            mock_cv2.VideoCapture.return_value = mock_cap
            
            self.capture.start()
            self.assertTrue(self.capture.is_running)
    
    def test_stop_capture(self):
        """Test stopping screen capture."""
        with patch('screen_capture.cv2') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.get.return_value = 1920
            mock_cv2.VideoCapture.return_value = mock_cap
            
            self.capture.start()
            self.capture.stop()
            self.assertFalse(self.capture.is_running)
    
    def test_get_frame(self):
        """Test getting a frame."""
        with patch('screen_capture.cv2') as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = True
            mock_cap.get.return_value = 1920
            mock_cv2.VideoCapture.return_value = mock_cap
            
            mock_frame = MagicMock()
            mock_frame.shape = (1080, 1920, 3)
            mock_cap.read.return_value = (True, mock_frame)
            
            self.capture.start()
            frame = self.capture.get_frame()
            self.assertIsNotNone(frame)
            self.capture.stop()


class TestConnectionManager(unittest.TestCase):
    """Test connection manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server_config = ServerConfig()
        self.manager = ConnectionManager(self.server_config)
    
    def test_initialization(self):
        """Test connection manager initialization."""
        self.assertEqual(self.manager.get_client_count(), 0)
        self.assertFalse(self.manager._running)
    
    def test_add_client(self):
        """Test adding a client."""
        mock_ws = MagicMock()
        self.manager.add_client("test_client", mock_ws)
        
        self.assertEqual(self.manager.get_client_count(), 1)
        self.assertIn("test_client", self.manager._clients)
    
    def test_remove_client(self):
        """Test removing a client."""
        mock_ws = MagicMock()
        self.manager.add_client("test_client", mock_ws)
        self.manager.remove_client("test_client")
        
        self.assertEqual(self.manager.get_client_count(), 0)
        self.assertNotIn("test_client", self.manager._clients)
    
    def test_close_client(self):
        """Test closing a client connection."""
        mock_ws = MagicMock()
        self.manager.add_client("test_client", mock_ws)
        self.manager.close_client("test_client")
        
        mock_ws.close.assert_called_once()
    
    def test_get_active_clients(self):
        """Test getting active clients."""
        mock_ws = MagicMock()
        self.manager.add_client("test_client", mock_ws)
        
        active = self.manager.get_active_clients()
        self.assertIn("test_client", active)
    
    def test_mark_activity(self):
        """Test marking client activity."""
        self.manager.add_client("test_client", MagicMock())
        self.manager.mark_activity("test_client")
        
        self.assertIn("test_client", self.manager._last_activity)


class TestInputHandler(unittest.TestCase):
    """Test input handler functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = InputConfig()
        self.handler = InputHandler(self.config)
    
    def test_initialization(self):
        """Test input handler initialization."""
        self.assertEqual(self.handler._mouse_sensitivity, 1.0)
        self.assertTrue(self.handler._log_enabled)
    
    def test_mouse_move(self):
        """Test mouse movement."""
        with patch('input_handler.pyautogui') as mock_pyautogui:
            self.handler.mouse_move(100, 200)
            mock_pyautogui.moveTo.assert_called_once()
    
    def test_mouse_click(self):
        """Test mouse click."""
        with patch('input_handler.pyautogui') as mock_pyautogui:
            self.handler.mouse_click('left')
            mock_pyautogui.click.assert_called_once()
    
    def test_key_press(self):
        """Test key press."""
        with patch('input_handler.pyautogui') as mock_pyautogui:
            self.handler.key_press('a')
            mock_pyautogui.press.assert_called_once_with('a')
    
    def test_type_text(self):
        """Test typing text."""
        with patch('input_handler.pyautogui') as mock_pyautogui:
            self.handler.type_text("Hello")
            mock_pyautogui.write.assert_called_once()
    
    def test_set_sensitivity(self):
        """Test setting mouse sensitivity."""
        self.handler.set_sensitivity(2.0)
        self.assertEqual(self.handler._mouse_sensitivity, 2.0)
    
    def test_set_invalid_sensitivity(self):
        """Test setting invalid mouse sensitivity."""
        with self.assertLogs('input_handler', level='WARNING') as cm:
            self.handler.set_sensitivity(10.0)
            self.assertIn("Invalid sensitivity", cm.output[0])


class TestInputParser(unittest.TestCase):
    """Test input parsing functionality."""
    
    def test_parse_mouse(self):
        """Test parsing mouse input."""
        data = {'type': 'mouse_move', 'x': 100, 'y': 200, 'button': 'left'}
        result = InputParser.parse_mouse(data)
        
        self.assertEqual(result.x, 100)
        self.assertEqual(result.y, 200)
        self.assertIsNotNone(result.button)
    
    def test_parse_keyboard(self):
        """Test parsing keyboard input."""
        data = {'type': 'key_press', 'key': 'a', 'modifiers': ['ctrl']}
        result = InputParser.parse_keyboard(data)
        
        self.assertEqual(result.key, 'a')
        self.assertEqual(result.modifiers, ['ctrl'])
    
    def test_parse_touch(self):
        """Test parsing touch input."""
        data = {
            'type': 'touch',
            'x': 100,
            'y': 200,
            'screen_width': 1920,
            'screen_height': 1080
        }
        result = InputParser.parse_touch(data)
        
        self.assertEqual(result.x, 100)
        self.assertEqual(result.y, 200)
        self.assertEqual(result.screen_width, 1920)
    
    def test_parse_scroll(self):
        """Test parsing scroll input."""
        data = {'type': 'scroll', 'x': 100, 'y': 200, 'delta_y': 120}
        result = InputParser.parse_scroll(data)
        
        self.assertEqual(result.x, 100)
        self.assertEqual(result.y, 200)
        self.assertEqual(result.delta_y, 120)


class TestInputTypes(unittest.TestCase):
    """Test input type data classes."""
    
    def test_mouse_input_to_dict(self):
        """Test mouse input to dictionary conversion."""
        input_data = MouseInput(x=100, y=200, button=None)
        result = input_data.to_dict()
        
        self.assertEqual(result['type'], 'mouse_move')
        self.assertEqual(result['x'], 100)
        self.assertEqual(result['y'], 200)
    
    def test_keyboard_input_to_dict(self):
        """Test keyboard input to dictionary conversion."""
        input_data = KeyboardInput(key='a', modifiers=['ctrl'])
        result = input_data.to_dict()
        
        self.assertEqual(result['type'], 'key_press')
        self.assertEqual(result['key'], 'a')
        self.assertEqual(result['modifiers'], ['ctrl'])


class TestConfigLoader(unittest.TestCase):
    """Test configuration loading from file."""
    
    def test_load_config_from_file(self):
        """Test loading configuration from file."""
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json.dumps({
                'server': {'port': 9999},
                'screen': {'capture_fps': 30}
            }))
            temp_path = f.name
        
        try:
            loader = ConfigLoader(temp_path)
            config = loader.load()
            self.assertIsInstance(config, Config)
            self.assertEqual(config.server_config.port, 9999)
            self.assertEqual(config.screen_config.capture_fps, 30)
        finally:
            os.unlink(temp_path)
    
    def test_load_config_default(self):
        """Test loading configuration with defaults."""
        # Test that ConfigLoader can be instantiated
        loader = ConfigLoader()
        self.assertIsNotNone(loader)


class TestWebSocketServer(unittest.TestCase):
    """Test WebSocket server functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.server = WebSocketServer(self.config)
    
    def test_initialization(self):
        """Test WebSocket server initialization."""
        self.assertFalse(self.server._running)
        self.assertIsNotNone(self.server.connection_manager)
        self.assertIsNotNone(self.server.input_handler)
    
    def test_get_status(self):
        """Test getting server status."""
        status = self.server.get_status()
        
        self.assertIn('running', status)
        self.assertIn('host', status)
        self.assertIn('port', status)
        self.assertIn('connected_clients', status)


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestScreenCapture))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestInputHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestInputParser))
    suite.addTests(loader.loadTestsFromTestCase(TestInputTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigLoader))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSocketServer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
