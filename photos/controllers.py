
from datetime import datetime
import aiofiles
import os
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from photos.models import Photo, Tag
from photos.schemas import PhotoModel, PhotoResponse, TagResponse
import logging
import qrcode
import cloudinary.uploader
from pathlib import Path
from app.settings import settings
from io import BytesIO


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class PhotosController:

    def __init__(self, db):
        self.db = db
        cloudinary.config(
            cloud_name=settings.cloudinary.CLOUD_NAME,
            api_key=settings.cloudinary.CLOUD_API_KEY,
            api_secret=settings.cloudinary.CLOUD_API_SECRET
        )

    async def delete_photo(self, photo_id: int, user_id: int):
        logging.info(f"Attempting to delete photo with ID {photo_id} for user {user_id}")
        photo = self.db.query(Photo).filter(Photo.id == photo_id, Photo.user_id == user_id).first()

        if not photo:
            logging.error(f"Photo with ID {photo_id} not found or doesn't belong to user {user_id}")
            raise HTTPException(status_code=404, detail="Photo not found or doesn't belong to the user")

        parts = photo.name.split('/')
        public_id = parts[-2] + '/' + parts[-1].split('.')[0]
        try:
            response = cloudinary.uploader.destroy(public_id)
            print(response)
        except Exception as e:
            print(f"Error deleting file from Cloudinary: {e}")

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

    async def upload_photo(self, photo: PhotoModel, file: UploadFile):
        logging.info("Starting photo upload process")

        file_contents = await file.read()

        try:
            logging.info("Uploading photo to Cloudinary")
            result = cloudinary.uploader.upload(file_contents, folder=photo.user_id, resource_type='auto')
            uploaded_image_url = result.get('url')
            logging.info(f"Photo uploaded successfully to Cloudinary. URL: {uploaded_image_url}")
        except Exception as e:
            logging.exception("Error uploading photo to Cloudinary", exc_info=e)
            raise HTTPException(status_code=500, detail=str(e))

        try:
            new_photo = Photo(
                name=uploaded_image_url,
                title=photo.title,
                description=photo.description,
                user_id=photo.user_id,
            )

            self.db.add(new_photo)
            logging.info(f"Photo added successfully to DB. URL: {uploaded_image_url}")

            if photo.tags:
                for tag_data in photo.tags:
                    if tag_data.name:
                        tag = self.db.query(Tag).filter_by(name=tag_data.name).first()
                        if not tag:
                            tag = Tag(name=tag_data.name)
                            self.db.add(tag)
                            self.db.flush()
                        new_photo.tags.append(tag)

            self.db.commit()
            logging.info("Photo and tags saved to database successfully")

            response = PhotoResponse(
                id=new_photo.id,
                name=new_photo.name,
                title=new_photo.title,
                description=new_photo.description,
                tags=[TagResponse(id=tag.id, name=tag.name) for tag in new_photo.tags],
                user_id=new_photo.user_id
            )
            logging.info("Photo upload process completed successfully")
            return response
        except Exception as e:
            logging.exception("Error saving photo and tags to database", exc_info=e)
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save photo and tags to database")

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