from fastapi import APIRouter, Depends
from app.db import DBConnectionDep
from typing import Annotated, List
from users import schemas
from users.controllers import UsersController, SessionController
from app.services.auth import auth, AuthDep

UsersControllerDep = Annotated[UsersController, Depends(UsersController)]
SessionControllerDep = Annotated[SessionController, Depends(SessionController)]

session_router = APIRouter(prefix="/session", tags=['session'])
user_router = APIRouter(prefix="/users", tags=['users'])

# User routes
@user_router.get('/', response_model=List[schemas.UserResponse])
async def users_list(controller: UsersControllerDep, db: DBConnectionDep, q: str = '', skip: int = 0, limit: int = 100):
    pass

#Session routes
@session_router.get('/', response_model=List[schemas.UserResponse])
async def session_create(controller: SessionControllerDep, db: DBConnectionDep):
    pass