from abc import ABC, abstractmethod
from typing import List, Dict, Any


class StorageClient(ABC):
    """
    Абстрактный интерфейс для работы с хранилищами данных.
    Позволяет менять тип хранилища (PostgreSQL, файлы, память) без изменения кода.
    """

    @abstractmethod
    async def get_data(self) -> List[Dict[str, Any]]:
        """Получает все данные из хранилища"""
        pass

    @abstractmethod
    async def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в хранилище"""
        pass
