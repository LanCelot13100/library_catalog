import pytest
from src.domain.entities import BookEntity
from src.models.book import BookFilters


@pytest.mark.asyncio  # помечаем асинхронный тест
async def test_get_by_id_found(book_repository, mock_storage_client):
    """Тест получения книги по ID когда книга существует"""
    # Arrange - подготовка данных
    book_id = 1
    mock_storage_client.get_data.return_value = [
        {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "year_of_releasing": 2020,
            "genre": "Fiction",
            "amount_of_pages": 300,
            "status": "available",
            "isbn": "1234567890",
            "cover_url": None,
            "description": None,
            "created_at": None,
            "updated_at": None
        }
    ]

    # Act - выполнение действия
    result = await book_repository.get_by_id(book_id)

    # Assert - проверка результатов
    assert result is not None
    assert isinstance(result, BookEntity)
    assert result.id == book_id
    assert result.title == "Test Book"
    assert result.author == "Test Author"
    mock_storage_client.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(book_repository, mock_storage_client):
    """Тест получения книги по ID когда книга не существует"""
    # Arrange
    book_id = 999
    mock_storage_client.get_data.return_value = []

    # Act
    result = await book_repository.get_by_id(book_id)

    # Assert
    assert result is None
    mock_storage_client.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_with_filters(book_repository, mock_storage_client):
    """Тест получения списка книг с фильтрацией"""
    # Arrange
    filters = BookFilters(title="Test", author=None, status=None, genre=None, offset=0, limit=10)
    mock_storage_client.get_data.return_value = [
        {
            "id": 1,
            "title": "Test Book",
            "author": "Test Author",
            "year_of_releasing": 2020,
            "genre": "Fiction",
            "amount_of_pages": 300,
            "status": "available",
            "isbn": "1234567890"
        }
    ]

    # Act
    result = await book_repository.get_all(filters)

    # Assert
    assert len(result) == 1
    assert isinstance(result[0], BookEntity)
    assert "Test" in result[0].title
    mock_storage_client.get_data.assert_called_once()


@pytest.mark.asyncio
async def test_create_book(book_repository, mock_storage_client, sample_book_entity):
    """Тест создания новой книги"""
    # Arrange
    mock_storage_client.get_data.return_value = []
    mock_storage_client.save_data.return_value = None

    # Act
    result = await book_repository.create(sample_book_entity)

    # Assert
    assert result is not None
    assert isinstance(result, BookEntity)
    assert result.id is not None
    mock_storage_client.save_data.assert_called_once()


@pytest.mark.asyncio
async def test_update_book(book_repository, mock_storage_client, sample_book_entity):
    """Тест обновления существующей книги"""
    # Arrange
    book_id = 1
    sample_book_entity.id = book_id
    sample_book_entity.title = "Updated Title"

    mock_storage_client.get_data.return_value = [
        {
            "id": 1,
            "title": "Old Title",
            "author": "Test Author",
            "year_of_releasing": 2020,
            "genre": "Fiction",
            "amount_of_pages": 300,
            "status": "available"
        }
    ]
    mock_storage_client.save_data.return_value = None

    # Act
    result = await book_repository.update(book_id, sample_book_entity)

    # Assert
    assert result is not None
    assert result.title == "Updated Title"
    mock_storage_client.save_data.assert_called_once()


@pytest.mark.asyncio
async def test_delete_book_success(book_repository, mock_storage_client):
    """Тест удаления существующей книги"""
    # Arrange
    book_id = 1
    mock_storage_client.get_data.return_value = [
        {"id": 1, "title": "Test Book", "author": "Test Author"}
    ]
    mock_storage_client.save_data.return_value = None

    # Act
    result = await book_repository.delete(book_id)

    # Assert
    assert result is True
    mock_storage_client.save_data.assert_called_once()


@pytest.mark.asyncio
async def test_delete_book_not_found(book_repository, mock_storage_client):
    """Тест удаления несуществующей книги"""
    # Arrange
    book_id = 999
    mock_storage_client.get_data.return_value = []

    # Act
    result = await book_repository.delete(book_id)

    # Assert
    assert result is False
    mock_storage_client.save_data.assert_not_called()


@pytest.mark.asyncio
async def test_count_total(book_repository, mock_storage_client):
    """Тест подсчета общего количества книг с фильтрами"""
    # Arrange
    filters = BookFilters(title=None, author=None, status=None, genre=None, offset=0, limit=10)
    mock_storage_client.get_data.return_value = [
        {"id": 1, "title": "Book 1"},
        {"id": 2, "title": "Book 2"},
        {"id": 3, "title": "Book 3"}
    ]

    # Act
    result = await book_repository.count_total(filters)

    # Assert
    assert result == 3
    mock_storage_client.get_data.assert_called_once()