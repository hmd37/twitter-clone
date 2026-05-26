from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from app.utils.dependencies import get_db
from app.utils.connection_manager import manager
from app.utils.jwt import decode_access_token
from app.models.user import User
from app.models.message import Message

router = APIRouter(tags=["Chat"])


@router.websocket("/ws/{token}")
async def websocket_endpoint(token: str, websocket: WebSocket, db: Session = Depends(get_db)):
    user_id = decode_access_token(token)

    if user_id is None:
        await websocket.close(code=4001)
        return

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        await websocket.close(code=4001)
        return

    await manager.connect(user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            receiver_username = data.get("to")
            content = data.get("content", "").strip()

            if not receiver_username or not content:
                await websocket.send_json({"error": "Missing 'to' or 'content'"})
                continue

            if len(content) > 1000:
                await websocket.send_json({"error": "Message too long"})
                continue

            receiver = db.query(User).filter(User.username == receiver_username).first()

            if not receiver:
                await websocket.send_json({"error": f"User '{receiver_username}' not found"})
                continue

            # save to database
            message = Message(
                content=content,
                sender_id=user_id,
                receiver_id=receiver.id
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            payload = {
                "id": message.id,
                "content": message.content,
                "from": user.username,
                "to": receiver.username,
                "created_at": message.created_at.isoformat()
            }

            # deliver to receiver if connected
            await manager.send_to_user(receiver.id, payload)

            # echo back to sender with sent flag
            await websocket.send_json({**payload, "sent": True})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
