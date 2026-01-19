from fastapi import HTTPException, status
from .security import decode_jwt
from .models import BlackListTokens

def validate_access_token(token:str, db):
    credentials = decode_jwt(token)
    is_blocked_token = db.query(BlackListTokens).filter(BlackListTokens.token == token).first()
    if is_blocked_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already blocked")
    if credentials["type"] != "access":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token")
    return credentials

def validate_refresh_token(token:str, db):
    is_blocked_token = db.query(BlackListTokens).filter(BlackListTokens.token == token).first()
    if is_blocked_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already blocked")
    
    credentials = decode_jwt(token)
    if credentials["type"] != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token")
    return credentials