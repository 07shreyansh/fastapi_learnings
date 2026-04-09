from database import engine, Base
from model import Book

Base.metadata.create_all(bind=engine)