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
PHOTOS_LIST = [ 
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1711960798/21/m9fkhh3liez1llnsimdr.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1711978586/21/hsgkvmuwpytf3paiqiy4.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712074526/21/hii4ghshznktmkw6gmrw.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712074588/21/pmvy16s0ujwbizhjiyv9.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1711960798/21/m9fkhh3liez1llnsimdr.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075184/21/qlnhsk6vkekxpmui6o39.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075282/21/vbgrny2yentrhk8gmzho.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075586/21/iveje8y9ucgnizkxbh0p.png',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075617/21/wenyr6lzoutrkwapk8wx.png',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075650/21/kvxeuv2hisl5wngisahd.png',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075666/21/arzvpmyeockmxqtjthqo.png',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712075701/21/xrn3jyxvjphvuihdxjsr.png',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712078593/21/sfrhpvdktwgvlbllvlok.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712079416/21/ifz5d3zyz3y3fmgbwhxl.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712079423/21/gs3q07xrfmdjvrat5b5w.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712079433/21/dohj0fytwccjzf5a2czw.jpg',
    'http://res.cloudinary.com/dxle4i1vi/image/upload/v1712079447/21/hbkb8ie50mwb490e0qna.jpg'
    ]

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
            "name": choice(PHOTOS_LIST),
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