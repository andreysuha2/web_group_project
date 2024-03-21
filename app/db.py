from app.settings import settings
from fastapi import Depends
from sqlalchemy import create_engine, DateTime
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, Mapped, mapped_column
from datetime import datetime, UTC
from typing import Annotated

engine = create_engine(settings.db.CONNECTION_STRING)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Dependency
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

DBConnectionDep = Annotated[Session, Depends(get_db)]

# Helpers
class TimestampsMixin():
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    update_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=lambda: datetime.now(UTC), nullable=True)