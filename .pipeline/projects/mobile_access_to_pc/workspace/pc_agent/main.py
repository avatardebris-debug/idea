#!/usr/bin/env python3
"""
Mobile Access to PC - PC Agent Main Entry Point

This is the main entry point for the PC agent that handles screen capture,
input processing, and WebSocket communication.
"""

import asyncio
import json
import logging
import os
import signal
import sys

import websockets
from websockets.server import serve

from config import ConfigLoader
from screen_capture import ScreenCapture
from connection_manager import ConnectionManager
from input_handler import InputHandler
from input_types import InputParser
from utils.compression import VideoCompressor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pc_agent.log')
    ]
)
logger = logging.getLogger(__name__)


class WebSocketServer:
    """WebSocket server for PC Agent."""
    
    def __init__(self, config):
        """Initialize WebSocket server."""
        self.config = config
        self.server_config = config.server_config
        self.connection_manager = ConnectionManager(self.server_config)
        self.input_handler = InputHandler(config.input_config)
        self.screen_capture = ScreenCapture(config.screen_config)
        self.video_compressor = VideoCompressor(config.screen_config)
        self._server = None
        self._running = False
        
        logger.info("WebSocketServer initialized")
    
    async def handle_connection(self, websocket):
        """Handle a new WebSocket connection."""
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
    
    async def _send_welcome(self, websocket, client_id: str):
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
    
    async def _send_frames(self, websocket):
        """Send screen frames to client."""
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
    
    async def _process_message(self, websocket, client_id: str, message: str):
        """Process incoming message from client."""
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


class PCAgent:
    """Main PC Agent class that coordinates all components."""
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize the PC Agent with configuration."""
        self.config_path = config_path
        
        # Load configuration
        loader = ConfigLoader(config_path)
        self.config = loader.load()
        
        # Initialize components
        self.server_config = self.config.server_config
        self.screen_config = self.config.screen_config
        self.input_config = self.config.input_config
        
        self.server = WebSocketServer(self.config)
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("PC Agent initialized successfully")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    async def start(self):
        """Start the PC Agent."""
        self.running = True
        await self.server.start()
    
    def stop(self):
        """Stop the PC Agent."""
        logger.info("Stopping PC Agent...")
        self.running = False
        self.server.stop()
        logger.info("PC Agent stopped")


def main():
    """Main entry point."""
    config_path = os.environ.get('PC_AGENT_CONFIG', 'config.json')
    
    agent = PCAgent(config_path)
    
    try:
        asyncio.run(agent.start())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        agent.stop()


if __name__ == '__main__':
    main()
