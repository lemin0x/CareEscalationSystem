"""
WebSocket connection manager for real-time notifications.
"""
from typing import List, Dict, Any
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manages WebSocket connections for real-time alerts."""
    
    def __init__(self):
        """Initialize connection manager with empty connections list."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: Dictionary message to send
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            # Connection may be closed, remove it
            self.disconnect(websocket)
            raise e
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected WebSocket clients.
        
        Args:
            message: Dictionary message to broadcast
        """
        # Create a copy of connections list to avoid modification during iteration
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Mark for removal if connection is closed
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


# Global WebSocket manager instance
websocket_manager = ConnectionManager()

