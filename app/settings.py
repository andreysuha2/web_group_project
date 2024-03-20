from dotenv import load_dotenv
from pydantic import BaseModel
import os

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

class AppSettings(BaseModel):
    SECRET: str = os.getenv("APP_SECRET_KEY")
    BASE_URL_PREFIX: str = '/api'

    @property
    def LOGIN_URL(self) -> str:
        return f"{self.BASE_URL_PREFIX}/session"

class Settings(BaseModel):
    app: AppSettings = AppSettings()
    db: DBSettings = DBSettings()
    token: TokenSettings = TokenSettings()

settings = Settings()

