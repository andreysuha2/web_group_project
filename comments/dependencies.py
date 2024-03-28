from fastapi import Depends, HTTPException, status
from typing import Annotated
from comments.controllers import CommentsController
from photos.models import Photo
from app.db import DBConnectionDep

CommentsControllerDep = Annotated[CommentsController, Depends(CommentsController)]

async def photo_dependency(photo_id: int, controller: CommentsControllerDep, db: DBConnectionDep) -> Photo:
    photo = controller.read_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return Photo

PhotoDep = Annotated[Photo, Depends(photo_dependency)]