# from libgravatar import Gravatar
from sqlalchemy import select

from typing import List, Optional
import users
from users.models import User
from sqlalchemy.orm import Session
from users import schemas
from datetime import datetime
from app.db import DBConnectionDep



class SessionController:
    base_model = User

    # async def get_users(self, email: str, db: Session, skip: int = 0, limit: int = 100) -> base_model | None:
    #     return db.query(self.base_model).filter(self.base_model.email == email).first()
    
    async def get_user(self, email: str, db: Session) -> base_model | None:
        return db.query(self.base_model).filter(self.base_model.email == email).first()
    
    async def comfirm_email(self, email, db: Session) -> None:
        user = await self.get_user(email, db)
        user.confirmed_at = datetime.now()
        db.commit()
    
    async def create(self, body: schemas.UserCreationModel, db: Session) -> base_model:
        avatar = None
        try:
            pass
            # g = Gravatar(body.email)
            # avatar = g.get_image()
        except Exception as e:
            print("Avatar exception:", e)
        user = self.base_model(**body.model_dump(), avatar=avatar)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
class UsersController:
    base_model = User

    async def update_avatar(self, user: base_model, url: str, db: DBConnectionDep):
        user.avatar = url
        db.commit()
        return user


    def get_users(self, db: DBConnectionDep, offset: int = 0, limit: int = 100) -> Optional[List[User]]:
        stmt = select(User).offset(offset).limit(limit)
        users = db.execute(stmt)
        return users.scalars().all()
        

