from fastapi import APIRouter, WebSocket

router = APIRouter()
active_connections =  {}


@router.websocket("/comments/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await websocket.accept()
    
    if project_id not in active_connections:
        active_connections[project_id] = []
    active_connections[project_id].append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        active_connections[project_id].remove(websocket)
        if not active_connections[project_id]:
            del active_connections[project_id]


async def notify_clients(project_id: str, message: str):
    for connection in active_connections[project_id]:
        await connection.send_json({"message": message})
