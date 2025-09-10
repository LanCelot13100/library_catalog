from pydantic import BaseModel
from typing import Optional, List


class Book(BaseModel):
    id: int
    title: str
    author: str
    year_of_releasing: int
    genre: str
    amount_of_pages: int
    status: str
    cover_url: Optional[str] = None
    description: Optional[str] = None
    subjects: Optional[List[str]] = []


class BookCreate(BaseModel):
    title: str
    author: str
    year_of_releasing: int
    genre: str
    amount_of_pages: int
    status: str


class BookUpdate(BaseModel):
    title: Optional[str]
    author: Optional[str]
    year_of_releasing: Optional[int]
    genre: Optional[str]
    amount_of_pages: Optional[int]
    status: Optional[str]
