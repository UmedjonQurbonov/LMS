from pydantic import BaseModel, Field
from typing import Optional

class TeacherProfileCreateSchema(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    price_per_lesson: int = Field(..., gt=0)

class TeacherProfileUpdateSchema(BaseModel):
    description: Optional[str] = Field(None, max_length=1000)
    price_per_lesson: Optional[int] = Field(None, gt=0)

class TeacherProfileResponseSchema(BaseModel):
    id: int
    description: Optional[str]
    price_per_lesson: int
    rating: int
    is_verified: bool

    class Config:
        from_attributes = True

class StudentProfileCreateSchema(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)

class StudentProfileResponseSchema(BaseModel):
    id: int
    full_name: str

    class Config:
        from_attributes = True

class SubjectCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

class SubjectResponseSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class TeacherSubjectCreateSchema(BaseModel):
    subject_id: int = Field(..., gt=0)

class ScheduleSlotCreateSchema(BaseModel):
    start_time: str = Field(..., example="2026-01-20 10:00")
    end_time: str = Field(..., example="2026-01-20 11:00")

class ScheduleSlotResponseSchema(BaseModel):
    id: int
    start_time: str
    end_time: str
    status: str

    class Config:
        from_attributes = True

class BookingCreateSchema(BaseModel):
    slot_id: int = Field(..., gt=0)

class BookingResponseSchema(BaseModel):
    id: int
    slot_id: int
    student_id: int
    teacher_id: int
    status: str

    class Config:
        from_attributes = True

class PaymentCreateSchema(BaseModel):
    booking_id: int = Field(..., gt=0)
    amount: int = Field(..., gt=0)

class PaymentResponseSchema(BaseModel):
    id: int
    booking_id: int
    amount: int
    status: str

    class Config:
        from_attributes = True

class ReviewCreateSchema(BaseModel):
    booking_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)

class ReviewResponseSchema(BaseModel):
    id: int
    rating: int
    comment: Optional[str]

    class Config:
        from_attributes = True

class MessageSchema(BaseModel):
    detail: str
