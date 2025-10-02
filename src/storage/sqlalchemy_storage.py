from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.sqlalchemy_models import BookORM
from src.storage.base import StorageClient
from typing import List, Dict, Any
from src.core.logger import get_logger

logger = get_logger(__name__)

class SQLAlchemyStorageClient(StorageClient):
    """Хранилище данных в PostgreSQL через SQLAlchemy ORM"""

    def __init__(self, session: AsyncSession):
        if session is None:
            raise ValueError("AsyncSession is required")
        self.session = session
        logger.info("SQLAlchemyStorageClient initialized")

    async def get_data(self) -> List[Dict[str, Any]]:
        """Загружает все книги из базы данных"""
        try:
            result = await self.session.execute(select(BookORM))
            books = result.scalars().all()

            # Конвертируем ORM объекты в словари
            books_data = []
            for book in books:
                book_dict = {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "year_of_releasing": book.year_of_releasing,
                    "genre": book.genre,
                    "amount_of_pages": book.amount_of_pages,
                    "status": book.status,
                    "isbn": book.isbn,
                    "cover_url": book.cover_url,
                    "description": book.description,
                    "created_at": book.created_at,
                    "updated_at": book.updated_at
                }
                books_data.append(book_dict)

            logger.info(f"Loaded {len(books_data)} books from database")
            return books_data

        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            await self.session.rollback()
            raise

    async def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в базу данных (полная перезапись)"""
        logger.info(f"Saving {len(data)} books to database")

        try:
            await self.session.execute(delete(BookORM))

            if data:
                await self.session.execute(insert(BookORM), data)

            await self.session.commit()
            logger.info(f"Successfully saved {len(data)} books to database")

        except Exception as e:
            logger.error(f"Error saving data to database: {e}")
            await self.session.rollback()
            raise