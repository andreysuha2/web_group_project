from fastapi import HTTPException, status, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import timedelta, datetime, UTC
from typing import Optional
from enum import Enum
from app.settings import settings, TokenSettings
from app.db import get_db as db
from users.models import User, Token as TokenDBModel
from users import schemas
from dataclasses import dataclass
from typing import Callable, List, Annotated
from app.services.redis import redis_client
from functools import wraps

class TokenScopes(Enum):
    ACCESS='access_token'
    REFRESH='refresh_token'

class Password:
    def __init__(self, pwd_context: CryptContext):
        self.pwd_context = pwd_context

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify(self, password: str, hash: str) -> bool:
        return self.pwd_context.verify(password, hash)
    
@dataclass
class TokenCoder:
    encode: Callable[[dict, str, str], str]
    decode: Callable[[str, str, List[str]], dict]
    error: Exception
    
class Token:
    def __init__(self, secret: str, config: TokenSettings, coder: TokenCoder) -> None:
        self.config = config
        self.coder = coder
        self.secret = secret
         
    async def create(self, data: dict, scope: TokenScopes, expires_delta: Optional[float] = None) -> schemas.TokenModel:
        to_encode_data = data.copy()
        now = datetime.now(UTC)
        expired = now + timedelta(minutes=expires_delta) if expires_delta else now + timedelta(minutes=self.config.DEFAULT_EXPIRED)
        to_encode_data.update({"iat": now, "exp": expired, "scope": scope.value})
        token = self.coder.encode(to_encode_data, self.secret, algorithm=self.config.ALGORITHM)
        return { "token": token, "expired_at": expired, "scope": scope.value }
    
    async def decode(self, token: str, scope: TokenScopes) -> dict:
        try:
            payload = self.coder.decode(token, self.secret, algorithms=[self.config.ALGORITHM])
            if payload['scope'] == scope.value:
                return payload
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except self.coder.error as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    async def create_access(self, data: dict, expires_delta: Optional[float] = None) -> schemas.TokenModel:
        return await self.create(data=data, scope=TokenScopes.ACCESS, expires_delta=expires_delta or self.config.ACCESS_EXPIRED)
    
    async def create_refresh(self, data: dict, expires_delta: Optional[float] = None) -> schemas.TokenModel:
        return await self.create(data=data, scope=TokenScopes.REFRESH, expires_delta=expires_delta or self.config.REFRESH_EXPIRED)

    async def decode_access(self, token: str) -> dict:
        return await self.decode(token, TokenScopes.ACCESS)

    async def decode_refresh(self, token: str) -> dict:
        return await self.decode(token, TokenScopes.REFRESH)

class Auth:
    oauth2_scheme = OAuth2PasswordBearer(settings.app.LOGIN_URL)
    UserModel = User
    TokensModel = TokenDBModel
    not_found_error = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    invalid_credential_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    invalid_refresh_token_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    forbidden_access_error = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    credentionals_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    def __init__(self, password: Password, token: Token) -> None:
        self.password = password
        self.token = token

    def validate(self, user: UserModel | None, credentials: OAuth2PasswordRequestForm) -> bool:
        if user is None:
            return False
        if not self.password.verify(credentials.password, user.password):
            return False
        return True
    
    async def role_in(self, roles: List[str]):
        async def checker(token: str = Depends(self.oauth2_scheme)):
            payload = await self.token.decode_access(token)
            if payload.get('role', None) not in roles or redis_client.get(f"{settings.token.BLACK_LIST_PREFIX}{token}") == "1":
                raise self.forbidden_access_error
        return checker
    
    def role_not_in(self, roles: List[str]):
        async def checker(token: str = Depends(self.oauth2_scheme)):
            payload = await self.token.decode_access(token)
            if payload.get('role', None) in roles or redis_client.get(f"{settings.token.BLACK_LIST_PREFIX}{token}") == "1":
                raise self.forbidden_access_error
        return checker

    async def refresh(self, refresh_token_str: str, db: Session) -> schemas.TokenLoginResponse:
        payload = await self.token.decode_refresh(refresh_token_str)
        refresh_token = db.query(self.TokensModel).filter(
            self.TokensModel.token==refresh_token_str
            ).options(joinedload(self.TokensModel.user)).first()
        user = await self.__get_user(payload["email"], db)
        if refresh_token:
            db.delete(refresh_token)
            db.commit()
        if user is None or refresh_token is None or refresh_token.user != user:
            raise self.credentionals_exception
        return await self.__generate_tokens(user, db)
        
    async def authenticate(self, credentials: OAuth2PasswordRequestForm, db: Session) -> schemas.TokenLoginResponse:
        user = await self.__get_user(credentials.username, db)
        if not self.validate(user, credentials):
            raise self.invalid_credential_error
        return await self.__generate_tokens(user, db)
    
    async def logout(self, user: UserModel, token: str, db: Session) -> dict:
        payload = await self.token.decode_access(token)
        refresh_token = db.query(self.TokensModel).filter(self.TokensModel.id == payload["refresh"], self.TokensModel.user == user).first()
        redis_client.set(f"{settings.token.BLACK_LIST_PREFIX}{token}", 1, ex=timedelta(minutes=settings.token.ACCESS_EXPIRED))
        if refresh_token:
            db.delete(refresh_token)
            db.commit()
        return {"message": "Logout successful"}
    
    async def __generate_tokens(self, user: UserModel, db: Session) -> schemas.TokenLoginResponse:
        refresh_token = await self.token.create_refresh({"email": user.email})
        token = self.TokensModel(token=refresh_token["token"], expired_at=refresh_token["expired_at"])
        user.tokens.append(token)
        db.commit()
        db.refresh(token)
        access_token = await self.token.create_access({"email": user.email, "role": user.role.value, "refresh": token.id})
        return { 
            "access_token": access_token["token"], 
            "access_expired_at": access_token["expired_at"] , 
            "refresh_token": refresh_token["token"],
            "refresh_expired_at": refresh_token["expired_at"] , 
            "token_type": "bearer"
        }
        
    async def __get_user(self, username: str, db: Session) -> UserModel | None:
        return db.query(self.UserModel).filter(or_(
            self.UserModel.email == username,
            self.UserModel.username == username
            )).first()

    async def __call__(self, token: str = Depends(oauth2_scheme), db: Session = Depends(db)) -> UserModel:
        if redis_client.get(f"{settings.token.BLACK_LIST_PREFIX}{token}") == "1":
            raise self.credentionals_exception
        pyload = await self.token.decode_access(token)
        if pyload["email"] is None:
            raise self.credentionals_exception
        user = await self.__get_user(pyload["email"], db)
        if user is None:
            raise self.not_found_error
            
        return user
        

auth: Auth = Auth(
    password=Password(CryptContext(schemes=['bcrypt'], deprecated='auto')),
    token=Token(secret=settings.app.SECRET, config=settings.token, coder=TokenCoder(encode=jwt.encode, decode=jwt.decode, error=JWTError))
)

AuthDep = Annotated[auth, Depends(auth)]