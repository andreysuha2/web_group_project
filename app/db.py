from app.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase

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