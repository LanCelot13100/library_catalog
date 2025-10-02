from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import BookEntity
from src.models.book import BookFilters


class BookRepositoryInterface(ABC):
    """Интерфейс репозитория книг - определяет контракт для слоя данных"""

    @abstractmethod
    async def get_all(self, filters: BookFilters) -> List[BookEntity]:
        """Получить все книги с фильтрацией и пагинацией"""
        pass

    @abstractmethod
    async def get_by_id(self, book_id: int) -> Optional[BookEntity]:
        """Найти книгу по ID"""
        pass

    @abstractmethod
    async def create(self, book: BookEntity) -> BookEntity:
        """Создать новую книгу"""
        pass

    @abstractmethod
    async def update(self, book_id: int, book: BookEntity) -> Optional[BookEntity]:
        """Обновить данные книги"""
        pass

    @abstractmethod
    async def delete(self, book_id: int) -> bool:
        """Удалить книгу"""
        pass

    @abstractmethod
    async def count_total(self, filters: BookFilters) -> int:
        """Подсчитать общее количество книг с учетом фильтров"""
        pass