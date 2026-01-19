from pydantic import BaseModel, model_validator, field_validator, ValidationError, ConfigDict, Field
from .models import Permission
from typing import Optional, List

class RegisterSchema(BaseModel):
    username:str
    password:str

    model_config = ConfigDict(extra="forbid")
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value



class AddUserShcema(BaseModel):
    username:str
    password:str
    confirm_password:str
    is_staff:bool = False
    is_superuser:bool = False
    

class LoginSchema(BaseModel):
    username:str
    password:str

    @field_validator('*', mode='before')
    def not_empty_validators(value):
        if not value:
            raise ValidationError('Fields are required')
        return value    

class UserSchema(BaseModel):
    id:int
    username:str
    permissions:list["PermissionSchema"]
    roles:list["RoleSchema"]
    
    model_config=ConfigDict(from_attributes=True)
    
    
class SetUserPermissionsSchema(BaseModel):
    user_id:int
    permissions:list[int] 

    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value

class SetRolePermissionsSchema(BaseModel):
    role_id:int
    permissions:list[int]
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required")
        return value


class PermissionSchema(BaseModel):
    id:int
    name:str
    description:str


class RoleSchema(BaseModel):
    id:int
    name:str
    permissions:list[PermissionSchema]
    
class AddRoleSchema(BaseModel):
    name:str
    
    @field_validator("name", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("role name must be set!")
        return value


class SetRoleToUserSchema(BaseModel):
    user_id:int
    roles:list[int]
    
    @field_validator("*", mode="before")
    def not_empty_validators(value):
        if not value:
            raise ValueError("Fields are required!")
        return value


