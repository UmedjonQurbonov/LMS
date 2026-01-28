from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from server.settings import get_db
from accounts.permissions import get_current_user
from accounts.models import User
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from .chat_ws import manager
from .models import Chat, Message, Group, GroupMember, GroupMessage
from .schemas import *


chat_router = APIRouter(prefix="/chats", tags=["Chats"])

@chat_router.post("", response_model=ChatResponseSchema)
def create_chat(
    data: ChatCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # проверка: не создавать дубликат
    existing = db.query(Chat).filter_by(
        student_id=user.id,
        teacher_id=data.teacher_id,
        booking_id=data.booking_id
    ).first()
    if existing:
        return existing

    chat = Chat(
        student_id=user.id,
        teacher_id=data.teacher_id,
        booking_id=data.booking_id,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@chat_router.get("", response_model=List[ChatResponseSchema])
def my_chats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Chat).filter(
        (Chat.student_id == user.id) | (Chat.teacher_id == user.id)
    ).all()


@chat_router.get("/{chat_id}/messages", response_model=List[MessageResponseSchema])
def chat_messages(
    chat_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    chat = db.query(Chat).filter_by(id=chat_id).first()
    if not chat:
        raise HTTPException(404, "Chat not found")

    if user.id not in (chat.student_id, chat.teacher_id):
        raise HTTPException(403, "Access denied")

    return db.query(Message).filter_by(chat_id=chat_id).order_by(Message.created_at).all()


group_router = APIRouter(prefix="/groups", tags=["Groups"])


@group_router.post("", response_model=GroupResponseSchema)
def create_group(
    data: GroupCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    group = Group(name=data.name, owner_id=user.id)
    db.add(group)
    db.commit()
    db.refresh(group)

    # владелец — админ
    member = GroupMember(group_id=group.id, user_id=user.id, is_admin=True)
    db.add(member)
    db.commit()

    return group


@group_router.get("", response_model=List[GroupResponseSchema])
def my_groups(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Group)
        .join(GroupMember)
        .filter(GroupMember.user_id == user.id)
        .all()
    )


@group_router.post("/{group_id}/members", response_model=GroupMemberResponseSchema)
def add_member(
    group_id: int,
    data: GroupMemberCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    admin = db.query(GroupMember).filter_by(
        group_id=group_id, user_id=user.id, is_admin=True
    ).first()
    if not admin:
        raise HTTPException(403, "Only admin can add members")

    member = GroupMember(group_id=group_id, user_id=data.user_id)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@group_router.get("/{group_id}/messages", response_model=List[GroupMessageResponseSchema])
def group_messages(
    group_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    member = db.query(GroupMember).filter_by(group_id=group_id, user_id=user.id).first()
    if not member:
        raise HTTPException(403, "Not a group member")

    return (
        db.query(GroupMessage)
        .filter_by(group_id=group_id)
        .order_by(GroupMessage.created_at)
        .all()
    )



chat_router = APIRouter(prefix="/chats", tags=["Chats"])

@chat_router.websocket("/ws/{chat_id}")
async def chat_ws(
    websocket: WebSocket,
    chat_id: int,
    db: Session = Depends(get_db),
):
    await manager.connect(chat_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()

            message = Message(
                chat_id=chat_id,
                sender_id=data["sender_id"],
                text=data["text"],
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            await manager.broadcast(
                chat_id,
                {
                    "id": message.id,
                    "chat_id": chat_id,
                    "sender_id": message.sender_id,
                    "text": message.text,
                    "created_at": message.created_at.isoformat(),
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
