from email import message
from sqlalchemy import select
from fastapi import  status
from typing import List, Optional
from users.models import User
from users.models import UserRoles
from sqlalchemy.orm import Session
from users import schemas
from datetime import datetime
from app.db import DBConnectionDep



class SessionController:
    base_model = User

    async def get_user(self, email: str, db: Session) -> base_model | None:
        return db.query(self.base_model).filter(self.base_model.email == email).first()
    
    async def comfirm_email(self, email, db: Session) -> None:
        user = await self.get_user(email, db)
        user.confirmed_at = datetime.now()
        db.commit()
    
    async def create(self, body: schemas.UserCreationModel, db: Session) -> base_model:
        user = self.base_model(**body.model_dump()) 
        # print("========================================" , user.email, user.username)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
class UsersController:
    base_model = User

    def get_users(self, db: DBConnectionDep) -> Optional[List[User]]:
        return db.query(self.base_model).all()


    def get_user_by_id(self, user_id: int, db: DBConnectionDep) -> User | None:
        return db.query(self.base_model).filter(self.base_model.id == user_id).first()


    def update_role(self, user: User, db: DBConnectionDep, new_role: str, user_id: int) -> User:
        user_to_update = db.query(self.base_model).filter(self.base_model.id == user_id).first()
        if user.role.value == "admin":
            user_to_update.role = new_role.upper()
            db.commit()
            return user_to_update
        if user.role.value == "moder" and new_role != "admin":
            user_to_update.role = new_role.upper()
            db.commit()
            return user_to_update
        else:
            print("---------------------========zsdxfcgh=======-------------   errrrrooooorrrr")
            return user_to_update
            
