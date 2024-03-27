from pydantic import BaseModel, validator
import re


class TagModel(BaseModel):
    name: str

    @validator('name')
    def validate_tag_name(cls, v):
        pattern = r'^#[^\s]+$'
        if not re.match(pattern, v):
            raise ValueError('tag must start with a # and contain no spaces')
        return v


class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True


class PhotoModel(BaseModel):
    title: str
    description: Optional[str] = None
    tags: Optional[List[TagModel]] = []


class PhotoResponse(PhotoModel):
    id: int

    class Config:
        from_attributes = True

