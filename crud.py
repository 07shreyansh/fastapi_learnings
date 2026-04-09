from fastapi import FastAPI , status , HTTPException
from pydantic import BaseModel
from typing import Optional


books = [
    {
        "id": 1,
        "title": "Harry Potter and the Sorcerer's Stone",
        "author": "J.K. Rowling",
        "publish_date": "1997-06-26"
    },
    {
        "id": 2,
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "publish_date": "1954-07-29"
    },
    {
        "id": 3,
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "publish_date": "1988-01-01"
    },
    {
        "id": 4,
        "title": "Atomic Habits",
        "author": "James Clear",
        "publish_date": "2018-10-16"
    },
    {
        "id": 5,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "publish_date": "2008-08-01"
    }
]

class Book(BaseModel):
    id: int
    title: str
    author: str
    publish_date: str

app = FastAPI()

@app.get("/books")
def getbook():
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book['id'] == book_id:
            return book
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not Found"
    )


@app.post("/books")
def createbook(book : Book):
    newbook = book.model_dump()
    books.append(newbook)
    return newbook

class BookUpdate(BaseModel):
    title: str
    author: str
    publish_date: str

@app.put("/books/{book_id}")
def update_book(book_id: int , book_update: BookUpdate):
    for book in books:
        if book['id'] == book_id:
            book['title'] = book_update.title
            book['author'] = book_update.author
            book['publish_date'] = book_update.publish_date
            
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not Found"
    )

@app.delete("/books/{book_id}")
def delete_book(book_id : int):
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return {"Message": "Our book is deleted"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not Found"
    )


class BookUpdatePartial(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None

@app.patch("/books/{book_id}")
def update_book(book_id: int, book_update: BookUpdate):
    for book in books:
        if book["id"] == book_id:
            update_data = book_update.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                book[key] = value

            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not Found"
    )