from sqlalchemy.orm import Session
from app.db import get_db
from app.services.auth import auth
from app.settings import settings
from users.models import User
from libgravatar import Gravatar
from typing import List
import faker
import csv

fake_data: faker.Faker = faker.Faker()

COUNT_USERS = 20

def create_users(count: int) -> List[dict]:
    users = []       
    for _ in range(count):
        profile = fake_data.profile()
        avatar = None
        try:
            g = Gravatar(profile["mail"])
            avatar = g.get_image()
        except Exception as e:
            print("Avatar exception:", e)
        users.append({
            "username": profile["username"],
            "email": profile["mail"],
            "avatar": avatar
        })
    return users

def upload_contacts(db: Session, users: List[dict]) -> None:
    header = ['email', 'password']
    with open(f"settings.app.ROOT_DIR/users.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for user_data in users:
            password = fake_data.password()
            writer.writerow([user_data['email'], password])
            user = User(**user_data, password=auth.password.hash(password))
            db.add(user)
    db.commit()

    
def main():
    users = create_users(COUNT_USERS)
    upload_contacts(db=next(get_db()), users=users)

if __name__ == "__main__":
    main()