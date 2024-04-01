from photos.models import Photo, Tag
import logging
from enum import Enum
import cloudinary.uploader
from app.settings import settings
from cloudinary import CloudinaryImage
from photos.controllers import extract_public_id_from_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ImageAction(Enum):
    crop = "crop"
    mirror = "mirror"
    rotate = "rotate"
    pad = "pad"
    scale = "scale"


class CloudinaryController:

    def __init__(self, db):
        self.db = db
        cloudinary.config(
            cloud_name=settings.cloudinary.CLOUD_NAME,
            api_key=settings.cloudinary.CLOUD_API_KEY,
            api_secret=settings.cloudinary.CLOUD_API_SECRET
        )

    async def crop_photo(self, photo_id: int, user_id: int, crop_width: int, crop_height: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()
            if not photo:
                logging.info(f"Photo with ID {photo_id} not found for user {user_id}")
                return False

            public_id = extract_public_id_from_url(photo.name)
            logging.info(f"Croping photo {public_id}")
            # Використовуємо Cloudinary Python SDK для обрізання фото

            # Тут 'upload' - це тип ресурсу, який вказує, що ми хочемо змінити вже існуюче зображення
            result = cloudinary.uploader.explicit(public_id,
                                                  type='upload',
                                                  crop='crop',
                                                  width=crop_width,
                                                  height=crop_height)

            self.db.commit()

            return result['url']
        except Exception as e:
            logging.error(f"Помилка під час обрізання фото: {str(e)}")
            raise

    async def mirror_photo(self, photo_id: int, user_id: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

            if not photo:
                logging.error(f"Photo with ID {photo_id} not found for user {user_id}")
                return None  # або raise HTTPException з відповідним статус кодом

            public_id = extract_public_id_from_url(photo.name)

            # Використовуємо Cloudinary Python SDK для відзеркалення фото
            result = cloudinary.uploader.explicit(public_id,
                                                  type='upload',
                                                  effect='h_flip')  # відзеркалення по горизонталі

            # Перед збереженням змін у базі, ми повинні зберегти нове посилання в об'єкті photo
            photo.url = result['url']
            self.db.commit()

            logging.info(f"Photo {photo_id}, {public_id} mirrored successfully for user {user_id}."
                         f"Result in {result}")
            return result['url']
        except Exception as e:
            logging.error(f"Error mirroring photo {photo_id}: {str(e)}")
            raise

    async def rotate_photo(self, photo_id: int, user_id: int, angle: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

            if not photo:
                logging.error(f"Photo with ID {photo_id} not found for user {user_id}")
                return None  # або raise HTTPException з відповідним статус кодом

            public_id = extract_public_id_from_url(photo.name)

            # Використовуємо Cloudinary Python SDK для обертання фото
            result = cloudinary.uploader.explicit(public_id,
                                                  type='upload',
                                                  angle=angle)  # Обертання на заданий кут

            # Перед збереженням змін у базі, ми повинні зберегти нове посилання в об'єкті photo
            photo.url = result['url']
            self.db.commit()

            logging.info(f"Photo {photo_id} rotated successfully for user {user_id}")
            return result['url']
        except Exception as e:
            logging.error(f"Error rotating photo {photo_id}: {str(e)}")
            raise

    async def scale_photo(self, photo_id: int, user_id: int, width: int, height: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

            if not photo:
                logging.error(f"Photo with ID {photo_id} not found for user {user_id}")
                return None  # Or raise an HTTPException with an appropriate status code

            public_id = extract_public_id_from_url(photo.name)

            # Use Cloudinary Python SDK to scale the photo
            result = cloudinary.uploader.explicit(public_id,
                                                  type='upload',
                                                  crop='scale',
                                                  width=width,
                                                  height=height)

            # Before saving changes to the database, you should update the photo object with the new URL
            photo.url = result['url']
            self.db.commit()

            logging.info(f"Photo {photo_id} scaled successfully for user {user_id}")
            return result['url']
        except Exception as e:
            logging.error(f"Error scaling photo {photo_id}: {str(e)}")
            raise
