from app.db import Base, TimestampsMixin
from app.settings import settings
from sqlalchemy import Integer, String, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from users.models import User
    from comments.models import Comment

photo_tag_table = Table(
    "photo_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("photo_id", Integer, ForeignKey("photos.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"))
)

class Photo(Base, TimestampsMixin):
    __tablename__ = "photos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String(20), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="photos")
    tags: Mapped[List["Tag"]] = relationship(back_populates="photos", secondary=photo_tag_table)
    comments: Mapped[List["Comment"]] = relationship(back_populates="photo")

    @hybrid_property
    def storage_path(self):
        return f"{settings.app.STORAGE_FOLDER}/{self.user.username}/{self.name}"
    
class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    photos: Mapped[List[Photo]] = relationship(back_populates="tags", secondary=photo_tag_table)
