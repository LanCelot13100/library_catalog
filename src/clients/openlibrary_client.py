"""Конкретная реализация абстрактных методов для метаданных, чтобы их подтягивать"""
from typing import Optional, List
from src.core.base_api_client import BaseApiClient
from src.clients.metadata_client import MetadataClient, BookMetadata
from src.core.exceptions import MetadataClientError
from src.core.logger import get_logger
import re


logger = get_logger(__name__)


class OpenLibraryClient(BaseApiClient, MetadataClient):  # наследуемся от базового HTTP клиента и реализуем интерфейс метаданных
    """Клиент для работы с Open Library API"""

    def __init__(self):
        super().__init__(base_url="https://openlibrary.org")  # инициализируем базовый класс с URL Open Library

    async def search_book(self, title: str, author: Optional[str] = None, timeout: float = 10.0) -> List[BookMetadata]:
        params = {"title": title}
        if author:
            params["author"] = author

        try:
            data = await self.get('/search.json', params=params, timeout=timeout)

            books = []
            for doc in data.get("docs", [])[:3]:
                work_key = doc.get("key")
                description = ""

                if work_key:
                    try:
                        work_data = await self.get(f'{work_key}.json', timeout=timeout)
                        description = self._extract_description(work_data)
                    except Exception as e:
                        logger.warning(f"Failed to get work details for {work_key}: {e}")

                isbn = self._extract_isbn(doc)

                logger.info(f"Book: {doc.get('title')}, ISBN: {isbn}, Cover ID: {doc.get('cover_i')}")

                book = BookMetadata(
                    title=doc.get("title", "Unknown Title"),
                    author=self._extract_authors(doc),
                    year_of_releasing=doc.get("first_publish_year"),
                    genre=self._extract_subjects(doc),
                    amount_of_pages=doc.get("number_of_pages_median"),
                    isbn=self._extract_isbn(doc),
                    description=description,
                    cover_id = doc.get("cover_i")
                )
                books.append(book)

            logger.info(f"Found {len(books)} books for title='{title}', author='{author}'")
            return books

        except Exception as e:
            logger.error(f"Search failed for title='{title}', author='{author}': {e}")
            raise MetadataClientError(f"Failed to search books in Open Library: {e}")

    async def get_book_details(self, book_id: str, timeout: float = 10.0) -> BookMetadata:
        """Получение детальной информации о книге по Open Library ID"""
        if not book_id.startswith('/works/'):
            book_id = f'/works/{book_id}'

        try:
            data = await self.get(f'{book_id}.json', timeout=timeout)

            description = self._extract_description(data)

            authors = await self._fetch_authors(data.get("authors", []), timeout)

            book = BookMetadata(  # создаем объект с детальной информацией
                title=data.get("title", "Unknown Title"),
                author=", ".join(authors) if authors else "Unknown Author",
                year_of_releasing=self._extract_publish_date(data),
                genre=", ".join(data.get("subjects", [])[:5]) if data.get("subjects") else None,
                amount_of_pages=None,
                isbn=None,
                description=description
            )

            logger.info(f"Retrieved details for book ID: {book_id}")
            return book

        except Exception as e:
            logger.error(f"Failed to get details for book ID '{book_id}': {e}")
            raise MetadataClientError(
                f"Failed to get book details from Open Library: {e}")

    def _extract_authors(self, doc: dict) -> str:
        """Извлекает авторов из документа поиска Open Library"""
        authors = doc.get("author_name", [])
        if authors:
            return ", ".join(authors[:3])
        return "Unknown Author"

    def _extract_subjects(self, doc: dict) -> Optional[str]:
        """Извлекает темы/жанры из документа поиска"""
        subjects = doc.get("subject", [])
        if subjects:
            return ", ".join(subjects[:3])
        return None

    def _extract_isbn(self, doc: dict) -> Optional[str]:
        """Извлекает ISBN из документа поиска"""
        isbn_list = doc.get("isbn", [])
        if isbn_list:
            return isbn_list[0]
        return None

    def _extract_description(self, data: dict) -> str:
        """Извлекает описание из детальных данных книги"""
        description = data.get("description")
        if isinstance(description, dict):
            return description.get("value", "")
        elif isinstance(description, str):
            return description
        return ""

    def _extract_publish_date(self, data: dict) -> Optional[int]:
        """Извлекает год публикации из детальных данных"""
        publish_date = data.get("first_publish_date")
        if publish_date:
            try:
                # Пытаемся извлечь год из строки даты (может быть "1984", "June 1984", "1984-06-01")
                year_match = re.search(r'\b(19|20)\d{2}\b', str(publish_date))  # ищем 4-значный год
                if year_match:  # если год найден
                    return int(year_match.group())  # возвращаем год как число
            except (ValueError, AttributeError):
                pass
        return None  # возвращаем None если год не найден

    async def _fetch_authors(self, authors_data: List[dict], timeout: float) -> List[
        str]:  # вспомогательный метод для получения информации об авторах
        """Получает имена авторов по их ключам Open Library"""
        author_names = []

        for author_ref in authors_data[:3]:
            author_key = author_ref.get("author", {}).get("key")
            if author_key:
                try:
                    author_data = await self.get(f'{author_key}.json', timeout=timeout)
                    name = author_data.get("name", "Unknown Author")
                    author_names.append(name)
                except Exception as e:
                    logger.warning(f"Failed to fetch author data for {author_key}: {e}")
                    author_names.append("Unknown Author")
            else:
                author_names.append("Unknown Author")

        return author_names