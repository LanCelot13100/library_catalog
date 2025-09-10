import json
import logging
from src.clients.jsonbin_client import JsonBinClient
from src.clients.openlibrary_client import OpenLibraryClient

logger = logging.getLogger(__name__)


class BookRepository:
    def __init__(self, client: JsonBinClient):
        self.db = JsonBinClient()
        self.ol = OpenLibraryClient()
        self.client = client

    def get_books(self):
        data = self.client.get()
        if not data:
            return []

        # если API возвращает список строк — раскодируем
        books = []
        for b in data:
            if isinstance(b, str):
                try:
                    books.append(json.loads(b))
                except json.JSONDecodeError:
                    continue
            elif isinstance(b, dict):
                books.append(b)
        return books

    def get_book(self, book_id: int):
        logger.info(f"Fetching book with ID={book_id}")
        books = self.get_books()
        return next((b for b in books if b.get("id") == book_id), None)

    def add_book(self, book_data: dict):
        logger.info(f"Adding new book: {book_data['title']} by {book_data['author']}")
        books = self.get_books()
        book_data["id"] = max([b["id"] for b in books], default=0) + 1

        # Подтягиваем данные из OpenLibrary
        extra = self.ol.search_book(book_data["title"], book_data["author"])
        if extra:
            logger.info(f"Found OpenLibrary match for '{book_data['title']}'")
            details = self.ol.get_book_details(extra["openlibrary_id"])
            book_data.update({
                "cover_url": extra.get("cover_url"),
                "description": details.get("description"),
                "subjects": details.get("subjects"),
            })
        else:
            logger.warning(f"No OpenLibrary match found for '{book_data['title']}'")

        books.append(book_data)
        self.db.put({"record": books})
        logger.info(f"Book added with ID={book_data['id']}")
        return book_data

    def update_book(self, book_id: int, book_data: dict):
        logger.info(f"Updating book with ID={book_id}")
        books = self.get_books()
        for book in books:
            if book["id"] == book_id:
                book.update(book_data)
                self.db.put({"record": books})
                logger.info(f"Book with ID={book_id} updated")
                return book
        logger.warning(f"Book with ID={book_id} not found for update")
        return None

    def delete_book(self, book_id: int):
        logger.info(f"🗑 Deleting book with ID={book_id}")
        books = self.get_books()
        updated = [b for b in books if b["id"] != book_id]
        if len(updated) == len(books):
            logger.warning(f"Book with ID={book_id} not found for deletion")
            return None
        self.db.put({"record": updated})
        logger.info(f"Book with ID={book_id} deleted")
        return {"message": "Book deleted successfully"}
