from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db , engine
from typing import List

import model

app = FastAPI()


# Pydantic schema (request body)
class BookCreate(BaseModel):
    title: str
    author: str
    publish_date: str


# API to create a book
@app.post("/books")
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = model.Book(
        title=book.title,
        author=book.author,
        publish_date=book.publish_date
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    publish_date: str

    class Config:
        from_attributes = True   


@app.get("/books", response_model=List[BookResponse])
def get_books(db: Session = Depends(get_db)):
    books = db.query(model.Book).all()
    return books