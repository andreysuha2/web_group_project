from app.db import Session
from comments.models import Comment
from users.models import User
from photos.models import Photo
from comments import schemas
from typing import List

class CommentsController:
    async def read_photo(self, photo_id: int, db: Session) -> Photo | None:
        return db.query(Photo).filter(Photo.id == photo_id).first()
    
    async def list(self, photo: Photo, db: Session, skip: int = 0, limit: int = 100) -> List[Comment]:
        return db.query(Comment).filter(Comment.photo == photo).offset(skip).limit(limit).all()

    async def create(self, user: User, photo: Photo, body: schemas.CommentModel, db: Session) -> Comment:
        comment = Comment(**body.model_dump(), user=user, photo=photo)
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    
    async def read(self, comment_id: int, photo: Photo, db: Session) -> Comment | None:
        return db.query(Comment).filter(Comment.id == comment_id, Comment.photo == photo).first()

    async def update(self, comment: Comment, db: Session, body: schemas.CommentModel) -> Comment:
        for key, value in body.model_dump().items():
            setattr(comment, key, value)
        db.commit()
        db.refresh(comment, )
        return comment
    
    async def remove(self, comment: Comment, db: Session) -> Comment:
        db.delete(comment)
        db.commit()
        return comment