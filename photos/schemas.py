from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
import re


class TagModel(BaseModel):
    name: str

    @field_validator('name')
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
    user_id: int = Field(..., description="ID of the user who is uploading the photo")


class PhotoResponse(PhotoModel):
    id: int

    class Config:
        from_attributes = True


