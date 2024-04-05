import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.db import Base, get_db
from users.models import User
from app.services.auth import auth

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db=TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session: Session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    def override_auth():
        user = session.query(User).filter(User.id == 1).first()
        if user is None:
            user = User(username="Thanos", email="thanos@stones.com", password=auth.password.hash("sc123123123"))
            user = User(username="Thanos", email="thanos@stones.five", password=auth.password.hash("123123123"), role="ADMIN")
            session.add(user)
            session.commit()
            session.refresh(user)
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth] = override_auth

    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def photo():
    return {
        "title": "Test Photo",
        "description": "A test photo",
        "tags": "#test #photo"
    }

@pytest.fixture(scope="module")
def user():
    return {
            "username": "username",
            "email": "user@example.com",
            "password": "string"
            }

@pytest.fixture(scope="module")
def photo_wrong_tag():
    return {
        "title": "Test Photo",
        "description": "A test photo",
        "tags": "test photo"
    }
