import logging
from app.settings import settings
from fastapi import APIRouter, Depends, UploadFile, File, Form
from app.db import DBConnectionDep
from typing import Annotated, List
from photos import schemas, models
from photos.controllers import PhotosController
from app.services.auth import AuthDep, auth
from users.models import UserRoles
from fastapi import HTTPException, status
from fastapi.responses import Response, StreamingResponse


PhotoContollerDep = Annotated[PhotosController, Depends(PhotosController)]

photos_router = APIRouter(prefix="/photos", tags=['photos'])
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
max_tags = settings.photo.MAX_TAGS

@photos_router.get('/', response_model=List[schemas.PhotoResponse])
async def photos_list(user: AuthDep, controller: PhotoContollerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass


@photos_router.post("/", response_model=schemas.PhotoResponse)
async def upload_photo(
        user: AuthDep,
        db: DBConnectionDep,
        title: str = Form(),
        description: str = Form(None),
        tags: str = Form(None),
        file: UploadFile = File(),
        ):
    controller = PhotosController(db)

    tag_models = []
    if tags:  # Перевіряємо, чи було передано теги
        # Розділити теги за пробілами, створити список об'єктів TagModel, і взяти перші N тегів
        tag_models = [schemas.TagModel(name=tag.strip()) for tag in tags.split(" ") if tag.strip()][:max_tags]

    # Створення об'єкта PhotoModel для передачі в контролер
    photo_model = schemas.PhotoModel(
        name=file.filename,
        title=title,
        description=description,
        tags=tag_models,
        user_id=user.id
    )
    logging.info(f'{photo_model} to the controller')
    # Виклик методу контролера для створення фотографії
    photo_response = await controller.upload_photo(photo=photo_model, file=file)
    logging.info(f"{photo_response} from controller")

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


@photos_router.get("/qr/{photo_id}", response_class=StreamingResponse)
async def get_photo_qr_code(photo_id: int, db: DBConnectionDep):
    controller = PhotosController(db=db)

    # Спочатку перевіримо, чи фото існує у базі даних
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Фотографія не знайдена")

    # Генеруємо URL для фотографії
    # Вам потрібно замінити це на фактичний шлях до вашої фотографії в додатку
    photo_url = f"{photo.name}"

    # Викликаємо метод контролера для генерації QR-коду
    return await controller.generate_qr_code(url=photo_url)


@photos_router.delete("/admin/{user_id}/{photo_id}",
                      status_code=status.HTTP_204_NO_CONTENT,
                      dependencies=[Depends(auth.role_not_in(UserRoles.USER.value))])
async def admin_delete_photo(photo_id: int,
                             user_id: int,
                             db: DBConnectionDep,
                             user: AuthDep):



    controller = PhotosController(db)
    result = await controller.delete_photo(photo_id=photo_id, user_id=user_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found or not owned by user")
    return Response(status_code=status.HTTP_204_NO_CONTENT)



@photos_router.put("/admin/{user_id}/{photo_id}", status_code=200,
                   dependencies=[Depends(auth.role_not_in(UserRoles.USER.value))])
async def admin_update_photo_description(photo_id: int,
                                         user_id: int,
                                         db: DBConnectionDep,
                                         user: AuthDep,
                                         photo_update: str = Form(),):

    controller = PhotosController(db)
    updated_photo = await controller.update_photo_description(photo_id=photo_id, user_id=user_id,
                                                              new_description=photo_update)
    if not updated_photo:
        raise HTTPException(status_code=404, detail="Photo not found or not allowed to edit")
    return updated_photo


@photos_router.post("/admin/{user_id}", response_model=schemas.PhotoResponse,
                    dependencies=[Depends(auth.role_not_in(UserRoles.USER.value))])
async def admin_upload_photo(
        user: AuthDep,
        db: DBConnectionDep,
        user_id: int,
        title: str = Form(),
        description: str = Form(None),
        tags: str = Form(None),
        file: UploadFile = File(),
        ):
    logging.info("admin_upload_photo start")
    controller = PhotosController(db)
    tag_models = []
    if tags:  # Перевіряємо, чи було передано теги
        # Розділити теги за пробілами, створити список об'єктів TagModel, і взяти перші N тегів
        tag_models = [schemas.TagModel(name=tag.strip()) for tag in tags.split(" ") if tag.strip()][:max_tags]

    # Створення об'єкта PhotoModel для передачі в контролер
    photo_model = schemas.PhotoModel(
        name=file.filename,
        title=title,
        description=description,
        tags=tag_models,
        user_id=user_id
    )
    logging.info(f'{photo_model} to the controller')
    # Виклик методу контролера для створення фотографії
    photo_response = await controller.create_photo(photo_data=photo_model, file=file)
    logging.info(f"{photo_response} from controller")

    # Повернення відповіді
    return photo_response
