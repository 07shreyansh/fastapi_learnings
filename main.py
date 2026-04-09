from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"Messeage": "Hellow World"}

@app.get("/people")
def people():
    return {"Messeage": "Hellow People"}

@app.get("/people/{name}")
def people_name(name: str):
    return {"Messeage": f"Hellow {name}"}

@app.get("/people/{age}")
def people_age(age: int):
    return {"Messeage": f"Hellow {age}"}

@app.get("/people/age/{name}")
def people_age_name(name: str, age: int):
    return {"Messeage": f"Hellow {name} and the age is {age}"}


@app.get("/people/age_optional/{name}")
def people_age_name(name: str, age: Optional[int]= None):
    return {"Messeage": f"Hellow {name} and optional age is {age}"}

class Student(BaseModel):
    name: str
    age: int
    roll: int

@app.post("/create_student")
def create_student(student: Student):
    return {
        "name": student.name,
        "age": student.age,
        "roll": student.roll
    }