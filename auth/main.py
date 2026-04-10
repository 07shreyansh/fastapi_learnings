from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os

import models, schema, utils
from auth_database import get_db

# ─────────────────────────────
# App & Config
# ─────────────────────────────
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY or not ALGORITHM:
    raise RuntimeError("SECRET_KEY or ALGORITHM not set in environment variables")

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ─────────────────────────────
# Token Helper
# ─────────────────────────────
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


# ─────────────────────────────
# SIGNUP
# ─────────────────────────────
@app.post("/signup", status_code=status.HTTP_201_CREATED)
def register_user(
    user: schema.UserCreate,
    db: Session = Depends(get_db)
):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=utils.hash_password(user.password),
        role=user.role or "user",
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role,
        "is_active": new_user.is_active,
        "created_at": new_user.created_at,
    }


# ─────────────────────────────
# LOGIN (username OR email)
# ─────────────────────────────
@app.post("/login")
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    identifier = form_data.username

    user = (
        db.query(models.User)
        .filter(
            or_(
                models.User.username == identifier,
                models.User.email == identifier,
            )
        )
        .first()
    )

    if not user or not utils.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    token_data = {
        "sub": user.email,   # stable identity
        "user_id": user.id,
        "role": user.role,
    }

    return {
        "access_token": create_access_token(token_data),
        "token_type": "bearer",
    }


# ─────────────────────────────
# AUTH DEPENDENCIES
# ─────────────────────────────
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],  # must be LIST
        )
        email: str | None = payload.get("sub")
        role: str | None = payload.get("role")

        if email is None or role is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    return {"email": email, "role": role}


def require_roles(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permission",
            )
        return current_user

    return role_checker


# ─────────────────────────────
# ROUTES
# ─────────────────────────────
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {
        "message": f"Hello {current_user['email']}, you are a {current_user['role']}"
    }

@app.get("/user")
def user_only_route(
    current_user: dict = Depends(require_roles(["user"]))
):
    return {
        "message": f"Welcome user {current_user['email']}"
    }

@app.get("/admin")
def admin_only_route(
    current_user: dict = Depends(require_roles(["admin"]))
):
    return {
        "message": f"Welcome admin {current_user['email']}"
    }

@app.get("/profile")
def get_profile(
    current_user: dict = Depends(require_roles(["user", "admin"]))
):
    return {
        "message": f"Profile of {current_user['email']} ({current_user['role']})"
    }
