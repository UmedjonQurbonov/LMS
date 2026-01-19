from passlib.hash import argon2
from fastapi import HTTPException, status
from server.settings import (
    JWT_ALGORITHM, JWT_SECRET_KEY, 
    ACCESSTOKEN_EXPIRED_TIME, REFRESHTOKEN_EXPIRED_TIME)
import jwt
from datetime import datetime, timedelta, timezone





def hash_password(password):
    return argon2.hash(password)

def verify_password(password, hashed_password):
    return argon2.verify(password, hashed_password)


def generate_token(payload, expired_time):
    current_time = datetime.now(timezone.utc)
    payload.update({
        "iat":current_time,
        "exp":current_time + expired_time
    })
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(username, user_id):
    payload = {
        "sub":str(user_id),
        "username":username,
        "type":"access",
    }
    return generate_token(payload, ACCESSTOKEN_EXPIRED_TIME)


def create_refresh_token(username, user_id):
    payload = {
        "sub":str(user_id),
        "username":username,
        "type":"refresh",
    }
    return generate_token(payload, REFRESHTOKEN_EXPIRED_TIME)



def decode_jwt(token:str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )