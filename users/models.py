from app.db import Base, TimestampsMixin
from enum import Enum
from sqlalchemy import Integer, String, ForeignKey, Enum as SQLEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from photos.models import Photo
    from comments.models import Comment

class UserRoles(Enum):
    ADMIN="admin"
    MODER="moder"
    USER="user"

class User(Base, TimestampsMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[UserRoles] = mapped_column(SQLEnum(name="user_role_enum"))
    tokens: Mapped[List["Token"]] = relationship(back_populates="user")
    photos: Mapped[List["Photo"]] = relationship(back_populates="user")
    comments: Mapped[List["Comment"]] = relationship(back_populates="user")

class Token(Base):
    __tablename__ = "tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[int] = mapped_column(Integer, primary_key=True)
    expired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="tokens")