from sqlalchemy import String, Integer, ForeignKey, Text, Integer, String, ForeignKey, false, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from server.models import BaseModel
from accounts.models import User

class TeacherProfile(BaseModel):
    __tablename__ = "teacher_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    description: Mapped[str] = mapped_column(Text)
    price_per_lesson: Mapped[int] = mapped_column(Integer, nullable=False)

    is_verified: Mapped[bool] = mapped_column(server_default=false(), nullable=False)

    rating: Mapped[int] = mapped_column(Integer, server_default="0")

    user: Mapped["User"] = relationship()


class StudentProfile(BaseModel):
    __tablename__ = "student_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    full_name: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship()

class Subject(BaseModel):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

class TeacherSubject(BaseModel):
    __tablename__ = "teacher_subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))


class ScheduleSlot(BaseModel):
    __tablename__ = "schedule_slots"

    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id"))

    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[str] = mapped_column(String, default="available") 


class Booking(BaseModel):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)

    slot_id: Mapped[int] = mapped_column(ForeignKey("schedule_slots.id"))
    student_id: Mapped[int] = mapped_column(ForeignKey("student_profiles.id"))
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher_profiles.id"))

    status: Mapped[str] = mapped_column(String, default="booked")  


class Payment(BaseModel):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id")
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(
        String, default="pending"
    )  


class Review(BaseModel):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id")
    )
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teacher_profiles.id")
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("student_profiles.id")
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text)



class Lesson(BaseModel):
    __tablename__ = "lessons"

    id = mapped_column(Integer, primary_key=True)
    subject_id = mapped_column(ForeignKey("subjects.id"))
    title = mapped_column(String(255))
    description = mapped_column(String, nullable=True)

    subject = relationship("Subject", back_populates="lessons")
    questions = relationship("Question", back_populates="lesson")


class Question(BaseModel):
    __tablename__ = "questions"

    id = mapped_column(Integer, primary_key=True)
    lesson_id = mapped_column(ForeignKey("lessons.id"))
    text = mapped_column(String)
    type = mapped_column(String, default="single")

    lesson = relationship("Lesson", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


class Answer(BaseModel):
    __tablename__ = "answers"

    id = mapped_column(Integer, primary_key=True)
    question_id = mapped_column(ForeignKey("questions.id"))
    text = mapped_column(String)
    is_correct = mapped_column(Boolean, default=False)

    question = relationship("Question", back_populates="answers")


