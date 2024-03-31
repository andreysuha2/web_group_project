from sqlalchemy.orm import Session
from app.db import get_db
from photos.models import Tag, Photo
from typing import List
from random import choices, choice, getrandbits, randint
import string
import faker

# load models
from users.models import User
import comments.models

fake_data: faker.Faker = faker.Faker()

COUNT_PHOTOS = 200
COUNT_TAGS = 500
PHOTOS_EXTS = ['jpg', 'png', 'jpeg', 'webp']

def create_tags(count: int) -> List[dict]:
    tags = []


    def create_tag():
        words = randint(1,3)
        word = ""
        for _ in range(words):
            word = f"{word}_{fake_data.word()}"
        word = word[1:]
        if word in tags:
            return create_tag()
        return word
    for _ in range(count):
        tags.append(create_tag())
    return [ { "name": tag } for tag in tags ]

def upload_tags(db: Session, tags_data: List[dict]) -> None:
    for tag_data in tags_data:
        tag = Tag(**tag_data)
        db.add(tag)
    db.commit()

def create_photos(count: int) -> List[dict]:
    photos = []
    for _ in range(count):
        description = None
        if bool(getrandbits(1)):
            description = fake_data.paragraph(nb_sentences=1)
        photos.append({
            "name": f"{''.join(choices(string.ascii_uppercase + string.digits, k=10))}.{choice(PHOTOS_EXTS)}",
            "title": fake_data.word(),
            "description": description
        })
    return photos

def upload_photos(db: Session, photos_data: List[dict]) -> None:
    tags = db.query(Tag).all()
    users = db.query(User).all()
    for photo_data in photos_data:
        photo = Photo(**photo_data, tags = choices(tags, k=randint(1, 5)), user = choice(users))
        db.add(photo)
    db.commit()

    
def main():
    tags = create_tags(COUNT_TAGS)
    upload_tags(db=next(get_db()), tags_data=tags)
    print("Tags seeds complete!")
    photos = create_photos(COUNT_PHOTOS)
    upload_photos(db=next(get_db()), photos_data=photos)
    print("Photos seeds complete!")

if __name__ == "__main__":
    main()