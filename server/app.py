import base64
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
import secrets

# FAST API
app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

# DATABASE
SQLALCHEMY_DATABASE_URL = "sqlite:///./password.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
    "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# This stores master password temporarily IN MEMORY ONLY
active_session = {}


""" Encryption with Fernet"""


def derive_key(master_password: str, salt: bytes = None):

    if salt is None:
        salt = secrets.token_bytes(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # High iterations make it harder to brute-force
    )

    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key, salt


def encrypt_with_master(data: str, master_password: str) -> str:
    """Encrypt data using master password"""
    key = derive_key(master_password)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()


def decrypt_with_master(encrypted_data: str, master_password: str) -> str:
    """Decrypt data using master password"""
    key = derive_key(master_password)
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()


""" DATABASE """


class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, index=True)
    username = Column(String)
    password = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    salt = Column(Text)  # 👈 SALT IS STORED HERE (not secret!)
    password_hash = Column(String)  # For authentication


# Create the database tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def get_vault(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request, "items": "test"})


@app.get("/vault", response_class=HTMLResponse)
async def save_password(request: Request):
    return templates.TemplateResponse("vault.html",
                                      {"request": request})


@app.get("/register_form", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html",
                                      {"request": request})


@app.post("/register")
async def register(
    master_password: str = Form(...),
):
    key, salt = derive_key(master_password)

    db = SessionLocal()
    new_user = User

    """DATABASE APIs"""


@app.post("/add")
async def add_password(
    login: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    # Save new password to database
    db = SessionLocal()

    new_password = Password(
        login=login,
        username=username,
        # TODO: encrypt the password
        password=password
    )
    db.add(new_password)
    db.commit()
    db.close()

    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{password_id}")
async def delete_password(password_id: int):

    db = SessionLocal()
    password = db.query(Password).filter(Password.id == password_id).first()
    if password:
        db.delete(password)
    db.commit()
    db.close()

    return RedirectResponse(url="/", status_code=303)


""" Generate Password from server """


@app.post("/generate_password")
async def generate_password():
    pass
