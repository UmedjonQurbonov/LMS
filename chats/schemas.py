from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChatCreateSchema(BaseModel):
    teacher_id: int
    booking_id: Optional[int] = None


class ChatResponseSchema(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    booking_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class MessageCreateSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)



class MessageResponseSchema(BaseModel):
    id: int
    chat_id: int
    sender_id: int
    text: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class GroupCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)




class GroupResponseSchema(BaseModel):
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class GroupMemberCreateSchema(BaseModel):
    user_id: int


class GroupMessageCreateSchema(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)


class GroupMessageResponseSchema(BaseModel):
    id: int
    group_id: int
    sender_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True

class GroupMemberResponseSchema(BaseModel):
    id: int
    group_id: int
    user_id: int
    is_admin: bool
    joined_at: datetime

    class Config:
        from_attributes = True
