from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {"client_id": client_id}
        await self.broadcast_system_status()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            del self.connection_data[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove stale connections
                self.disconnect(connection)

    async def broadcast_system_status(self):
        status = {
            "type": "system_status",
            "data": {
                "active_connections": len(self.active_connections),
                "agents_active": 0,  # Will be updated with real data
                "workflows_running": 0,
                "timestamp": "2025-06-14T08:00:00Z"
            }
        }
        await self.broadcast(json.dumps(status))

    async def broadcast_agent_update(self, agent_id: str, status: str, message: str = ""):
        update = {
            "type": "agent_update",
            "data": {
                "agent_id": agent_id,
                "status": status,
                "message": message,
                "timestamp": "2025-06-14T08:00:00Z"
            }
        }
        await self.broadcast(json.dumps(update))

# Global connection manager
manager = ConnectionManager()
