from sqlalchemy import ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from server.models import BaseModel


class Chat(BaseModel):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    booking_id: Mapped[int | None] = mapped_column(ForeignKey("bookings.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete"
    )


class Message(BaseModel):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    chat: Mapped["Chat"] = relationship(back_populates="messages")


class Group(BaseModel):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    members: Mapped[list["GroupMember"]] = relationship(
        back_populates="group",
        cascade="all, delete"
    )

    messages: Mapped[list["GroupMessage"]] = relationship(
        back_populates="group",
        cascade="all, delete"
    )


class GroupMember(BaseModel):
    __tablename__ = "group_members"

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    is_admin: Mapped[bool] = mapped_column(default=False)

    group: Mapped["Group"] = relationship(back_populates="members")



class GroupMessage(BaseModel):
    __tablename__ = "group_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    group: Mapped["Group"] = relationship(back_populates="messages")

