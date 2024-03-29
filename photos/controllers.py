
from datetime import datetime
from app.db import DBConnectionDep
from pathlib import Path
from datetime import datetime
import aiofiles
import os
from fastapi import UploadFile
from photos.models import Photo, Tag
from photos.schemas import PhotoModel, PhotoResponse, TagModel


class PhotosController:

    def __init__(self, db):
        self.db = db

    async def create_photo(self, photo_data: PhotoModel, file: UploadFile):
        print('до')
        file_name = await self.save_photo(file, photo_data)
        print('після')

        new_photo = Photo(
            name=photo_data.name,
            title=file_name,
            description=photo_data.description,
            user_id=photo_data.user_id,

        )
        self.db.add(new_photo)
        self.db.flush()  # Отримати id для new_photo

        # Обробка тегів
        for tag_data in photo_data.tags:
            if tag_data:
                tag = self.db.query(Tag).filter_by(name=tag_data.name).first()
                if not tag:
                    tag = Tag(name=tag_data.name)
                    self.db.add(tag)
                    self.db.flush()  # Отримати id для tag
                new_photo.tags.append(tag)

        self.db.commit()
        return PhotoResponse.from_orm(new_photo)  # Повернення відповіді

    @staticmethod
    async def save_photo(file: UploadFile, photo_data: PhotoModel) -> str:

        try:
            # Create a directory named with today's date
            date_today = datetime.now().strftime('%Y-%m-%d')
            directory = f'../app/files-storage/{photo_data.user_id}'

            if not os.path.exists(directory):
                os.makedirs(directory)

            # Save the file with the date and time included in the filename
            date_time_now = datetime.now().strftime('%H%M%S%f')
            filename = f"{date_time_now}_{file.filename}"
            file_location = f"{directory}/{filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(file.file.read())

            return filename

        except Exception as e:
            return {"error": str(e)}
