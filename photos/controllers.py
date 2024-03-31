
from datetime import datetime
import aiofiles
import os
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from photos.models import Photo, Tag
from photos.schemas import PhotoModel, PhotoResponse, TagResponse
import logging
import qrcode
import cloudinary
from pathlib import Path
from app.settings import settings
from io import BytesIO

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

    async def generate_qr_code(self, url: str) -> StreamingResponse:
        """Генерує QR-код для заданого URL."""
        try:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            img_bytes = BytesIO()
            img.save(img_bytes)
            img_bytes.seek(0)

            logging.info(f"QR-код успішно створено для URL: {url}")
            return StreamingResponse(img_bytes, media_type="image/png")
        except Exception as e:
            logging.error(f"Помилка при створенні QR-коду для URL: {url}. Помилка: {str(e)}")
            raise HTTPException(status_code=500, detail="Помилка при створенні QR-коду")

