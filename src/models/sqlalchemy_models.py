from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей"""
    pass


class BookORM(Base):
    """SQLAlchemy модель для таблицы books"""
    __tablename__ = "books"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    author = Column(String(200), nullable=False, index=True)
    year_of_releasing = Column(Integer, nullable=False)
    genre = Column(String(100), nullable=False, index=True)
    amount_of_pages = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, index=True)

    # Дополнительные поля
    isbn = Column(String(17), nullable=True, unique=True, index=True)
    cover_url = Column(Text, nullable=True)
    description = Column(Text, nullable=True)

    # Метаданные записи
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Композитные индексы для оптимизации запросов
    __table_args__ = (
        Index('idx_title_author', 'title', 'author'),  # индекс для поиска по названию и автору одновременно
        Index('idx_status_genre', 'status', 'genre'),  # индекс для фильтрации по статусу и жанру
        Index('idx_year_genre', 'year_of_releasing', 'genre'),  # индекс для фильтрации по году и жанру
    )

    def __repr__(self) -> str:  # строковое представление объекта для отладки
        """Строковое представление книги для отладки"""
        return f"<BookORM(id={self.id}, title='{self.title}', author='{self.author}')>"

    def __str__(self) -> str:  # человекочитаемое строковое представление
        """Человекочитаемое представление книги"""
        return f"{self.title} by {self.author} ({self.year_of_releasing})"