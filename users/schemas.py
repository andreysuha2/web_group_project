from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
# from contacts.schemas import ContactResponse
from typing import List

class UserCreationModel(BaseModel):
    username: str = Field(min_length=5, max_length=20, example="username")
    email: EmailStr
    password: str = Field(min_length=6)

class UserModel(BaseModel):
    username: str
    email: EmailStr
    # avatar: str
    created_at: datetime

class UserResponse(UserModel):
    id: int

    class Config:
        from_attributes = True

class TokenPairModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RequestEmail(BaseModel):
    email: EmailStr