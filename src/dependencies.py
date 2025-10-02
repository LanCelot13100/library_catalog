from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.repositories.book_repository import BookRepository
from src.services.book_service import BookService
from src.domain.metadata_service import MetadataService
from src.storage.factory import StorageFactory
from src.storage.base import StorageClient
from src.core.db import get_db_session
from src.clients.openlibrary_client import OpenLibraryClient
from src.core.logger import get_logger


logger = get_logger(__name__)


async def get_storage_client(session: Annotated[AsyncSession, Depends(get_db_session)]) -> StorageClient:
    """Создает клиент хранилища данных"""
    try:
        storage_factory = StorageFactory("postgres")
        storage = storage_factory.create_storage(session=session)
        logger.info("PostgreSQL storage client created")
        return storage
    except Exception as e:
        logger.error(f"PostgreSQL storage failed: {e}, falling back to memory storage")
        storage_factory = StorageFactory("memory")
        return storage_factory.create_storage()


async def get_metadata_client() -> OpenLibraryClient:
    """Создает клиент для получения метаданных книг"""
    logger.info("Creating OpenLibrary metadata client")
    return OpenLibraryClient()


async def get_metadata_service(metadata_client: Annotated[OpenLibraryClient, Depends(get_metadata_client)]) -> MetadataService:
    """Создает сервис для работы с метаданными"""
    logger.info("Creating metadata service")
    return MetadataService(metadata_client=metadata_client)


async def get_book_repository(storage_client: Annotated[StorageClient, Depends(get_storage_client)]) -> BookRepository:
    """Создает репозиторий для работы с книгами"""
    logger.info("Creating book repository")
    return BookRepository(storage_client=storage_client)


async def get_book_service(book_repo: Annotated[BookRepository, Depends(get_book_repository)], metadata_service: Annotated[MetadataService, Depends(get_metadata_service)]) -> BookService:
    """Создает сервис для бизнес-логики работы с книгами"""
    logger.info("Creating book service")
    return BookService(
        book_repo=book_repo,
        metadata_service=metadata_service
    )
