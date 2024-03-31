from email import message
from fastapi import APIRouter, status, Depends, HTTPException, Security, BackgroundTasks, Request, UploadFile, File, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from app.services.auth import auth, AuthDep
from fastapi.responses import FileResponse
from users import schemas
from users.models import UserRoles, User
from typing import Annotated, List
from app.db import DBConnectionDep
from users.controllers import SessionController, UsersController, ProfileController


security = HTTPBearer()

UsersControllerDep = Annotated[UsersController, Depends(UsersController)]
SessionControllerDep = Annotated[SessionController, Depends(SessionController)]
ProfileControllerDep = Annotated[ProfileController, Depends(ProfileController)]


session_router = APIRouter(prefix="/session", tags=['session'])
user_router = APIRouter(prefix="/users", tags=['users'])
profile_router = APIRouter(prefix="/profile", tags=['profile'])

@session_router.post('/', response_model=schemas.TokenLoginResponse)
async def login(controller: SessionControllerDep, db: DBConnectionDep, body:OAuth2PasswordRequestForm=Depends()):
    if db.query(User.banned).filter(User.email == body.username).first()[0] is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='User banned')
    result =  await auth.authenticate(body, db)
    return result


@session_router.delete('/')
async def logout(db: DBConnectionDep, user: AuthDep, token: str = Depends(auth.oauth2_scheme)):
    return await auth.logout(user, token, db)


@session_router.put('/', response_model=schemas.TokenLoginResponse)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)


@user_router.post('/', response_model=schemas.UserResponse|None)
async def singup(controller: SessionControllerDep, db: DBConnectionDep, bg_tasks: BackgroundTasks, request: Request, body: schemas.UserCreationModel):
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    return user


@user_router.get("/all", response_model=List[schemas.UserResponse]|None, status_code=status.HTTP_200_OK)
async def users_list(controller: UsersControllerDep, db: DBConnectionDep, user: AuthDep):
    return controller.get_users(db)


@user_router.get("/{username_or_id}", response_model=schemas.UserSelfModel|None, status_code=status.HTTP_200_OK)
async def read_user_by_name_or_id(user_name: str|int, db: DBConnectionDep, user: AuthDep,  controller: UsersControllerDep):
    try:
        user_id = int(user_name)
        if controller.get_user_by_id(user_id=user_id, db=db) is None:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
        return controller.get_user_by_id(user_id=user_id, db=db)
    except:
        pass
    if controller.get_user_by_name(user_name=user_name, db=db) is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    return controller.get_user_by_name(user_name=user_name, db=db)


@user_router.patch("/{user_id}/role", response_model=schemas.UserResponse|None, status_code=status.HTTP_200_OK)
async def update_role(db: DBConnectionDep, controller: UsersControllerDep, current_user: AuthDep, new_role:str, user_id: int):
    if db.query(User).filter(User.id == user_id).first() is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    roles = [role.value for role in UserRoles]
    if new_role not in roles:
        raise HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, detail = "Invalid role input")
    if current_user.role.value == "user":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN)
    if current_user.role.value == "moder" and new_role == "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN)
    return controller.update_role(user=current_user, db=db, new_role=new_role, user_id = user_id)


@user_router.patch("/{user_id}/ban",  response_model=schemas.UserResponse|None, status_code=status.HTTP_200_OK)
async def user_ban(db: DBConnectionDep, controller: UsersControllerDep, current_user: AuthDep, user_id: int):
    if db.query(User).filter(User.id == user_id).first() is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    if current_user.role.value != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN)
    return controller.ban(db=db, user_id = user_id)


@user_router.patch("/{user_id}/unban", response_model=schemas.UserResponse|None, status_code=status.HTTP_200_OK)
async def user_unban(db: DBConnectionDep, controller: UsersControllerDep, current_user: AuthDep, user_id: int):
    if db.query(User).filter(User.id == user_id).first() is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "User not found")
    if current_user.role.value != "admin":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN)
    return controller.unban(db=db, user_id = user_id)


@profile_router.get("/", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
async def read_self_user(user: AuthDep):
    return user


@profile_router.put("/", response_model=schemas.UserResponse, status_code=status.HTTP_200_OK)
async def modify_self_user(db: DBConnectionDep, controller: ProfileControllerDep, current_user: AuthDep,  body: schemas.UserProfileModel):
    return controller.update_profile(user=current_user, db=db, body=body)


