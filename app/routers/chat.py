import asyncio

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.user import User
from app.schemas.message import ConversationUser, MessageResponse
from app.utils.connection_manager import manager
from app.utils.dependencies import get_db, require_current_user
from app.utils.jwt import decode_access_token

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

    # start listening to this user's Redis channel in background
    subscribe_task = asyncio.create_task(manager.subscribe(user_id))

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
                await websocket.send_json(
                    {"error": f"User '{receiver_username}' not found"}
                )
                continue

            message = Message(
                content=content, sender_id=user_id, receiver_id=receiver.id
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            payload = {
                "id": message.id,
                "content": message.content,
                "from": user.username,
                "to": receiver.username,
                "created_at": message.created_at.isoformat(),
            }

            # publish to receiver's Redis channel
            await manager.publish(receiver.id, payload)

            # echo back to sender
            await websocket.send_json({**payload, "sent": True})

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        subscribe_task.cancel()


@router.get("/conversations", response_model=list[ConversationUser])
def get_conversations(db: Session = Depends(get_db), current_user: User = Depends(require_current_user)):
    messages = (
        db.query(Message)
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.receiver_id == current_user.id,
            )
        )
        .all()
    )

    user_ids = set()
    for m in messages:
        if m.sender_id != current_user.id:
            user_ids.add(m.sender_id)
        if m.receiver_id != current_user.id:
            user_ids.add(m.receiver_id)

    users = db.query(User).filter(User.id.in_(user_ids)).all()
    return users


@router.get("/conversations/{username}", response_model=list[MessageResponse])
def get_conversation(
    username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_current_user),
):
    other_user = db.query(User).filter(User.username == username).first()

    if not other_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(
                    Message.sender_id == current_user.id,
                    Message.receiver_id == other_user.id,
                ),
                and_(
                    Message.sender_id == other_user.id,
                    Message.receiver_id == current_user.id,
                ),
            )
        )
        .order_by(Message.created_at.asc())
        .all()
    )

    for m in messages:
        if m.receiver_id == current_user.id and not m.is_read:
            m.is_read = True
    db.commit()

    return messages
