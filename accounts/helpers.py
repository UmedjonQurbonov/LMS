from .models import User, Role
from .security import *
from sqlalchemy.orm import selectinload

def get_user(username:str=None, user_id:int=None, db:None=None):
    q = db.query(User).options(
        selectinload(User.permissions),
        selectinload(User.roles).selectinload(Role.permissions))
    if username:
        q = q.filter(User.username==username).first()
    elif user_id:
        q = q.filter(User.id==user_id).first()
    if q:
        return q
    return None


def authenticate(username:str, password:str=None, db:None=None):
    user = get_user(username=username, db=db)
    if user:
        is_password_correct = verify_password(password, user.password)
        if is_password_correct:
            return user
    return None



def _create_user_object(data):
    data["password"] = hash_password(data["password"])
    data.pop("confirm_password")
    new_user = User(**data)

    return new_user


def _create_user(data, db):
    user = _create_user_object(data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_user(data, db):
    data = data.model_dump()
    user = _create_user(data, db)
    return user


def create_superuser(data, db):
    data = data.model_dump()
    data.update({
        "is_staff":True,
        "is_superuser":True
    })
    user = _create_user(data,db)
    return user
    
    