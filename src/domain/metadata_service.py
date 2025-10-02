from typing import Dict, Optional
from src.core.exceptions import MetadataClientError
from src.clients.openlibrary_client import OpenLibraryClient
from src.clients.metadata_client import MetadataClient
from src.core.logger import get_logger

logger = get_logger(__name__)


class MetadataService:
    """Сервис для получения метаданных книг из внешних источников"""

    def __init__(self, metadata_client: MetadataClient = None):  # принимаем клиент как зависимость
        self.metadata_client = metadata_client or OpenLibraryClient()  # используем переданный клиент или создаем OpenLibrary по умолчанию

    async def get_book_metadata(self, title: str, author: str) -> Dict:
        try:
            logger.info(f"Getting metadata for '{title}' by {author}")
            books = await self.metadata_client.search_book(title=title, author=author)

            if not books:
                logger.warning(f"No books found for '{title}' by {author}")
                return self._empty_metadata()

            book = books[0]

            logger.info(f"book.isbn = {book.isbn}")
            logger.info(f"hasattr(book, 'cover_id') = {hasattr(book, 'cover_id')}")
            logger.info(f"book.cover_id = {getattr(book, 'cover_id', 'NOT FOUND')}")

            # Генерируем cover_url используя ISBN или cover_id
            cover_url = None
            if book.isbn:
                cover_url = f"https://covers.openlibrary.org/b/isbn/{book.isbn}-L.jpg"
                logger.info(f"Generated cover_url from ISBN: {cover_url}")
            elif hasattr(book, 'cover_id') and book.cover_id:  # Проверяем наличие cover_id
                cover_url = f"https://covers.openlibrary.org/b/id/{book.cover_id}-L.jpg"
                logger.info(f"Generated cover_url from cover_id: {cover_url}")

            logger.info(f"First book found: title={book.title}, author={book.author}")
            logger.info(f"ISBN: {book.isbn}")
            logger.info(f"Description: {book.description}")
            logger.info(f"Genre: {book.genre}")

            metadata = {
                "cover_url": cover_url,
                "description": (book.description or "")[:2000] if book.description else "",
                "subjects": book.genre.split(", ") if book.genre else [],
                "isbn": book.isbn
            }

            logger.info(f"📦 Final metadata: cover_url={metadata['cover_url']}, isbn={metadata['isbn']}")

            logger.info(f"Successfully retrieved metadata for '{title}' by {author}")
            return metadata

        except Exception as e:
            logger.error(f"Failed to get metadata for '{title}' by {author}: {e}")
            raise MetadataClientError(f"Failed to get metadata for '{title}' by {author}: {e}")


    def _empty_metadata(self) -> Dict:
        """Возвращает пустые метаданные"""
        return {
            "cover_url": None,  # нет обложки
            "description": "",  # нет описания
            "subjects": []  # нет тем/жанров
        }

    def _generate_cover_url(self, isbn: str) -> Optional[str]:
        """Генерирует URL обложки книги по ISBN через OpenLibrary Covers API"""
        if not isbn:  # если ISBN отсутствует
            return None  # не можем сгенерировать URL

        # OpenLibrary Covers API: https://covers.openlibrary.org/b/isbn/{isbn}-{size}.jpg
        return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"  # возвращаем URL обложки среднего размера