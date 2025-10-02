from typing import List, Optional
from src.storage.base import StorageClient
from src.domain.repositories import BookRepositoryInterface
from src.domain.entities import BookEntity
from src.models.book import BookFilters
from src.core.logger import get_logger

logger = get_logger(__name__)


class BookRepository(BookRepositoryInterface):
    """Репозиторий для работы с книгами через абстрактное хранилище"""

    def __init__(self, storage_client: StorageClient):
        self.storage = storage_client  # клиент для работы с хранилищем данных


    async def get_all(self, filters: BookFilters) -> List[BookEntity]:
        """Получить все книги с фильтрацией и пагинацией"""
        logger.info(f"Getting books with filters: offset={filters.offset}, limit={filters.limit}")

        # Получаем данные из хранилища
        books_data: List[dict] = await self.storage.get_data()

        # Конвертируем в доменные сущности
        books = [self._dict_to_entity(book_data) for book_data in books_data]

        # Применяем фильтры
        filtered_books = self._apply_filters(books, filters)

        # Применяем пагинацию
        start = filters.offset
        end = filters.offset + filters.limit
        paginated_books = filtered_books[start:end]

        logger.info(
            f"Returning {len(paginated_books)} books out of {len(filtered_books)} filtered")
        return paginated_books


    async def get_by_id(self, book_id: int) -> Optional[BookEntity]:
        """Найти книгу по ID"""
        logger.info(f"Getting book by ID: {book_id}")

        books_data: List[dict] = await self.storage.get_data()

        # Ищем книгу с нужным ID
        for book_data in books_data:
            if book_data.get("id") == book_id:
                logger.info(f"Found book: {book_data.get('title')}")
                return self._dict_to_entity(book_data)

        logger.warning(f"Book not found: {book_id}")
        return None


    async def create(self, book: BookEntity) -> BookEntity:
        """Создать новую книгу"""
        logger.info(f"Creating book: {book.title}")

        books_data: List[dict] = await self.storage.get_data()

        # Генерируем новый ID
        book.id = self._generate_next_id(books_data)

        # Конвертируем в dict и сохраняем
        book_data = self._entity_to_dict(book)
        books_data.append(book_data)
        await self.storage.save_data(books_data)

        logger.info(f"Book created with ID: {book.id}")
        return book


    async def update(self, book_id: int, book: BookEntity) -> Optional[BookEntity]:
        """Обновить данные книги"""
        logger.info(f"Updating book: {book_id}")

        books_data: List[dict] = await self.storage.get_data()

        # Ищем и обновляем книгу
        for i, book_data in enumerate(books_data):
            if book_data.get("id") == book_id:
                book.id = book_id
                books_data[i] = self._entity_to_dict(book)
                await self.storage.save_data(books_data)
                logger.info(f"Book updated: {book_id}")
                return book

        logger.warning(f"Book not found for update: {book_id}")
        return None


    async def delete(self, book_id: int) -> bool:
        """Удалить книгу"""
        logger.info(f"Deleting book: {book_id}")

        books_data: List[dict] = await self.storage.get_data()
        initial_count = len(books_data)

        # Фильтруем книги (убираем с нужным ID)
        books_data = [book for book in books_data if book.get("id") != book_id]

        if len(books_data) < initial_count:
            await self.storage.save_data(books_data)
            logger.info(f"Book deleted: {book_id}")
            return True

        logger.warning(f"Book not found for deletion: {book_id}")
        return False


    async def count_total(self, filters: BookFilters) -> int:
        """Подсчитать общее количество книг с учетом фильтров"""
        books_data = await self.storage.get_data()
        books = [self._dict_to_entity(book_data) for book_data in books_data]
        filtered_books = self._apply_filters(books, filters)
        return len(filtered_books)


    def _dict_to_entity(self, book_data: dict) -> BookEntity:  # конвертация словаря в доменную сущность
        """Конвертирует словарь в доменную сущность BookEntity"""
        return BookEntity(
            id=book_data.get("id"),
            title=book_data.get("title", ""),
            author=book_data.get("author", ""),
            year_of_releasing=book_data.get("year_of_releasing", 0),
            genre=book_data.get("genre", ""),
            amount_of_pages=book_data.get("amount_of_pages", 0),
            status=book_data.get("status", "available"),
            isbn=book_data.get("isbn"),
            cover_url=book_data.get("cover_url"),
            description=book_data.get("description"),
            subjects=book_data.get("subjects", []),
            created_at=book_data.get("created_at"),
            updated_at=book_data.get("updated_at")
        )


    def _entity_to_dict(self, book: BookEntity) -> dict:  # конвертация доменной сущности в словарь
        """Конвертирует доменную сущность в словарь для хранилища"""
        return {
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
            "subjects": book.subjects,
            "created_at": book.created_at,
            "updated_at": book.updated_at
        }


    def _apply_filters(self, books: List[BookEntity], filters: BookFilters) -> List[BookEntity]:
        """Применяет фильтры к списку книг"""
        filtered_books = books  # начинаем с полного списка

        if filters.title:  # если указан фильтр по названию
            filtered_books = [book for book in filtered_books if
                              filters.title.lower() in book.title.lower()]

        if filters.author:  # если указан фильтр по автору
            filtered_books = [book for book in filtered_books if
                              filters.author.lower() in book.author.lower()]

        if filters.status:  # если указан фильтр по статусу
            filtered_books = [book for book in filtered_books if
                              book.status == filters.status.value]

        if filters.genre:  # если указан фильтр по жанру
            filtered_books = [book for book in filtered_books if
                              filters.genre.lower() in book.genre.lower()]

        return filtered_books  # возвращаем отфильтрованный список


    def _generate_next_id(self, books_data: List[dict]) -> int:
        """Генерирует следующий доступный ID"""
        if not books_data:
            return 1
        max_id = max(book.get("id", 0) for book in books_data)
        return max_id + 1


