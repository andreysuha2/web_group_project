from fastapi import APIRouter, status, Depends, HTTPException, Security, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth import auth, AuthDep
from users import schemas
from users.models import User
from typing import Annotated, List
from app import settings
from app.db import DBConnectionDep

from users.controllers import SessionController, UsersController
# import cloudinary
# import cloudinary.uploader


security = HTTPBearer()

UsersControllerDep = Annotated[UsersController, Depends(UsersController)]
SessionControllerDep = Annotated[SessionController, Depends(SessionController)]

session_router = APIRouter(prefix="/session", tags=['session'])
user_router = APIRouter(prefix="/users", tags=['users'])

@user_router.get("/all", response_model=List[schemas.UserModel]|None, status_code=status.HTTP_200_OK)
async def users_list(controller: UsersControllerDep, db: DBConnectionDep, offset: int = 0, limit: int = 100):
    return controller.get_users(db, offset, limit)




@session_router.post('/signup', response_model=schemas.UserResponse|None)
# async def session_create(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends()):
#     return await auth.authenticate(body, db)
async def singup(controller: SessionControllerDep, db: DBConnectionDep, bg_tasks: BackgroundTasks, request: Request, body: schemas.UserCreationModel):
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    # body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    # bg_tasks.add_task(ConfirmationEmail(email=user.email), username=user.username, host=request.base_url)
    return user

@session_router.post('/login', response_model=schemas.UserResponse|None)
async def session_create(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends()):
    return await auth.authenticate(body, db)


@session_router.get('/refresh_token', response_model=schemas.UserResponse|None)
async def session_read(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends(), credentials: HTTPAuthorizationCredentials = Security(security)):
    return auth(db, body)


@session_router.put('/', response_model=schemas.UserResponse)
async def session_update(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(db, credentials)


@session_router.delete('/')
async def session_delete(credentials: HTTPAuthorizationCredentials = Security(security) ):
    return await auth.logout()








