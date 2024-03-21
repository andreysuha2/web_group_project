from pydantic import BaseModel

class CommentModel(BaseModel):
    pass

class CommentResponse(CommentModel):
    id: int

    class Config:
        from_attributes = True