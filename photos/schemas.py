from pydantic import BaseModel, validator, Field
from typing import List, Optional
import re


class TagModel(BaseModel):
    name: str

    @validator('name')
    def validate_tag_name(cls, value: str) -> str:
        pattern = r'^#[^\s]+$'
        if not re.match(pattern, value):
            raise ValueError('Tag must start with a # and contain no spaces')
        return value


class TagResponse(BaseModel):
    id: int
    name: str


class PhotoModel(BaseModel):
    name: str
    title: str
    description: Optional[str] = None
    tags: List[TagModel] = []
    user_id: int = Field(..., description="ID of the user who is uploading the photo")

    # Якщо вам потрібно валідувати або перетворювати дані при отриманні з ORM,
    # ви можете визначити метод from_orm класу, але для базової моделі це зазвичай не потрібно


class PhotoResponse(BaseModel):
    id: int
    name: str
    title: str
    description: Optional[str]
    tags: List[TagResponse]
    user_id: int

    # Для конвертації ORM об'єкта в модель Pydantic використовуйте from_orm
    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            title=obj.title,
            description=obj.description,
            tags=[TagResponse.from_orm(tag) for tag in obj.tags],
            user_id=obj.user_id
        )



