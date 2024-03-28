from fastapi import APIRouter, status, Depends, HTTPException, Security, BackgroundTasks, Request, UploadFile, File, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth import auth, AuthDep
from fastapi.responses import FileResponse
from users import schemas
from users.models import User
from typing import Annotated, List
from app import settings
from app.db import DBConnectionDep
from users.controllers import SessionController, UsersController


security = HTTPBearer()

UsersControllerDep = Annotated[UsersController, Depends(UsersController)]
SessionControllerDep = Annotated[SessionController, Depends(SessionController)]

session_router = APIRouter(prefix="/session", tags=['session'])
user_router = APIRouter(prefix="/users", tags=['users'])

@session_router.post('/', response_model=schemas.TokenLoginResponse)
async def login(controller: SessionControllerDep, db: DBConnectionDep, body:OAuth2PasswordRequestForm=Depends()):
    result =  await auth.authenticate(body, db)
    return result


@session_router.delete('/')
async def logout(db: DBConnectionDep, user: AuthDep, token: str = Depends(auth.oauth2_scheme)):
    return await auth.logout(user, token, db)


@session_router.put('/', response_model=schemas.TokenLoginResponse)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)



@user_router.get("/all", response_model=List[schemas.UserResponse]|None, status_code=status.HTTP_200_OK)
async def users_list(controller: UsersControllerDep, db: DBConnectionDep, user: AuthDep):
    return controller.get_users(db)


@user_router.post('/', response_model=schemas.UserResponse|None)
async def singup(controller: SessionControllerDep, db: DBConnectionDep, bg_tasks: BackgroundTasks, request: Request, body: schemas.UserCreationModel):
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    return user


@user_router.get("/", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
async def read_self_user(user: AuthDep):
    return user
    

@user_router.get("/{user_id}", response_model=schemas.UserResponse|None, status_code=status.HTTP_200_OK)
async def read_user_by_id(user_id: int, db: DBConnectionDep, user: AuthDep,  controller: UsersControllerDep):
    return  controller.get_user_by_id(user_id=user_id, db=db)
    

@user_router.patch("/role", response_model=schemas.UserResponse)
async def update_role(db: DBConnectionDep, controller: UsersControllerDep, current_user: AuthDep, file: UploadFile = File()):
   pass



