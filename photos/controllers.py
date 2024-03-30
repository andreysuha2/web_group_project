
from datetime import datetime
import aiofiles
import os
from fastapi import UploadFile, HTTPException
from photos.models import Photo, Tag
from photos.schemas import PhotoModel, PhotoResponse, TagResponse
import logging
import cloudinary.uploader
import httpx
from tempfile import NamedTemporaryFile
import cloudinary
from pathlib import Path
from app.settings import settings

cloudinary.config(
    cloud_name=settings.cloudinary.CLOUD_NAME,
    api_key=settings.cloudinary.CLOUD_API_KEY,
    api_secret=settings.cloudinary.CLOUD_API_SECRET
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PhotosController:

    def __init__(self, db):
        self.db = db

    async def create_photo(self, photo_data: PhotoModel, file: UploadFile):
        print('до')
        file_name = await self.save_photo(file, photo_data)
        print('після')

        new_photo = Photo(
            name=file_name,
            title=photo_data.title,
            description=photo_data.description,
            user_id=photo_data.user_id,

        )
        self.db.add(new_photo)
        #print(new_photo.__dict__)
        #self.db.flush()  # Отримати id для new_photo

        # Обробка тегів
        if photo_data.tags:
            for tag_data in photo_data.tags:
                if tag_data.name:  # Переконатися, що ім'я тега визначено і не пусте
                    tag = self.db.query(Tag).filter_by(name=tag_data.name).first()
                    if not tag:
                        tag = Tag(name=tag_data.name)
                        self.db.add(tag)
                        self.db.flush()  # Отримати id для tag
                    new_photo.tags.append(tag)

        self.db.commit()

        return PhotoResponse(
            id=new_photo.id,
            name=new_photo.name,
            title=new_photo.title,
            description=new_photo.description,
            tags=[TagResponse(id=tag.id, name=tag.name) for tag in new_photo.tags],
            user_id=new_photo.user_id
        )

    @staticmethod
    async def save_photo(file: UploadFile, photo_data: PhotoModel) -> str:
        print(file)
        try:
            # Create a directory named with today's date
            date_today = datetime.now().strftime('%Y-%m-%d')
            directory = f'{settings.app.STORAGE_FOLDER}/{photo_data.user_id}'

            if not os.path.exists(directory):
                os.makedirs(directory)

            # Save the file with the date and time included in the filename
            date_time_now = datetime.now().strftime('%H%M%S%f')
            filename = f"{date_time_now}_{Path(file.filename).name}"
            file_location = f"{directory}/{filename}"

            async with aiofiles.open(file_location, "wb") as file_object:

                content = await file.read()
                await file_object.write(content)

            return filename

        except Exception as e:
            return {"error": str(e)}

    async def delete_photo(self, photo_id: int, user_id: int):
        logging.info(f"Attempting to delete photo with ID {photo_id} for user {user_id}")
        photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

        if not photo:
            logging.error(f"Photo with ID {photo_id} not found or doesn't belong to user {user_id}")
            raise HTTPException(status_code=404, detail="Photo not found or doesn't belong to the user")

        try:
            if os.path.exists(photo.storage_path):
                logging.info(f"Deleting file at {photo.storage_path}")
                os.remove(photo.storage_path)
        except Exception as e:
            logging.error(f"Error deleting file at {photo.storage_path}: {e}")
            # В залежності від вашої логіки обробки помилок, ви можете вирішити продовжити видалення з бази даних
            # або повернути помилку. Тут ми продовжуємо процес.

        self.db.delete(photo)
        self.db.commit()
        logging.info(f"Photo with ID {photo_id} successfully deleted from database and filesystem")
        return True

    async def update_photo_description(self, photo_id: int, user_id: int, new_description: str):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()
            if not photo:
                logging.info(f"Photo with ID {photo_id} not found for user {user_id}")
                return False

            photo.description = new_description
            self.db.commit()
            logging.info(f"Photo with ID {photo_id} description updated for user {user_id}")

            return True
        except Exception as e:
            logging.error(f"Error updating photo description for photo ID {photo_id} and user {user_id}: {e}")
            raise

    async def crop_photo(self,
                         photo_id: int,
                         crop_width: int,
                         crop_height: int,
                         user_id: int):
        logging.info(f"Starting to crop photo with ID {photo_id} for user {user_id}")

        # Знайти фото в базі даних
        photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()
        if not photo:
            logging.error(f"Photo with ID {photo_id} not found or does not belong to user {user_id}")
            raise HTTPException(status_code=404, detail="Photo not found or does not belong to the user")

        # Виклик Cloudinary для обрізки фото
        try:
            logging.info(f"Cropping photo {photo.name} with width {crop_width} and height {crop_height}")
            result = cloudinary.uploader.upload(photo.storage_path,
                                                crop="limit", width=crop_width, height=crop_height,
                                                public_id=photo.name)
            cropped_image_url = result.get('url')
            logging.info(f"Photo cropped successfully. URL: {cropped_image_url}")
        except Exception as e:
            logging.error(f"Error cropping photo {photo_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

        # Перетворення URL в UploadFile
        try:
            upload_file = await url_to_uploadfile(cropped_image_url)
            logging.info(f"Converted cropped image URL to UploadFile successfully")
        except Exception as e:
            logging.error(f"Error converting URL to UploadFile: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to convert URL to UploadFile")

        # Підготовка `photo_data` з отриманих даних
        photo_data = PhotoModel(
            name=photo.name,
            title=photo.title,
            description=photo.description,
            tags=[TagModel(name=tag.name) for tag in photo.tags],
            user_id=photo.user_id
        )

        # Створення нового фото з обрізаним зображенням
        try:
            new_photo = await self.create_photo(photo_data, upload_file)
            logging.info(f"New cropped photo created successfully for user {user_id}")
            return new_photo
        except Exception as e:
            logging.error(f"Error creating new cropped photo: {str(e)}")
            raise


# async def url_to_uploadfile(url: str) -> UploadFile:
#     async with httpx.AsyncClient() as client:
#         response = await client.get(url)
#         if response.status_code == 200:
#             # Створення тимчасового файлу
#             temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
#             async with aiofiles.open(temp_file.name, 'wb') as out_file:
#                 await out_file.write(response.content)
#
#             # Оскільки UploadFile очікує файловий об'єкт, а не шлях,
#             # вам потрібно відкрити файл асинхронно
#             file_like = await aiofiles.open(temp_file.name, 'rb')
#
#             # Створення екземпляра UploadFile
#             # УВАГА: Після цього ви не зможете використати `temp_file` в якості контекстного менеджера,
#             # оскільки воно вже буде використано та закрите
#             upload_file = UploadFile(filename=temp_file.name, file=file_like)
#             return upload_file
