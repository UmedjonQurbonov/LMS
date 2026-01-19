from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.settings import get_db
from .validators import validate_access_token
from .models import User



oauth_bearer = HTTPBearer(auto_error=False)



def is_authenticated(credentials:HTTPAuthorizationCredentials=Depends(oauth_bearer), db:Session=Depends(get_db)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized!"
        )
    is_valid_token = validate_access_token(token=credentials.credentials, db=db)
    if is_valid_token is not None:
        return is_valid_token
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized!"
        )


def get_current_user(credentials=Depends(is_authenticated), db:Session=Depends(get_db)):
    user = db.query(User).filter(User.username==credentials["username"]).first()
    return user


def required_permission(req_permissions:list):
    def has_permission(user=Depends(get_current_user)):
        user_permissions = [per.name for per in user.permissions]
        for role in user.roles:
            for per in role.permissions:
                user_permissions.append(per.name)
        for permission in req_permissions:
            if permission in user_permissions:
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied!"
        )
    return has_permission
            


def role_required(req_roles:list):
    def has_permission(user=Depends(get_current_user)):
        user_roles = [role.name for role in user.roles]
        
        for role in req_roles:
            if role in user_roles:
                return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied!"
        )
    return has_permission


def is_admin_user(user=Depends(get_current_user)):
    if user.is_staff==True or user.is_superuser:
        return True
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied!")        