from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from server.settings import get_db
from .models import *
from accounts.models import User
from .schemas import *
from accounts.permissions import get_current_user
from typing import List


teacher_router = APIRouter(prefix="/teachers", tags=["Teachers"])

@teacher_router.post("/profile", response_model=TeacherProfileResponseSchema)
def create_teacher_profile(
    data: TeacherProfileCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = TeacherProfile(user_id=user.id, description=data.description, price_per_lesson=data.price_per_lesson)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

@teacher_router.get("/profile/me", response_model=TeacherProfileResponseSchema)
def get_my_teacher_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(TeacherProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@teacher_router.put("/profile/me", response_model=TeacherProfileResponseSchema)
def update_teacher_profile(
    data: TeacherProfileUpdateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = db.query(TeacherProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile

@teacher_router.get("/{teacher_id}", response_model=TeacherProfileResponseSchema)
def get_teacher_profile(teacher_id: int, db: Session = Depends(get_db)):
    profile = db.query(TeacherProfile).filter_by(id=teacher_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return profile


@teacher_router.post("/subjects")
def assign_subject_to_teacher(
    data: TeacherSubjectCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    teacher_profile = db.query(TeacherProfile).filter_by(user_id=user.id).first()
    if not teacher_profile:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
    teacher_subject = TeacherSubject(teacher_id=teacher_profile.id, subject_id=data.subject_id)
    db.add(teacher_subject)
    db.commit()
    return {"status": "subject assigned"}

@teacher_router.get("", response_model=List[TeacherProfileResponseSchema])
def search_teachers(
    subject: int = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    rating: int = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(TeacherProfile)
    if min_price is not None:
        query = query.filter(TeacherProfile.price_per_lesson >= min_price)
    if max_price is not None:
        query = query.filter(TeacherProfile.price_per_lesson <= max_price)
    if rating is not None:
        query = query.filter(TeacherProfile.rating >= rating)
    if subject is not None:
        query = query.join(TeacherSubject).filter(TeacherSubject.subject_id == subject)
    return query.all()


@teacher_router.get("/slots/{teacher_id}", response_model=List[ScheduleSlotResponseSchema])
def get_teacher_slots(teacher_id: int, db: Session = Depends(get_db)):
    return db.query(ScheduleSlot).filter_by(teacher_id=teacher_id).all()


student_router = APIRouter(prefix="/students", tags=["Students"])

@student_router.get("/profile/me", response_model=StudentProfileResponseSchema)
def get_my_student_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@student_router.put("/profile/me", response_model=StudentProfileResponseSchema)
def update_student_profile(
    data: StudentProfileCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    profile.full_name = data.full_name
    db.commit()
    db.refresh(profile)
    return profile


subject_router = APIRouter(prefix="/subjects", tags=["Subjects"])

@subject_router.post("", response_model=SubjectResponseSchema)
def create_subject(data: SubjectCreateSchema, db: Session = Depends(get_db)):
    subject = Subject(name=data.name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@subject_router.get("", response_model=List[SubjectResponseSchema])
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()


schedule_router = APIRouter(prefix="/schedule", tags=["Schedule"])

@schedule_router.post("/slots", response_model=ScheduleSlotResponseSchema)
def create_slot(data: ScheduleSlotCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    slot = ScheduleSlot(teacher_id=user.id, start_time=data.start_time, end_time=data.end_time)
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot

@schedule_router.get("/slots/me", response_model=List[ScheduleSlotResponseSchema])
def my_slots(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(ScheduleSlot).filter_by(teacher_id=user.id).all()

@schedule_router.delete("/slots/{slot_id}")
def delete_slot(slot_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    slot = db.query(ScheduleSlot).filter_by(id=slot_id, teacher_id=user.id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    db.delete(slot)
    db.commit()
    return {"status": "deleted"}


booking_router = APIRouter(prefix="/bookings", tags=["Bookings"])

@booking_router.post("", response_model=BookingResponseSchema)
def create_booking(data: BookingCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    slot = db.query(ScheduleSlot).filter_by(id=data.slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    booking = Booking(student_id=user.id, teacher_id=slot.teacher_id, slot_id=slot.id, status="booked")
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@booking_router.get("/me", response_model=List[BookingResponseSchema])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Booking).filter((Booking.student_id==user.id)|(Booking.teacher_id==user.id)).all()

@booking_router.get("/{booking_id}", response_model=BookingResponseSchema)
def get_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@booking_router.patch("/{booking_id}/cancel")
def cancel_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()
    return {"status": "cancelled"}

@booking_router.patch("/{booking_id}/complete")
def complete_booking(booking_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter_by(id=booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "completed"
    db.commit()
    return {"status": "completed"}


payment_router = APIRouter(prefix="/payments", tags=["Payments"])

@payment_router.post("", response_model=PaymentResponseSchema)
def create_payment(data: PaymentCreateSchema, db: Session = Depends(get_db)):
    payment = Payment(booking_id=data.booking_id, amount=data.amount, status="pending")
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment

@payment_router.get("/me", response_model=List[PaymentResponseSchema])
def my_payments(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Payment).filter_by(student_id=user.id).all()

@payment_router.get("/{payment_id}", response_model=PaymentResponseSchema)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@payment_router.patch("/{payment_id}/pay")
def pay(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "paid"
    db.commit()
    return {"status": "paid"}

@payment_router.patch("/{payment_id}/release")
def release(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment.status = "released"
    db.commit()
    return {"status": "released"}


review_router = APIRouter(prefix="/reviews", tags=["Reviews"])

@review_router.post("", response_model=ReviewResponseSchema)
def create_review(data: ReviewCreateSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    review = Review(teacher_id=data.teacher_id, student_id=user.id, rating=data.rating, comment=data.comment)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

@review_router.get("/teacher/{teacher_id}", response_model=List[ReviewResponseSchema])
def teacher_reviews(teacher_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter_by(teacher_id=teacher_id).all()


parent_router = APIRouter(prefix="/parents", tags=["Parents"])

@parent_router.get("/children/{student_id}/bookings", response_model=List[BookingResponseSchema])
def child_bookings(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Booking).filter_by(student_id=student_id).all()

@parent_router.get("/children/{student_id}/reviews", response_model=List[ReviewResponseSchema])
def child_reviews(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    student = db.query(StudentProfile).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return db.query(Review).filter_by(student_id=student_id).all()


utils_router = APIRouter(tags=["Utils"])

@utils_router.get("/health")
def health_check():
    return {"status": "ok"}


lesson_router = APIRouter(prefix="/lessons", tags=["Lessons"])


@lesson_router.post("", response_model=LessonResponseSchema)
def create_lesson(
    data: LessonCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    lesson = Lesson(
        subject_id=data.subject_id,
        title=data.title,
        description=data.description,
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson

@lesson_router.get("/{lesson_id}", response_model=LessonResponseSchema)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not lesson:
        raise HTTPException(404, "Lesson not found")
    return lesson

@lesson_router.get("/subject/{subject_id}", response_model=List[LessonResponseSchema])
def subject_lessons(subject_id: int, db: Session = Depends(get_db)):
    return db.query(Lesson).filter_by(subject_id=subject_id).all()


question_router = APIRouter(prefix="/questions", tags=["Questions"])


@question_router.post("", response_model=QuestionResponseSchema)
def create_question(
    data: QuestionCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    question = Question(
        lesson_id=data.lesson_id,
        text=data.text,
        type=data.type,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@question_router.get("/lesson/{lesson_id}", response_model=List[QuestionResponseSchema])
def lesson_questions(lesson_id: int, db: Session = Depends(get_db)):
    return db.query(Question).filter_by(lesson_id=lesson_id).all()



answer_router = APIRouter(prefix="/answers", tags=["Answers"])


@answer_router.post("", response_model=AnswerResponseSchema)
def create_answer(
    data: AnswerCreateSchema,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    answer = Answer(
        question_id=data.question_id,
        text=data.text,
        is_correct=data.is_correct,
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@answer_router.get("/question/{question_id}", response_model=List[AnswerResponseSchema])
def question_answers(question_id: int, db: Session = Depends(get_db)):
    return db.query(Answer).filter_by(question_id=question_id).all()


