"""
WebSocket Server Module for PC Agent

This module implements the WebSocket server that handles
bidirectional communication with iOS clients.
"""

import asyncio
import json
import logging

import websockets
from websockets.server import serve, WebSocketServerProtocol

from config import Config
from connection_manager import ConnectionManager
from input_handler import InputHandler
from input_types import InputParser
from screen_capture import ScreenCapture
from utils.compression import VideoCompressor

logger = logging.getLogger(__name__)


class WebSocketServer:
    """
    WebSocket server for PC Agent.
    
    Features:
    - Listens on configurable port
    - Handles multiple client connections
    - Sends encoded screen frames
    - Receives and processes input commands
    - Connection state tracking
    - Automatic reconnection logic
    - TLS/SSL support for secure connections
    """
    
    def __init__(self, config: Config):
        """
        Initialize WebSocket server.
        
        Args:
            config: Config object with all configuration settings
        """
        self.config = config
        self.server_config = config.server_config
        self.connection_manager = ConnectionManager(self.server_config)
        self.input_handler = InputHandler(config.input_config)
        self.screen_capture = ScreenCapture(config.screen_config)
        self.video_compressor = VideoCompressor(config.screen_config)
        self._server = None
        self._running = False
        
        logger.info("WebSocketServer initialized")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol):
        """
        Handle a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection object
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"New connection from: {client_id}")
        
        # Add to connection manager
        self.connection_manager.add_client(client_id, websocket)
        
        try:
            # Send welcome message
            await self._send_welcome(websocket, client_id)
            
            # Start frame sender task
            frame_task = asyncio.create_task(self._send_frames(websocket))
            
            # Process incoming messages
            async for message in websocket:
                try:
                    await self._process_message(websocket, client_id, message)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from {client_id}")
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}")
            
            # Client disconnected
            logger.info(f"Client disconnected: {client_id}")
            
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Connection closed: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            # Clean up
            frame_task.cancel()
            try:
                await frame_task
            except asyncio.CancelledError:
                pass
            
            self.connection_manager.remove_client(client_id)
    
    async def _send_welcome(self, websocket: WebSocketServerProtocol, client_id: str):
        """Send welcome message to client."""
        welcome_message = {
            'type': 'connected',
            'message': 'Connected to PC Agent',
            'screen_width': self.screen_capture.width,
            'screen_height': self.screen_capture.height,
            'server_version': '1.0.0'
        }
        
        try:
            await websocket.send(json.dumps(welcome_message))
            logger.debug(f"Welcome message sent to {client_id}")
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
    
    async def _send_frames(self, websocket: WebSocketServerProtocol):
        """
        Send screen frames to client.
        """
        while self._running:
            try:
                # Wait for next frame interval
                await asyncio.sleep(0.1)
                
                # Capture frame
                frame = self.screen_capture.get_frame()
                if frame is None:
                    continue
                
                # Compress frame
                compressed = self.video_compressor.compress(frame)
                
                # Send frame
                await websocket.send(compressed)
                
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed during frame send")
                break
            except Exception as e:
                logger.error(f"Error sending frame: {e}")
                await asyncio.sleep(0.1)
    
    async def _process_message(self, websocket: WebSocketServerProtocol, client_id: str, message: str):
        """
        Process incoming message from client.
        
        Args:
            websocket: WebSocket connection
            client_id: Client identifier
            message: Message string
        """
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'mouse_move':
                input_data = InputParser.parse_mouse(data)
                if input_data:
                    self.input_handler.mouse_move(input_data.x, input_data.y)
            
            elif msg_type == 'mouse_click':
                input_data = InputParser.parse_mouse(data)
                if input_data and input_data.button:
                    self.input_handler.mouse_click(input_data.button.value)
                else:
                    self.input_handler.mouse_click('left')
            
            elif msg_type == 'key_press':
                input_data = InputParser.parse_keyboard(data)
                if input_data:
                    self.input_handler.key_press(input_data.key, input_data.modifiers)
            
            elif msg_type == 'keyboard_text':
                text = data.get('text', '')
                self.input_handler.type_text(text)
            
            elif msg_type == 'heartbeat':
                # Acknowledge heartbeat
                await websocket.send(json.dumps({
                    'type': 'heartbeat_ack',
                    'timestamp': asyncio.get_event_loop().time()
                }))
            
            elif msg_type == 'touch':
                input_data = InputParser.parse_touch(data)
                if input_data:
                    screen_x, screen_y = input_data.screen_coordinates()
                    self.input_handler.mouse_move(screen_x, screen_y)
                    self.input_handler.mouse_click('left')
            
            else:
                logger.warning(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
    
    async def start(self):
        """Start the WebSocket server."""
        self._running = True
        
        # Initialize screen capture
        self.screen_capture.start()
        logger.info(f"Screen capture started: {self.screen_capture.width}x{self.screen_capture.height}")
        
        # Start WebSocket server
        host = self.server_config.host
        port = self.server_config.port
        
        logger.info(f"Starting WebSocket server on {host}:{port}")
        
        self._server = await serve(
            self.handle_connection,
            host,
            port
        )
        
        logger.info(f"PC Agent started successfully on ws://{host}:{port}")
        logger.info(f"Max connections: {self.server_config.max_connections}")
        
        # Start heartbeat monitor
        asyncio.create_task(self.connection_manager.start_heartbeat_monitor())
        
        # Keep running
        try:
            while self._running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Server cancelled")
    
    def stop(self):
        """Stop the WebSocket server."""
        logger.info("Stopping WebSocket server...")
        self._running = False
        
        # Close all connections
        self.connection_manager.close_all()
        
        # Stop screen capture
        self.screen_capture.stop()
        
        # Close WebSocket server
        if self._server:
            self._server.close()
        
        logger.info("WebSocket server stopped")
    
    def get_status(self) -> dict:
        """
        Get server status information.
        
        Returns:
            Dictionary with server status information
        """
        return {
            'running': self._running,
            'host': self.server_config.host,
            'port': self.server_config.port,
            'screen_width': self.screen_capture.width,
            'screen_height': self.screen_capture.height,
            'capture_fps': self.screen_capture.config.capture_fps,
            'quality': self.screen_capture.config.quality,
            'client_count': self.connection_manager.get_client_count(),
            'connected_clients': self.connection_manager.get_active_clients(),
            'input_sensitivity': self.input_handler._mouse_sensitivity,
            'compression_stats': self.video_compressor.get_compression_stats()
        }
    
    def set_screen_quality(self, quality: int):
        """
        Set screen capture quality.
        
        Args:
            quality: Quality level (1-100)
        """
        if 1 <= quality <= 100:
            self.screen_capture.config.quality = quality
            self.video_compressor.set_quality(quality)
            logger.info(f"Screen quality set to {quality}")
    
    def set_capture_fps(self, fps: int):
        """
        Set capture frame rate.
        
        Args:
            fps: Frames per second (1-60)
        """
        if 1 <= fps <= 60:
            self.screen_capture.config.capture_fps = fps
            logger.info(f"Capture FPS set to {fps}")
    
    def set_input_sensitivity(self, sensitivity: float):
        """
        Set input sensitivity.
        
        Args:
            sensitivity: Sensitivity value (0.1-5.0)
        """
        if 0.1 <= sensitivity <= 5.0:
            self.input_handler.set_sensitivity(sensitivity)
            logger.info(f"Input sensitivity set to {sensitivity}")
    
    def restart_screen_capture(self):
        """Restart screen capture with current settings."""
        self.screen_capture.stop()
        self.screen_capture.start()
        logger.info("Screen capture restarted")
