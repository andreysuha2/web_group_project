
from app.db import DBConnectionDep
from fastapi import UploadFile
from .models import Photo, Tag  # Припускаючи, що моделі так називаються
from .schemas import PhotoModel  # Припускаючи, що схема створення фото так називається


class PhotosController:

    def __init__(self, db: DBConnectionDep):
        self.db = db
    @staticmethod
    def create_photo(db: DBConnectionDep, photo_data: PhotoModel, file: UploadFile):
        # Спочатку збережемо файл на диск або в облачне сховище
        # Потім створимо запис в базі даних для фото
        # В цьому прикладі ми просто припускаємо, що файл вже збережено і маємо URL
        file_url = "path/to/the/saved/file.jpg"  # Тут має бути логіка збереження файлу і отримання URL

        # Створення нового об'єкта фотографії
        new_photo = Photo(
            title=photo_data.title,
            description=photo_data.description,
            image_url=file_url,
            tags=[]
        )

        # Обробка тегів
        for tag_data in photo_data.tags:
            # Перевірка, чи існує тег в базі
            tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
            if not tag:
                # Якщо тег не знайдено, створюємо новий
                tag = Tag(name=tag_data.name)
                db.add(tag)
                db.commit()

            # Додаємо тег до фотографії
            new_photo.tags.append(tag)

        # Додаємо фотографію до сесії і зберігаємо зміни
        db.add(new_photo)
        db.commit()
        db.refresh(new_photo)

        return new_photo


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
