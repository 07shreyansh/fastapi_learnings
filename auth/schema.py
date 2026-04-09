from pydantic import BaseModel, EmailStr, Field


#schema for new user create and login user

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str | None = "user"


class UserLogin(BaseModel):
    username_or_email: str = Field(
        ...,
        min_length=3,
        strip_whitespace=True
    )
    password: str = Field(
        ...,
        min_length=8,
        strip_whitespace=True
    )