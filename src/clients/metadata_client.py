"""metadata_client.py представляет из себя модуль для абстракции класса, который будет подтягивать метаданные для книги """

from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class BookMetadata:  # структура данных для метаданных книги из внешних API
    """Метаданные книги из внешнего источника"""
    title: str
    author: str
    year_of_releasing: Optional[int] = None
    genre: Optional[str] = None
    amount_of_pages: Optional[int] = None
    isbn: Optional[str] = None
    description: Optional[str] = None
    cover_id: Optional[int] = None


class MetadataClient(ABC):  # абстрактный базовый класс для всех клиентов метаданных

    @abstractmethod
    async def search_book(  # поиск книг по названию и автору
            self,
            title: str,
            author: Optional[str] = None,
            timeout: float = 10.0
    ) -> List[BookMetadata]:
        pass

    @abstractmethod
    async def get_book_details(  # получение подробной информации о книге по ID
            self,
            book_id: str,
            timeout: float = 10.0
    ) -> BookMetadata:
        pass