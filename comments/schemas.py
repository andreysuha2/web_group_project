from pydantic import BaseModel
from datetime import datetime

class CommentModel(BaseModel):
    text: str

class CommentResponse(CommentModel):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True