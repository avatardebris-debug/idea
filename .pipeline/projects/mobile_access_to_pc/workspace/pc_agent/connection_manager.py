"""
Connection Manager for PC Agent

This module handles WebSocket connection state management,
including connection tracking, disconnection handling, and
automatic reconnection logic.
"""

import asyncio
import json
import logging
import time

import websockets
from websockets.server import WebSocketServerProtocol

from config import ServerConfig

logger = logging.getLogger(__name__)


class ConnectionState:
    """Enumeration of possible connection states."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class ConnectionManager:
    """
    Manages WebSocket connections to PC Agent.
    
    Features:
    - Track multiple client connections
    - Connection state management
    - Automatic reconnection with exponential backoff
    - Heartbeat monitoring
    - Graceful disconnection handling
    """
    
    def __init__(self, config: ServerConfig):
        """
        Initialize connection manager.
        
        Args:
            config: ServerConfig with connection settings
        """
        self.config = config
        self._clients: dict[str, WebSocketServerProtocol] = {}
        self._states: dict[str, str] = {}
        self._last_activity: dict[str, float] = {}
        self._reconnect_attempts: dict[str, int] = {}
        self._reconnect_times: dict[str, float] = {}
        self._running = False
        
        logger.info("ConnectionManager initialized")
    
    def add_client(self, client_id: str, websocket: WebSocketServerProtocol):
        """
        Add a new client connection.
        
        Args:
            client_id: Unique identifier for the client
            websocket: WebSocket connection object
        """
        self._clients[client_id] = websocket
        self._states[client_id] = ConnectionState.CONNECTED
        self._last_activity[client_id] = time.time()
        self._reconnect_attempts[client_id] = 0
        self._reconnect_times[client_id] = 0
        
        logger.info(f"Client added: {client_id}")
    
    def remove_client(self, client_id: str):
        """
        Remove a client connection.
        
        Args:
            client_id: Unique identifier for the client
        """
        if client_id in self._clients:
            del self._clients[client_id]
        if client_id in self._states:
            del self._states[client_id]
        if client_id in self._last_activity:
            del self._last_activity[client_id]
        if client_id in self._reconnect_attempts:
            del self._reconnect_attempts[client_id]
        if client_id in self._reconnect_times:
            del self._reconnect_times[client_id]
        
        logger.info(f"Client removed: {client_id}")
    
    def is_connected(self, websocket: WebSocketServerProtocol) -> bool:
        """
        Check if a websocket connection is active.
        
        Args:
            websocket: WebSocket connection object
            
        Returns:
            True if connection is active, False otherwise
        """
        for client_id, ws in self._clients.items():
            if ws == websocket:
                return self._states.get(client_id) == ConnectionState.CONNECTED
        return False
    
    def get_client_id(self, websocket: WebSocketServerProtocol) -> str | None:
        """
        Get client ID for a websocket connection.
        
        Args:
            websocket: WebSocket connection object
            
        Returns:
            Client ID if found, None otherwise
        """
        for client_id, ws in self._clients.items():
            if ws == websocket:
                return client_id
        return None
    
    def mark_activity(self, client_id: str):
        """
        Mark a client as active.
        
        Args:
            client_id: Unique identifier for the client
        """
        self._last_activity[client_id] = time.time()
    
    def get_active_clients(self) -> list:
        """
        Get list of active client IDs.
        
        Returns:
            List of client IDs with CONNECTED state
        """
        return [
            client_id for client_id, state in self._states.items()
            if state == ConnectionState.CONNECTED
        ]
    
    def get_client_count(self) -> int:
        """
        Get number of active clients.
        
        Returns:
            Number of connected clients
        """
        return len(self.get_active_clients())
    
    def close_client(self, client_id: str):
        """
        Close a specific client connection.
        
        Args:
            client_id: Unique identifier for the client
        """
        if client_id in self._clients:
            try:
                websocket = self._clients[client_id]
                asyncio.create_task(websocket.close(1000, "Connection closed"))
                self._states[client_id] = ConnectionState.DISCONNECTED
                logger.info(f"Client closed: {client_id}")
            except Exception as e:
                logger.error(f"Error closing client {client_id}: {e}")
    
    def close_all(self):
        """Close all client connections."""
        for client_id in list(self._clients.keys()):
            self.close_client(client_id)
        logger.info("All connections closed")
    
    async def send_to_client(self, client_id: str, message: dict) -> bool:
        """
        Send a message to a specific client.
        
        Args:
            client_id: Unique identifier for the client
            message: Message dictionary to send
            
        Returns:
            True if message was sent, False otherwise
        """
        if client_id not in self._clients:
            logger.warning(f"Client not found: {client_id}")
            return False
        
        try:
            websocket = self._clients[client_id]
            if websocket.open:
                await websocket.send(json.dumps(message))
                self.mark_activity(client_id)
                return True
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Connection closed for client: {client_id}")
            self._states[client_id] = ConnectionState.DISCONNECTED
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
        
        return False
    
    async def broadcast(self, message: dict, exclude_client: str | None = None) -> int:
        """
        Send a message to all connected clients.
        
        Args:
            message: Message dictionary to send
            exclude_client: Optional client ID to exclude
        """
        sent_count = 0
        for client_id in self.get_active_clients():
            if client_id != exclude_client:
                if await self.send_to_client(client_id, message):
                    sent_count += 1
        
        logger.info(f"Broadcast sent to {sent_count} clients")
        return sent_count
    
    def calculate_backoff(self, client_id: str) -> float:
        """
        Calculate exponential backoff time for reconnection.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Backoff time in seconds
        """
        import random
        
        attempts = self._reconnect_attempts.get(client_id, 0)
        base_backoff = 1.0  # 1 second base
        max_backoff = 30.0  # 30 seconds max
        
        # Exponential backoff with jitter
        backoff = min(max_backoff, base_backoff * (2 ** attempts))
        jitter = backoff * 0.2  # 20% jitter
        
        return backoff + (jitter * (0.5 - random.random()))
    
    def increment_reconnect_attempt(self, client_id: str):
        """Increment reconnect attempt counter for a client."""
        attempts = self._reconnect_attempts.get(client_id, 0)
        self._reconnect_attempts[client_id] = attempts + 1
    
    def reset_reconnect_attempts(self, client_id: str):
        """Reset reconnect attempt counter for a client."""
        self._reconnect_attempts[client_id] = 0
        self._reconnect_times[client_id] = 0
    
    async def start_heartbeat_monitor(self):
        """Start monitoring client heartbeats."""
        self._running = True
        
        while self._running:
            try:
                current_time = time.time()
                
                for client_id in list(self._last_activity.keys()):
                    time_since_activity = current_time - self._last_activity[client_id]
                    
                    if time_since_activity > self.config.connection_timeout:
                        logger.warning(f"Client timeout: {client_id}")
                        self.close_client(client_id)
                
                await asyncio.sleep(self.config.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitor: {e}")
                await asyncio.sleep(5)
    
    def stop_heartbeat_monitor(self):
        """Stop heartbeat monitoring."""
        self._running = False
        logger.info("Heartbeat monitor stopped")
    
    def get_connection_stats(self) -> dict:
        """
        Get connection statistics.
        
        Returns:
            Dictionary with connection statistics
        """
        return {
            'total_clients': len(self._clients),
            'connected_clients': len(self.get_active_clients()),
            'states': dict(self._states),
            'average_reconnect_attempts': (
                sum(self._reconnect_attempts.values()) / len(self._reconnect_attempts)
                if self._reconnect_attempts else 0
            )
        }
