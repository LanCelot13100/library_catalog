import os
from typing import Optional
from src.storage.memory import InMemoryStorageClient
from src.storage.file_storage import FileStorageClient
from src.storage.jsonbin import JsonBinStorageClient
from src.storage.base import StorageClient
from src.storage.sqlalchemy_storage import SQLAlchemyStorageClient
from src.core.logger import get_logger
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

class StorageFactory:
    """Фабрика для создания экземпляров хранилищ данных"""

    def __init__(self, storage_type: Optional[str] = None):
        self.storage_type = storage_type or os.getenv("STORAGE_TYPE", "postgres")
        logger.info(f"StorageFactory initialized with type: {self.storage_type}")

    def create_storage(self, session: Optional[AsyncSession] = None) -> StorageClient:
        """Создает экземпляр хранилища данных"""
        logger.info(f"Creating storage client of type: {self.storage_type}")

        if self.storage_type == "postgres":
            if session is None:
                raise ValueError("AsyncSession is required for postgres storage type")
            return SQLAlchemyStorageClient(session)

        elif self.storage_type == "memory":
            return InMemoryStorageClient()

        elif self.storage_type == "file":
            file_path = os.getenv("STORAGE_FILE", "data.json")
            return FileStorageClient(path=file_path)

        elif self.storage_type == "jsonbin":
            base_url = os.getenv("JSONBIN_URL")
            api_key = os.getenv("JSONBIN_KEY")

            if not base_url:
                raise ValueError("JSONBIN_URL environment variable is required for jsonbin storage")
            if not api_key:
                raise ValueError("JSONBIN_KEY environment variable is required for jsonbin storage")

            headers = {
                "X-Master-Key": api_key,
                "Content-Type": "application/json"
            }
            return JsonBinStorageClient(base_url, headers)

        else:
            raise ValueError(f"Unknown storage type: {self.storage_type}")


def create_default_storage(session: Optional[AsyncSession] = None) -> StorageClient:
    """Создает хранилище по умолчанию из переменных окружения"""
    factory = StorageFactory()
    return factory.create_storage(session)