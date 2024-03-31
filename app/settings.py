from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path
import os
import cloudinary

load_dotenv(override=True)

class DBSettings(BaseModel):
    ENGINE: str = os.getenv("DB_ENGINE")
    NAME: str = os.getenv("DB_NAME")
    USER: str = os.getenv("DB_USER")
    PASSWORD: str = os.getenv("DB_PASSWORD")
    HOST: str = os.getenv("DB_HOST")
    PORT: int = int(os.getenv("DB_PORT"))

    @property
    def CONNECTION_STRING(self) -> str:
        return f"{self.ENGINE}://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"
    
class TokenSettings(BaseModel):
    ALGORITHM: str = "HS256"
    DEFAULT_EXPIRED: int = 120
    ACCESS_EXPIRED: int = 15
    REFRESH_EXPIRED: int = 7 * 1440
    BLACK_LIST_PREFIX: str = "INVALID_ACCESS_TOKEN_"

class AppSettings(BaseModel):
    NAME: str = "PhotoShopper"
    VERSION: str = '0.1.0'
    HOST: str = os.getenv("APP_HOST")
    PORT: int = int(os.getenv("APP_PORT"))
    ROOT_DIR: str = Path(__file__).parent.parent
    ENV: str = os.getenv("APP_ENV")
    SECRET: str = os.getenv("APP_SECRET")
    BASE_URL_PREFIX: str = '/api'
    
    @property
    def STORAGE_FOLDER(self) -> str:
        return f"{self.ROOT_DIR}/app/files-storage"

    @property
    def LOGIN_URL(self) -> str:
        return f"{self.BASE_URL_PREFIX}/session"
    
class PhotoSettings(BaseModel):
    MAX_TAGS: int = 5

class RedisSettings(BaseModel):
    PORT: int = int(os.getenv("REDIS_PORT"))
    HOST: str = os.getenv("REDIS_HOST")
    DB: int = 0
    ENCODING: str = 'utf-8'

class CloudinarySettings(BaseModel):
    CLOUD_NAME: str = os.getenv("CLOUD_NAME")
    CLOUD_API_KEY: str = os.getenv("CLOUD_API_KEY")
    CLOUD_API_SECRET: str = os.getenv("CLOUD_API_SECRET")



class Settings(BaseModel):
    app: AppSettings = AppSettings()
    db: DBSettings = DBSettings()
    token: TokenSettings = TokenSettings()
    photo: PhotoSettings = PhotoSettings()
    redis: RedisSettings = RedisSettings()
    cloudinary: CloudinarySettings = CloudinarySettings()

settings = Settings()

