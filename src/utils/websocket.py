from typing import List
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    Manages active WebSocket connections for real-time updates.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accepts a new WebSocket connection and adds it to the list of active connections.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected: {websocket}. Total active: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        """
        Removes a WebSocket connection from the list of active connections.
        """
        try:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected: {websocket}. Total active: {len(self.active_connections)}")
        except ValueError:
            # Connection might have already been removed by broadcast cleanup
            logger.warning(f"Attempted to disconnect a WebSocket ({websocket}) not found in active connections.")


    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Sends a message to a specific WebSocket client.
        """
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            logger.warning(f"Failed to send personal message to {websocket}: Client disconnected.")
            await self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending personal message to WebSocket client {websocket}: {e}")
            await self.disconnect(websocket)

    async def broadcast(self, message: str):
        """
        Sends a message to all active WebSocket clients.
        Handles disconnection if a client is no longer available.
        """
        disconnected_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                # Client has disconnected, mark for removal
                disconnected_connections.append(connection)
                logger.warning(f"Client {connection} disconnected during broadcast.")
            except Exception as e:
                # Log other potential errors, but assume connection might be dead
                logger.error(f"Error sending broadcast to WebSocket client {connection}: {e}")
                disconnected_connections.append(connection)

        for connection in disconnected_connections:
            # Use disconnect method to ensure consistent cleanup and logging
            await self.disconnect(connection)

# Singleton instance to be used across the application
websocket_manager = WebSocketManager()