from typing import Optional
from datetime import datetime, timezone
from src.domain.entities import BookEntity
from src.domain.repositories import BookRepositoryInterface
from src.domain.metadata_service import MetadataService
from src.models.book import Book, BookCreate, BookFilters, PaginatedBooks, BookUpdate
from src.models.book import BookStatus
from src.domain.exceptions import BookAlreadyExistsError, InvalidBookDataError, BookNotFoundError
from src.core.logger import get_logger

logger = get_logger(__name__)

def entity_to_model(entity: BookEntity) -> Book:
    """Конвертация доменной сущности в API модель"""
    return Book(
        id=entity.id,
        title=entity.title,
        author=entity.author,
        year_of_releasing=entity.year_of_releasing,
        genre=entity.genre,
        amount_of_pages=entity.amount_of_pages,
        status=BookStatus(entity.status),
        isbn=entity.isbn,
        cover_url=entity.cover_url,
        description=entity.description,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )


def model_to_entity(model: BookCreate) -> BookEntity:
    """Конвертация API модели в доменную сущность"""
    return BookEntity(
        title=model.title,
        author=model.author,
        year_of_releasing=model.year_of_releasing,
        genre=model.genre,
        amount_of_pages=model.amount_of_pages,
        status=model.status.value,
        isbn=model.isbn,
        description=model.description,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )


class BookService:
    """Сервис содержит всю бизнес-логику работы с книгами"""

    def __init__(self, book_repo: BookRepositoryInterface, metadata_service: Optional[MetadataService] = None):
        self.book_repo = book_repo  # репозиторий для работы с данными книг
        self.metadata_service = metadata_service  # опциональный сервис метаданных

    async def create_book(self, book_data: BookCreate) -> Book:
        """Создание новой книги с валидацией и обогащением метаданными"""
        logger.info(f"Creating book: {book_data.title} by {book_data.author}")
        logger.info(f"Metadata service available: {self.metadata_service is not None}")

        # Валидация перед созданием
        await self._validate_book_creation(book_data)

        # Конвертируем в доменную сущность
        book_entity = model_to_entity(book_data)

        # Обогащаем метаданными если доступно
        if self.metadata_service and book_data.title and book_data.author:
            logger.info("Attempting to enrich with metadata...")
            await self._enrich_with_metadata(book_entity)

        # Создаем через репозиторий
        created_entity = await self.book_repo.create(book_entity)

        logger.info(f"Book created successfully with ID: {created_entity.id}")
        return entity_to_model(created_entity)

    async def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Получение книги по ID"""
        logger.info(f"Getting book by ID: {book_id}")

        entity = await self.book_repo.get_by_id(book_id)
        if entity:
            return entity_to_model(entity)

        logger.warning(f"Book not found: {book_id}")
        return None

    async def update_book(self, book_id: int, data: BookUpdate) -> Optional[Book]:
        """Обновление книги по ID"""
        logger.info(f"Updating book: {book_id}")

        # Получаем существующую книгу
        existing_entity = await self.book_repo.get_by_id(book_id)
        if not existing_entity:
            raise BookNotFoundError(f"Book with ID {book_id} not found")

        # Обновляем поля
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(existing_entity, field):
                setattr(existing_entity, field, value)

        existing_entity.updated_at = datetime.now(timezone.utc)

        # Сохраняем изменения
        updated_entity = await self.book_repo.update(book_id, existing_entity)
        if updated_entity:
            logger.info(f"Book updated successfully: {book_id}")
            return entity_to_model(updated_entity)

        return None

    async def delete_book(self, book_id: int) -> bool:
        """Удаление книги по ID"""
        logger.info(f"Deleting book: {book_id}")

        # Проверяем существование книги
        existing_entity = await self.book_repo.get_by_id(book_id)
        if not existing_entity:
            raise BookNotFoundError(f"Book with ID {book_id} not found")

        # Удаляем книгу
        success = await self.book_repo.delete(book_id)
        if success:
            logger.info(f"Book deleted successfully: {book_id}")

        return success

    async def get_filtered_books(self, filters: BookFilters) -> PaginatedBooks:
        """Получение книг с фильтрацией и пагинацией"""
        logger.info(f"Getting filtered books: offset={filters.offset}, limit={filters.limit}")

        # Получаем книги из репозитория
        entities = await self.book_repo.get_all(filters)
        total_count = await self.book_repo.count_total(filters)

        # Конвертируем в API модели
        books = [entity_to_model(entity) for entity in entities]

        # Создаем пагинированный ответ
        return PaginatedBooks.create(
            items=books,
            total=total_count,
            offset=filters.offset,
            limit=filters.limit
        )

    async def _validate_book_creation(self, book_data: BookCreate) -> None:
        """Валидация перед созданием книги"""
        all_filters = BookFilters(
            title=book_data.title,
            author=book_data.author,
            status=None,
            genre=None,
            offset=0,
            limit=1
        )
        existing_books = await self.book_repo.get_all(all_filters)

        for book in existing_books:
            if (book.title.lower() == book_data.title.lower() and
                    book.author.lower() == book_data.author.lower()):
                raise BookAlreadyExistsError(f"Book '{book_data.title}' by {book_data.author} already exists")

        # Проверяем год издания
        current_year = datetime.now(timezone.utc).year
        if book_data.year_of_releasing > current_year:
            raise InvalidBookDataError("Publication year cannot be in the future")
        if book_data.year_of_releasing < 1400:
            raise InvalidBookDataError("Publication year is too early")

    async def _enrich_with_metadata(self, book_entity: BookEntity) -> None:
        try:
            metadata = await self.metadata_service.get_book_metadata(
                title=book_entity.title,
                author=book_entity.author
            )

            if not book_entity.cover_url and metadata.get("cover_url"):
                book_entity.cover_url = metadata["cover_url"]
                logger.info(f"Set cover_url: {book_entity.cover_url}")

            if not book_entity.description and metadata.get("description"):
                book_entity.description = metadata["description"]
                logger.info(f"Set description")

            if not book_entity.isbn and metadata.get("isbn"):
                book_entity.isbn = metadata["isbn"]
                logger.info(f"Set isbn: {book_entity.isbn}")

            if metadata.get("subjects"):
                book_entity.subjects = metadata["subjects"]

            logger.info(f"Book enriched with metadata: {book_entity.title}")

        except Exception as e:
            logger.warning(f"Failed to enrich book with metadata: {e}")