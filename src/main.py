import logging
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from src.models import Book, BookCreate, BookUpdate
from src.repositories.book_repository import BookRepository
from src.clients.jsonbin_client import JsonBinClient


logger = logging.getLogger(__name__)
app = FastAPI()
jsonbin_client = JsonBinClient()
repo = BookRepository(client=jsonbin_client)


@app.get("/books", response_model=List[Book])
def get_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    logger.info(f"GET /books | filters: title={title}, author={author}, status={status}")
    books = repo.get_books()
    if title:
        books = [b for b in books if title.lower() in b["title"].lower()]
    if author:
        books = [b for b in books if author.lower() in b["author"].lower()]
    if status:
        books = [b for b in books if b["status"] == status]
    return books


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    logger.info(f"GET /books/{book_id}")
    book = repo.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@app.post("/books", response_model=Book)
def create_book(book: BookCreate):
    logger.info(f"POST /books | {book.title} by {book.author}")
    return repo.add_book(book.model_dump())


@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate):
    logger.info(f"PUT /books/{book_id}")
    updated = repo.update_book(book_id, book_update.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    logger.info(f"DELETE /books/{book_id}")
    deleted = repo.delete_book(book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
    return deleted
