from fastapi import Depends, HTTPException, status
from typing import Annotated
from comments.controllers import CommentsController
from photos.models import Photo
from comments.models import Comment
from app.services.auth import AuthDep
from app.db import DBConnectionDep

CommentsControllerDep = Annotated[CommentsController, Depends(CommentsController)]

async def photo_dependency(photo_id: int, controller: CommentsControllerDep, db: DBConnectionDep) -> Photo:
    photo = await controller.read_photo(photo_id, db)
    if photo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo not found")
    return photo

PhotoDep = Annotated[Photo, Depends(photo_dependency)]


async def comment_dependency(comment_id: int, photo: PhotoDep, controller: CommentsControllerDep, db: DBConnectionDep) -> Comment:
    comment = await controller.read(comment_id, photo, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment

CommentDep = Annotated[Comment, Depends(comment_dependency)]