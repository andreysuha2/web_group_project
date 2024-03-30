from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.db import DBConnectionDep
from typing import Annotated, List
from photos import schemas, models
from photos.controllers import PhotosController
from app.services.auth import AuthDep
from fastapi import HTTPException, status
from fastapi.responses import Response



PhotoContollerDep = Annotated[PhotosController, Depends(PhotosController)]

photos_router = APIRouter(prefix="/photos", tags=['photos'])


@photos_router.get('/', response_model=List[schemas.PhotoResponse])
async def photos_list(user: AuthDep, controller: PhotoContollerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass


@photos_router.post("/", response_model=schemas.PhotoResponse)
async def upload_photo(
        user: AuthDep,

        db: DBConnectionDep,
        title: str = Form(),
        description: str = Form(None),
        tags: List[str] = Form(None),
        file: UploadFile = File(),
):
    controller = PhotosController(db)
    # Перетворення тегів у список об'єктів TagModel
    tag_models = [schemas.TagModel(name=tag) for tag in tags] if tags else []

    # Створення об'єкта PhotoModel для передачі в контролер
    photo_model = schemas.PhotoModel(
        name=file.filename,
        title=title,
        description=description,
        tags=tag_models,
        user_id=user.id
    )

    # Виклик методу контролера для створення фотографії
    photo_response = await controller.create_photo(photo_data=photo_model, file=file)

    # Повернення відповіді
    return photo_response


@photos_router.delete('/{photo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo(user: AuthDep,
                       db: DBConnectionDep,
                       photo_id: int
                       ):
    controller = PhotosController(db)
    result = await controller.delete_photo(photo_id=photo_id, user_id=user.id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found or not owned by user")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@photos_router.put("/{photo_id}", status_code=200)
async def update_photo_description(
                        photo_id: int,
                        user: AuthDep,
                        db: DBConnectionDep,
                        photo_update: str = Form(),
                        ):
    controller = PhotosController(db)
    updated_photo = await controller.update_photo_description(photo_id=photo_id, user_id=user.id, new_description=photo_update)
    if not updated_photo:
        raise HTTPException(status_code=404, detail="Photo not found or not allowed to edit")
    return updated_photo


@photos_router.get("/{photo_id}")
async def get_photo(
        photo_id: int,
        db: DBConnectionDep):
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found")

    try:
        file_path = photo.storage_path
        return file_path
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading photo: {e}")


@photos_router.post("/upload/")
async def upload_image(photo_id: int,
                       crop_width: int,
                        crop_height: int,

                        user: AuthDep,
                        db: DBConnectionDep,
                        ):

    controller = PhotosController(db)

    photo_response = await controller.crop_photo(photo_id, crop_height, crop_width, user.id)

    # Повернення відповіді
    return photo_response
