from sqlalchemy.orm import Session
from app.db import get_db
from comments.models import Comment
from typing import List
from random import choice
import faker

# load models
from users.models import User
from photos.models import Photo

fake_data: faker.Faker = faker.Faker()

COMMENTS_COUNT = 1000

def create_comments(count: int) -> List[dict]:
    comments = []
    for _ in range(count):
        comments.append({ "text": fake_data.paragraph(nb_sentences=1) })
    return comments

def upload_comments(db: Session, comments_data: List[dict]) -> None:
    users = db.query(User).all()
    photos = db.query(Photo).all()
    for comment_data in comments_data:
        comment = Comment(**comment_data, user = choice(users), photo = choice(photos))
        db.add(comment)
    db.commit()
    
def main():
    coments = create_comments(COMMENTS_COUNT)
    upload_comments(db=next(get_db()), comments_data=coments)
    print("Comments seeds complete!")

if __name__ == "__main__":
    main()