import pytest
from unittest.mock import AsyncMock
from typing import List, Dict, Any
import asyncio

from src.repositories.book_repository import BookRepository
from src.services.book_service import BookService
from src.storage.base import StorageClient
from src.clients.metadata_client import MetadataClient, BookMetadata
from src.domain.metadata_service import MetadataService
from src.domain.entities import BookEntity
from src.storage.memory import InMemoryStorageClient


@pytest.fixture(scope="session")
def event_loop():
    """Создает event loop для всех асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_storage_client() -> AsyncMock:
    """Создает мок StorageClient для тестов без реальной БД"""
    mock = AsyncMock(spec=StorageClient)
    mock.get_data.return_value = [
        {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "year_of_releasing": 2020,
            "genre": "Fiction",
            "amount_of_pages": 300,
            "status": "available",
            "isbn": "1234567890",
            "cover_url": None,
            "description": None,
            "created_at": None,
            "updated_at": None
        }
    ]
    mock.save_data.return_value = None
    return mock


@pytest.fixture
def mock_metadata_client() -> AsyncMock:
    """Создает мок MetadataClient для тестов без реальных HTTP запросов"""
    mock = AsyncMock(spec=MetadataClient)
    mock.search_book.return_value = [
        BookMetadata(
            title="Test Book",
            author="Test Author",
            year_of_releasing=2020,
            genre="Fiction",
            amount_of_pages=300,
            isbn="1234567890",
            description="Test description"
        )
    ]
    return mock


@pytest.fixture
def mock_metadata_service(mock_metadata_client: AsyncMock) -> AsyncMock:
    """Создает мок MetadataService для тестов"""
    mock = AsyncMock(spec=MetadataService)
    mock.get_book_metadata.return_value = {
        "cover_url": "http://example.com/cover.jpg",
        "description": "Test description",
        "subjects": ["Fiction", "Test"]
    }
    return mock


@pytest.fixture
def in_memory_storage() -> InMemoryStorageClient:
    """Создает реальное in-memory хранилище для интеграционных тестов"""
    return InMemoryStorageClient()


@pytest.fixture
def book_repository(mock_storage_client: AsyncMock) -> BookRepository:
    """Создает BookRepository с мок-зависимостями для unit тестов"""
    return BookRepository(
        storage_client=mock_storage_client)


@pytest.fixture
def book_repository_real_storage(in_memory_storage: InMemoryStorageClient) -> BookRepository:
    """Создает BookRepository с реальным in-memory хранилищем для интеграционных тестов"""
    return BookRepository(storage_client=in_memory_storage)


@pytest.fixture
def book_service(book_repository: BookRepository, mock_metadata_service: AsyncMock) -> BookService:
    """Создает BookService для тестов бизнес-логики"""
    return BookService(
        book_repo=book_repository,
        metadata_service=mock_metadata_service
    )


@pytest.fixture
def sample_book_entity() -> BookEntity:
    """Создает тестовую BookEntity"""
    return BookEntity(
        id=1,
        title="Test Book",
        author="Test Author",
        year_of_releasing=2020,
        genre="Fiction",
        amount_of_pages=300,
        status="available",
        isbn="1234567890"
    )


@pytest.fixture
def sample_books_data() -> List[Dict[str, Any]]:
    """Создает список тестовых данных книг"""
    return [
        {
            "id": 1,
            "title": "Book One",
            "author": "Author One",
            "year_of_releasing": 2020,
            "genre": "Fiction",
            "amount_of_pages": 300,
            "status": "available",
            "isbn": "1111111111"
        },
        {
            "id": 2,
            "title": "Book Two",
            "author": "Author Two",
            "year_of_releasing": 2021,
            "genre": "Science",
            "amount_of_pages": 400,
            "status": "borrowed",
            "isbn": "2222222222"
        }
    ]