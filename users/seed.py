from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth import auth
from app.settings import settings
from users.models import User, UserRoles
from typing import List
from random import choice
import faker
import csv

# load models
import photos.models
import comments.models

fake_data: faker.Faker = faker.Faker()

COUNT_USERS = 20

def create_users(count: int) -> List[dict]:
    users = []       
    for _ in range(count):
        profile = fake_data.profile()
        users.append({
            "username": profile["username"],
            "email": profile["mail"],
            "role": choice(list(UserRoles))
        })
    return users

def upload_users(db: Session, users: List[dict]) -> None:
    header = ['email', 'password', 'role']
    with open(f"{settings.app.ROOT_DIR}/users.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for user_data in users:
            password = fake_data.password()
            writer.writerow([user_data['email'], password, user_data["role"]])
            user = User(**user_data, password=auth.password.hash(password))
            db.add(user)
    db.commit()

    
def main():
    users = create_users(COUNT_USERS)
    upload_users(db=next(get_db()), users=users)
    print("Users seeds complete!")

if __name__ == "__main__":
    main()