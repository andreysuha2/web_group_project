from pydantic import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    pass

class UserResponse(UserModel):
    id: int

    class Config:
        from_attributes = True

class TokenModel(BaseModel):
    token: str
    expired_at: datetime

class TokenPairModel(BaseModel):
    access: TokenModel
    refresh: TokenModel
    type: str = 'bearer'