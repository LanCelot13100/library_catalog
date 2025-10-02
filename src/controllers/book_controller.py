from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated

from src.dependencies import get_book_service
from src.services.book_service import BookService
from src.models.book import Book, BookCreate, BookUpdate, BookFilters, PaginatedBooks
from src.domain.exceptions import BookAlreadyExistsError, InvalidBookDataError, BookNotFoundError
from src.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)  # создание книги
async def create_book(
    book_data: BookCreate,  # данные для создания книги
    book_service: Annotated[BookService, Depends(get_book_service)],  # внедренный сервис
) -> Book:
    """Создание новой книги"""
    try:
        logger.info(f"Creating book: {book_data.title} by {book_data.author}")
        book = await book_service.create_book(book_data)
        logger.info(f"Book created successfully with ID: {book.id}")
        return book  # возвращаем созданную книгу
    except BookAlreadyExistsError as e:
        logger.warning(f"Book already exists: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))  # возвращаем 409 Conflict
    except InvalidBookDataError as e:
        logger.warning(f"Invalid book data: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))  # возвращаем 400 Bad Request


@router.get("/", response_model=PaginatedBooks)
async def get_books(
    filters: Annotated[BookFilters, Depends()],  # фильтры из query параметров
    book_service: Annotated[BookService, Depends(get_book_service)],  # внедренный сервис
) -> PaginatedBooks:
    """Получение списка книг с фильтрацией и пагинацией"""
    logger.info(f"Getting books with filters: offset={filters.offset}, limit={filters.limit}")
    result = await book_service.get_filtered_books(filters)
    logger.info(f"Returning {len(result.items)} books out of {result.total} total")
    return result  # возвращаем пагинированный список


@router.get("/{book_id}", response_model=Book)  # получение книги по ID
async def get_book_by_id(
    book_id: int,  # ID книги из path параметра
    book_service: Annotated[BookService, Depends(get_book_service)],  # внедренный сервис
) -> Book:
    """Получение книги по ID"""
    logger.info(f"Getting book by ID: {book_id}")
    book = await book_service.get_book_by_id(book_id)
    if not book:
        logger.warning(f"Book not found: {book_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")  # возвращаем 404
    logger.info(f"Book found: {book.title}")
    return book  # возвращаем найденную книгу


@router.put("/{book_id}", response_model=Book)
async def update_book(
    book_id: int,  # ID книги из path параметра
    book_data: BookUpdate,  # данные для обновления
    book_service: Annotated[BookService, Depends(get_book_service)],  # внедренный сервис
) -> Book:
    """Обновление информации о книге"""
    try:
        logger.info(f"Updating book: {book_id}")
        updated_book = await book_service.update_book(book_id, book_data)
        if not updated_book:
            logger.warning(f"Book not found for update: {book_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")  # возвращаем 404
        logger.info(f"Book updated successfully: {book_id}")
        return updated_book
    except BookNotFoundError as e:
        logger.warning(f"Book not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # возвращаем 404


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,  # ID книги из path параметра
    book_service: Annotated[BookService, Depends(get_book_service)],  # внедренный сервис
):
    """Удаление книги по ID"""
    try:
        logger.info(f"Deleting book: {book_id}")
        await book_service.delete_book(book_id)
        logger.info(f"Book deleted successfully: {book_id}")
        return None  # возвращаем пустой ответ с кодом 204
    except BookNotFoundError as e:
        logger.warning(f"Book not found for deletion: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))  # возвращаем 404
