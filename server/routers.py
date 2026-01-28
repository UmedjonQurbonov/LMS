from fastapi import FastAPI
from accounts.views import auth
from smartedu.views import *
from chats.views import *

app = FastAPI()

app.include_router(auth, prefix='/auth', tags=['accounts'])
app.include_router(teacher_router)
app.include_router(student_router)
app.include_router(subject_router)
app.include_router(schedule_router)
app.include_router(booking_router)
app.include_router(payment_router)
app.include_router(lesson_router)
app.include_router(question_router)
app.include_router(answer_router)
app.include_router(review_router)
app.include_router(parent_router)
app.include_router(utils_router)
app.include_router(chat_router)
app.include_router(group_router)
app.include_router(chat_router)


