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
import cloudinary
import cloudinary.uploader


security = HTTPBearer()

UsersControllerDep = Annotated[UsersController, Depends(UsersController)]
SessionControllerDep = Annotated[SessionController, Depends(SessionController)]

session_router = APIRouter(prefix="/session", tags=['session'])
user_router = APIRouter(prefix="/users", tags=['users'])

@user_router.get("/all", response_model=List[schemas.UserModel]|None, status_code=status.HTTP_200_OK)
async def users_list(controller: UsersControllerDep, db: DBConnectionDep, offset: int = 0, limit: int = 100):
    return controller.get_users(db, offset, limit)



# @session_router.post('/login', response_model=schemas.UserResponse|None)
# async def session_create(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends()):
#     return await auth.authenticate(body, db)


# @session_router.get('/refresh_token', response_model=schemas.UserResponse|None)
# async def session_read(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends(), credentials: HTTPAuthorizationCredentials = Security(security)):
#     return auth(db, body)


# @session_router.put('/', response_model=schemas.UserResponse)
# async def session_update(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
#     return await auth.refresh(db, credentials)


# @session_router.delete('/')
# async def session_delete(credentials: HTTPAuthorizationCredentials = Security(security) ):
#     return await auth.logout()


@session_router.post('/signup', response_model=schemas.UserResponse|None)
async def singup(controller: SessionControllerDep, db: DBConnectionDep, bg_tasks: BackgroundTasks, request: Request, body: schemas.UserCreationModel):
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    # bg_tasks.add_task(ConfirmationEmail(email=user.email), username=user.username, host=request.base_url)
    return user


@session_router.post('/login', response_model=schemas.TokenPairModel)
async def login(controller: SessionControllerDep, db: DBConnectionDep, body:OAuth2PasswordRequestForm=Depends()):
    result =  await auth.authenticate(body, db)
    return result
    


# @session_router.post('/login', response_model=schemas.TokenModel)
# async def login(controller: SessionControllerDep, db: DBConnectionDep, body:OAuth2PasswordRequestForm=Depends()):
#     user = await controller.get_user(email=body.email, db=db)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
#     if not auth_service.verify_password(body.password, user.password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
#     # Generate JWT
#     access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "Сергій Багмет"})
#     refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
#     await repositories_users.update_token(user, refresh_token, db)
#     return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@session_router.get('/confirmed_email/{token}')
async def confirm_email(token: str, db: DBConnectionDep, controller: UsersControllerDep):
    email = await auth.token.decode_email_confirm(token)
    user = await controller.get_user(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verefication error")
    if user.confirmed_at:
        return {"message": "Your email is already confirmed"}
    await controller.comfirm_email(email, db)
    return { "message": "Email confirmed!" }

@session_router.post('/request_email')
async def request_email(body: schemas.RequestEmail, bg_tasks: BackgroundTasks, request: Request, db: DBConnectionDep, controller: UsersControllerDep):
    user = await controller.get_user(body.email, db)
    if user.confirmed_at:
        return {"message": "Your email is already confirmed"}
    if user:
        pass
        # bg_tasks.add_task(ConfirmationEmail(body.email), username=user.username, host=request.base_url)
    return {"message": "Check your email for confirmation"}

@session_router.get('/refresh_token', response_model=schemas.TokenPairModel)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)

@user_router.get("/", response_model=schemas.UserResponse)
async def read_user(user: AuthDep):
    return user
    

@user_router.patch("/role", response_model=schemas.UserResponse)
async def update_user_avatar(db: DBConnectionDep, controller: UsersControllerDep, current_user: AuthDep, file: UploadFile = File()):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_KEY,
        api_secret=settings.CLOUDINARY_SECRET,
        security=True
    )
    public_id = f"ContactsApp/{current_user.username}"
    r = cloudinary.uploader.upload(file.file, public_id=public_id)
    src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await controller.update_avatar(current_user, src_url, db)
    return user


# @user_router.get('/{username}')
# async def request_email(username: str, response: Response, db: DBConnectionDep):
#     print('--------------------------------')
#     print(f'{username} зберігаємо що він відкрив email в БД')
#     print('--------------------------------')
#     return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")



