from fastapi import APIRouter, Depends
from app.db import DBConnectionDep
from typing import Annotated, List
from comments import schemas
from comments.controllers import CommentsController
from app.services.auth import auth, AuthDep

CommentsControllerDep = Annotated[CommentsController, Depends(CommentsController)]

comments_router = APIRouter(prefix="/photos/{photo_id}/comments", tags=['comments'])

@comments_router.get('/', response_model=List[schemas.CommentResponse])
async def comments_list(controller: CommentsControllerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass
