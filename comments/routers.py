from fastapi import APIRouter, HTTPException, status, Depends
from app.db import DBConnectionDep
from typing import List
from comments import schemas
from comments.dependencies import CommentsControllerDep, PhotoDep, CommentDep
from app.services.auth import AuthDep, auth
from users.models import UserRoles
  

comments_router = APIRouter(prefix="/photos/{photo_id}/comments", tags=['comments'])

@comments_router.get('/', response_model=List[schemas.CommentResponse])
async def comments_list(photo: PhotoDep, controller: CommentsControllerDep, db: DBConnectionDep, skip: int = 0, limit: int = 100):
    return await controller.list(photo, db, skip, limit)

@comments_router.post('/', response_model=schemas.CommentResponse)
async def create_comment(photo: PhotoDep, controller: CommentsControllerDep, db: DBConnectionDep, user: AuthDep, body: schemas.CommentModel):
    return await controller.create(user, photo, body, db)

@comments_router.put('/{comment_id}', response_model=schemas.CommentResponse)
async def update_comment(comment: CommentDep, controller: CommentsControllerDep, user: AuthDep, db: DBConnectionDep, body: schemas.CommentModel):
    if comment.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return await controller.update(comment, db, body)

@comments_router.delete('/{comment_id}', response_model=schemas.CommentResponse, dependencies=[Depends(auth.role_not_in(UserRoles.USER.value))])
async def delete_comment(comment: CommentDep, controller: CommentsControllerDep, db: DBConnectionDep):
    return await controller.remove(comment, db)