from photos.models import Photo
from photos.schemas import PhotoModel, PhotoResponse, TagResponse
import logging
from enum import Enum
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.settings import settings
from fastapi import HTTPException


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ImageAction(Enum):

    crop = "crop"
    mirror = "mirror"
    rotate = "rotate"
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

            result = cloudinary.uploader.upload(photo.name,
                                                folder=photo.user_id,
                                                type='upload',
                                                crop='crop',
                                                width=crop_width,
                                                height=crop_height)

            photo_response = await self.save_photo_to_database(result['url'], photo)

            return photo_response
        except Exception as e:
            logging.error(f"Помилка під час обрізання фото: {str(e)}")
            raise

    async def mirror_photo(self, photo_id: int, user_id: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

            if not photo:
                logging.error(f"Photo with ID {photo_id} not found for user {user_id}")
                return None  # або raise HTTPException з відповідним статус кодом

            result = cloudinary.uploader.upload(photo.name,
                                                folder=photo.user_id,
                                                type='upload',
                                                angle="hflip",
                                                )

            photo_response = await self.save_photo_to_database(result['url'], photo)

            return photo_response

        except Exception as e:
            logging.error(f"Error mirroring photo {photo_id}: {str(e)}")
            raise

    async def rotate_photo(self, photo_id: int, user_id: int, angle: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

            if not photo:
                logging.error(f"Photo with ID {photo_id} not found for user {user_id}")
                return None  # або raise HTTPException з відповідним статус кодом

            # Використовуємо Cloudinary Python SDK для обертання фото
            result = cloudinary.uploader.upload(photo.name,
                                                  folder=photo.user_id,
                                                  type='upload',
                                                  angle=angle)  # Обертання на заданий кут

            photo_response = await self.save_photo_to_database(result['url'], photo)

            return photo_response
        except Exception as e:
            logging.error(f"Error rotating photo {photo_id}: {str(e)}")
            raise

    async def scale_photo(self, photo_id: int, user_id: int, width: int, height: int):
        try:
            photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

            if not photo:
                logging.error(f"Photo with ID {photo_id} not found for user {user_id}")
                return None  # Or raise an HTTPException with an appropriate status code

            # Use Cloudinary Python SDK to scale the photo
            result = cloudinary.uploader.upload(photo.name,
                                                  folder=photo.user_id,
                                                  type='upload',
                                                  crop='scale',
                                                  width=width,
                                                  height=height)

            photo_response = await self.save_photo_to_database(result['url'], photo)

            return photo_response
        except Exception as e:
            logging.error(f"Error scaling photo {photo_id}: {str(e)}")
            raise

    async def save_photo_to_database(self, uploaded_image_url, photo: PhotoModel):
        try:
            logging.info("Create a new Photo instance")
            new_photo = Photo(
                name=uploaded_image_url,
                title=photo.title,
                user_id=photo.user_id,
            )

            logging.info(f"Add the new {photo.name} to the database")
            self.db.add(new_photo)
            self.db.commit()  # Ensure changes are committed to the database

            # Logging the successful addition
            logging.info(f"Photo added successfully to DB. URL: {uploaded_image_url}")

            # Prepare the response
            response = PhotoResponse(
                id=new_photo.id,
                name=new_photo.name,
                title=new_photo.title,
                description=new_photo.description,
                tags=[TagResponse(id=tag.id, name=tag.name) for tag in new_photo.tags],
                user_id=new_photo.user_id
            )

            # Logging the completion of the upload process
            logging.info("Photo upload process completed successfully")

            return response

        except Exception as e:
            # Log the exception details
            logging.exception("Error saving photo and tags to database", exc_info=e)

            # Rollback the transaction in case of an exception
            self.db.rollback()

            # Raising an HTTPException to inform the client about the failure
            raise HTTPException(status_code=500, detail="Failed to save photo to database")