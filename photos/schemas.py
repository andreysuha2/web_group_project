from pydantic import BaseModel

class PhotoModel(BaseModel):
    pass

class PhotoResponse(PhotoModel):
    id: int

    class Config:
        from_attributes = True

class TagModel(BaseModel):
    pass

class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True