from itertools import count
from typing import List
from datetime import datetime
from pydantic import Field, BaseModel, EmailStr, model_validator  
from users import models


class UserCreationModel(BaseModel):
    username: str = Field(min_length=5, max_length=20, example="username")
    email: EmailStr
    password: str = Field(min_length=6)


class UserModel(BaseModel):
    username: str
    email: EmailStr
    created_at: datetime


class UserProfileModel(BaseModel):
    email: EmailStr
    password : str = Field(min_length=6)


class UserResponse(UserModel):
    id: int
    role: models.UserRoles

    class Config:
        from_attributes = True


class UserSelfModel(UserResponse):
    # photos: List[PhotoResponse]
    photos_count: int


class TokenPairModel(BaseModel):
    access_token: dict
    refresh_token: dict
    token_type: str 


class TokenLoginResponse(BaseModel):
    access_token: str
    access_expired_at: datetime
    refresh_token: str
    refresh_expired_at: datetime
    token_type: str


class TokenModel(BaseModel):
    access_token: dict
    expired_at: datetime


class RequestEmail(BaseModel):
    email: EmailStr

    
