from app.db import Session
from comments.models import Comment
from users.models import User
from photos.models import Photo

class CommentsController:
    async def read_photo(self, photo_id: int, db: Session) -> Photo | None:
        return db.query(Photo).filter(Photo.id == photo_id).first()

    async def create_comment(self, user: User, photo: Photo, text: str, db: Session) -> Comment:
        print(photo)
        comment = Comment(text=text, user=user, photo=photo)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
