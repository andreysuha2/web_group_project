from fastapi import APIRouter, Depends
from app.db import DBConnectionDep
from typing import List
from comments import schemas
from comments.dependencies import CommentsControllerDep, PhotoDep
from app.services.auth import AuthDep
  

comments_router = APIRouter(prefix="/photos/{photo_id}/comments", tags=['comments'])

@comments_router.get('/', response_model=List[schemas.CommentResponse])
async def comments_list(controller: CommentsControllerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass

@comments_router.post('/', response_model=schemas.CommentResponse)
async def create_comment(controller: CommentsControllerDep, db: DBConnectionDep, user: AuthDep, body: schemas.CommentModel, photo: PhotoDep):
    return await controller.create_comment(user, photo, body.text, db)