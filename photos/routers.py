from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.db import DBConnectionDep
from typing import Annotated, List
from photos import schemas
from photos.controllers import PhotosController
from app.services.auth import auth, AuthDep
from users.schemas import UserResponse

PhotoContollerDep = Annotated[PhotosController, Depends(PhotosController)]

photos_router = APIRouter(prefix="/photos", tags=['photos'])

@photos_router.get('/', response_model=List[schemas.PhotoResponse])
async def photos_list(user: AuthDep, controller: PhotoContollerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass


@photos_router.post("/", response_model=schemas.PhotoResponse)
async def upload_photo(
        title: str = Form(...),
        description: str = Form(None),
        tags: List[str] = Form(None),
        file: UploadFile = File(...),
        user: UserResponse = Depends(AuthDep),  # Використання AuthDep для отримання аутентифікованого користувача
        controller: PhotosController = Depends(),

):
    # Перетворення тегів у список об'єктів TagModel
    tag_models = [schemas.TagModel(name=tag) for tag in tags] if tags else []

    # Створення об'єкта PhotoModel для передачі в контролер
    photo_model = schemas.PhotoModel(
        title=title,
        description=description,
        tags=tag_models,
        user_id=user.id  # Встановлення user_id аутентифікованого користувача
    )

    # Виклик методу контролера для створення фотографії
    photo_response = await controller.create_photo(photo_data=photo_model, file=file)

    # Повернення відповіді
    return photo_response
