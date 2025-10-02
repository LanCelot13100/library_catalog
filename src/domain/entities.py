from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class BookEntity:
    """
    Доменная модель книги - содержит бизнес-правила и логику.
    Независима от внешних зависимостей (БД, API, фреймворков).
    """
    # Основные атрибуты книги
    title: str
    author: str
    year_of_releasing: int
    genre: str
    amount_of_pages: int
    status: str

    # Опциональные атрибуты
    id: Optional[int] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    subjects: List[str] = field(default_factory=list)

    # Аудиторские поля
    created_at: Optional[datetime] = None  # время создания записи
    updated_at: Optional[datetime] = None  # время последнего обновления

    def is_available(self) -> bool:  # бизнес-правило проверки доступности
        """Проверяет доступна ли книга для выдачи"""
        return self.status == "available"

    def is_borrowed(self) -> bool:  # бизнес-правило проверки выданности
        """Проверяет выдана ли книга читателю"""
        return self.status == "borrowed"

    def __str__(self) -> str:  # человекочитаемое представление
        """Строковое представление книги"""
        return f"'{self.title}' by {self.author} ({self.year_of_releasing}) - {self.status}"

    def __repr__(self) -> str:  # техническое представление для отладки
        """Техническое представление для отладки"""
        return f"BookEntity(id={self.id}, title='{self.title}', author='{self.author}', status='{self.status}')"