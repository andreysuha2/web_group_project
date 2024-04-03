
from datetime import datetime
from typing import List, Optional
from pydantic import Field, BaseModel, EmailStr 

from users import models


# for users_photos response
class PhotoResponse(BaseModel):
    id: int
    name: str
    title: str
    description: Optional[str]


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


class UserSelfPhotos(BaseModel):
    id: int
    username: str
    email: EmailStr
    photos: List[PhotoResponse] 


class UserSelfModel(UserResponse):
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

