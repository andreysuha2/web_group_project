from pydantic import BaseModel, field_validator, Field
from typing import List, Optional
import re


class TagModel(BaseModel):
    name: str

    @field_validator('name')
    def validate_tag_name(cls, value: str) -> str:
        if value:
            pattern = r'^#[^\s]+$'
            if not re.match(pattern, value):
                raise ValueError('Tag must start with a # and contain no spaces')
            return value


class TagResponse(TagModel):
    id: int


class PhotoModel(BaseModel):
    name: str
    title: str
    description: Optional[str] = None
    tags: List[TagModel] = []
    user_id: int = Field(..., description="ID of the user who is uploading the photo")


class PhotoResponse(BaseModel):
    id: int
    name: str
    title: str
    description: Optional[str]
    tags: List[TagResponse]
    user_id: int

