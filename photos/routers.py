from fastapi import APIRouter, Depends
from app.db import DBConnectionDep
from typing import Annotated, List
from photos import schemas
from photos.controllers import PhotosContoller
from app.services.auth import auth, AuthDep

PhotoContollerDep = Annotated[PhotosContoller, Depends(PhotosContoller)]

photos_router = APIRouter(prefix="/photos", tags=['photos'])

@photos_router.get('/', response_model=List[schemas.PhotoResponse])
async def photos_list(controller: PhotoContollerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass