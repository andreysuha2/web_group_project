from app.db import Base, TimestampsMixin
from sqlalchemy import Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from users.models import User
    from photos.models import Photo

class Comment(Base, TimestampsMixin):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="comments")
    photo_id: Mapped[int] = mapped_column(Integer, ForeignKey("photos.id", ondelete='CASCADE'))
    photo: Mapped["Photo"] = relationship(back_populates="comments")
