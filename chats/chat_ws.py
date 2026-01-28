from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connections: dict[int, list[WebSocket]] = {}

    async def connect(self, chat_id: int, ws: WebSocket):
        await ws.accept()
        self.connections.setdefault(chat_id, []).append(ws)

    def disconnect(self, chat_id: int, ws: WebSocket):
        self.connections[chat_id].remove(ws)

    async def broadcast(self, chat_id: int, data: dict):
        for ws in self.connections.get(chat_id, []):
            await ws.send_json(data)


manager = ConnectionManager()
