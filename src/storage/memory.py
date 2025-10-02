from typing import List, Dict, Any
from src.storage.base import StorageClient
from src.core.logger import get_logger

logger = get_logger(__name__)

class InMemoryStorageClient(StorageClient):
    """
    Хранилище данных в оперативной памяти.
    Подходит для тестов и прототипирования.
    Данные теряются при перезапуске приложения.
    """

    def __init__(self):
        self._data: List[Dict[str, Any]] = []
        logger.info("InMemoryStorageClient initialized")

    async def get_data(self) -> List[Dict[str, Any]]:
        """Возвращает все данные из памяти"""
        logger.info(f"Loading {len(self._data)} records from memory")
        return self._data.copy()

    async def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в память (полная перезапись)"""
        self._data = data.copy()
        logger.info(f"Saved {len(self._data)} records to memory")