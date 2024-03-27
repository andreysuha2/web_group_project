
from datetime import datetime
from ..app.db import DBConnectionDep
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile
from .models import Photo, Tag
from .schemas import PhotoModel, PhotoResponse, TagModel

class PhotosController:

    def __init__(self):
        self.db = DBConnectionDep

    async def create_photo(self, photo_data: PhotoModel, file: UploadFile):

        file_url = await self.save_photo(file)

        new_photo = Photo(
            title=photo_data.title,
            description=photo_data.description,
            user_id=photo_data.user_id,
            image_url=file_url
        )
        self.db.add(new_photo)
        self.db.flush()  # Отримати id для new_photo

        # Обробка тегів
        for tag_data in photo_data.tags:
            tag = self.db.query(Tag).filter_by(name=tag_data.name).first()
            if not tag:
                tag = Tag(name=tag_data.name)
                self.db.add(tag)
                self.db.flush()  # Отримати id для tag
            new_photo.tags.append(tag)

        self.db.commit()
        return PhotoResponse.from_orm(new_photo)  # Повернення відповіді

    async def save_photo(self, file: UploadFile) -> str:
        base_path = Path("app/files-storage")
        base_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{file.filename}"
        file_path = base_path / filename

        async with file_path.open("wb") as buffer:
            while content := await file.read(1024):
                buffer.write(content)

        return str(file_path.relative_to(Path.cwd()))
