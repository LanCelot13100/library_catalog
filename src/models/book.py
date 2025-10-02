from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import re  # для регулярных выражений при валидации
from datetime import datetime


class BookStatus(str, Enum):
    """Возможные статусы книги в системе"""
    AVAILABLE = "available"
    BORROWED = "borrowed"
    RESERVED = "reserved"
    MAINTENANCE = "maintenance"


def _validate_isbn(isbn: Optional[str]) -> Optional[str]:
    """Валидация ISBN - общая функция"""
    if isbn is None:
        return isbn
    cleaned = re.sub(r'[^\dX]', '', isbn.upper())
    if len(cleaned) not in [10, 13]:
        raise ValueError('ISBN должен содержать 10 или 13 цифр')
    return cleaned


class Book(BaseModel):
    """Модель книги для API ответов"""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=200)
    year_of_releasing: int = Field(..., ge=1000, le=2030)
    genre: str = Field(..., min_length=1, max_length=100)
    amount_of_pages: int = Field(..., gt=0, le=10000)
    status: BookStatus
    isbn: Optional[str] = Field(None, min_length=10, max_length=17)
    cover_url: Optional[str] = None
    description: Optional[str] = Field(None, max_length=2000)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BookCreate(BaseModel):
    """Модель для создания новой книги"""
    title: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=200)
    year_of_releasing: int = Field(..., ge=1000, le=2030)
    genre: str = Field(..., min_length=1, max_length=100)
    amount_of_pages: int = Field(..., gt=0, le=10000)
    status: BookStatus = BookStatus.AVAILABLE
    isbn: Optional[str] = Field(None, min_length=10, max_length=17)
    description: Optional[str] = Field(None, max_length=2000)


class BookUpdate(BaseModel):
    """Модель для обновления книги (все поля опциональны)"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    year_of_releasing: Optional[int] = Field(None, ge=1000, le=2030)
    genre: Optional[str] = Field(None, min_length=1, max_length=100)
    amount_of_pages: Optional[int] = Field(None, gt=0, le=10000)
    status: Optional[BookStatus] = None
    isbn: Optional[str] = Field(None, min_length=10, max_length=17)
    description: Optional[str] = Field(None, max_length=2000)


class BookFilters(BaseModel):
    """Модель для фильтрации книг в API"""
    title: Optional[str] = Field(None, max_length=200, min_length=1)
    author: Optional[str] = Field(None, max_length=100, min_length=1)
    status: Optional[BookStatus] = None  # фильтр по статусу книги
    genre: Optional[str] = Field(None, max_length=100, min_length=1)
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class PaginatedBooks(BaseModel):
    """Модель для пагинированного списка книг"""
    items: List[Book]
    total: int = Field(..., ge=0)
    offset: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=100)
    has_next: bool

    @classmethod
    def create(cls, items: List[Book], total: int, offset: int,
               limit: int) -> 'PaginatedBooks':
        """Удобный конструктор для создания пагинированного ответа"""
        return cls(
            items=items,
            total=total,
            offset=offset,
            limit=limit,
            has_next=offset + limit < total  # вычисляем есть ли следующая страница
        )


__all__ = [  # экспортируемые классы
    "Book",
    "BookCreate",
    "BookUpdate",
    "BookFilters",
    "PaginatedBooks",
    "BookStatus"
]