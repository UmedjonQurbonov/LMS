from fastapi import APIRouter
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from server.settings import get_db
from .models import *
from .schemas import *
from .helpers import *
from .security import *
from .validators import *
from .permissions import *

auth = APIRouter()

@auth.post("/register", response_model=UserSchema)
async def register_api_view(data:RegisterSchema, db:Session=Depends(get_db)):
    print(data.username)
    user = get_user(username=data.username, db=db)
    if user is not None:
        raise HTTPException(detail="User already exists!", status_code=status.HTTP_400_BAD_REQUEST)
    password_hash = hash_password(data.password)
    new_user = User(username=data.username, password=password_hash)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth.post("/add-user", dependencies=[Depends(is_admin_user), Depends(role_required(["admin"]))], response_model=UserSchema)
async def add_user_api_view(data:AddUserShcema, db:Session=Depends(get_db)):
    q = get_user(username=data.username, db=db)
    if q is not None:
        raise HTTPException(detail="User already exists!", status_code=status.HTTP_400_BAD_REQUEST)
    user = create_user(data=data, db=db)
    return user


@auth.post("/login")
async def register_api_view(data:LoginSchema, db:Session=Depends(get_db)):
    user = authenticate(username=data.username, password=data.password, db=db)
    if not user:
        return HTTPException(detail="Invalid credentials!", status_code=status.HTTP_400_BAD_REQUEST)
    
    return {
        "refresh":create_refresh_token(user.username, user.id),
        "access":create_access_token(user.username, user.id)
    }


@auth.post("/logout", dependencies=[Depends(is_authenticated)])
async def logout_api_view(token:str, db:Session=Depends(get_db)):
    is_valid_token = validate_refresh_token(token, db)
    if is_valid_token is not None:
        blocked_token = BlackListTokens(token=token)
        db.add(blocked_token)
        db.commit()
        db.refresh(blocked_token)
        return {
            "message":"logged out user",
            "status":status.HTTP_200_OK
        }
    return HTTPException("Invalid or expired token!")



@auth.post("/refresh", dependencies=[Depends(is_authenticated)])
async def refresh_token(token:str, db:Session=Depends(get_db)):
    is_valid_token = validate_refresh_token(token=token, db=db)
    if is_valid_token:
        return {
            "refresh":token,
            "access":create_access_token(
                username=is_valid_token["username"],
                user_id=int(is_valid_token["sub"]))
        }
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid token"
    )


@auth.get("/me", response_model=UserSchema)
async def get_profile(user=Depends(get_current_user)):
    return user


@auth.post("/set-permissions-to-user", dependencies=[Depends(is_admin_user)], response_model=UserSchema)
async def set_permissions_to_user_api_view(data:SetUserPermissionsSchema, db:Session=Depends(get_db)):
    user = get_user(user_id=data.user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User doedn't exists!")
    permissions = db.query(Permission).filter(Permission.id.in_(data.permissions)).all()
    print(permissions)
    if not permissions:
        print("error")
        raise HTTPException(detail="Permission doesn't exists", status_code=status.HTTP_400_BAD_REQUEST)
    
    for perm in permissions:
        if perm not in user.permissions:
            user.permissions.append(perm)
    db.commit()
    db.refresh(user)
    return user


@auth.post("/add-role", response_model=RoleSchema)
async def create_role_api_view(data:AddRoleSchema, db:Session=Depends(get_db)):
    role = Role(name=data.name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@auth.post("/add-permissions-to-role", response_model=RoleSchema)
async def add_permissions_to_role(data:SetRolePermissionsSchema, db:Session=Depends(get_db)):
    role = db.query(Role).filter(Role.id==data.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role not found!")
    permissions = db.query(Permission).filter(Permission.id.in_(data.permissions)).all()
    print(permissions)
    if not permissions:
        print("error")
        raise HTTPException(detail="Permission doesn't exists", status_code=status.HTTP_400_BAD_REQUEST)
    
    for perm in permissions:
        if perm not in role.permissions:
            role.permissions.append(perm)
    db.commit()
    db.refresh(role)
    return role


@auth.post("/add-role-to-user", response_model=UserSchema)
async def add_role_to_user_view(data:SetRoleToUserSchema, db:Session=Depends(get_db)):
    user = get_user(user_id=data.user_id, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exists!")
    roles = db.query(Role).filter(Role.id.in_(data.roles)).all()
    if not roles:
        raise HTTPException(detail="Roles doesn't exists", status_code=status.HTTP_400_BAD_REQUEST)
    
    for r in roles:
        if r not in user.roles:
            user.roles.append(r)
    db.commit()
    db.refresh(user)
    return user


