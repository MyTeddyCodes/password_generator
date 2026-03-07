import base64
from datetime import datetime, timedelta
from functools import wraps
import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from typing import Annotated
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, LargeBinary, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import sys
import secrets

from pydantic import BaseModel


sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'src')))


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


def derive_key(master_password: str, salt: bytes):

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # High iterations make it harder to brute-force
    )

    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def encrypt_with_master(data: str, master_password: str, salt: bytes) -> str:
    """Encrypt data using master password"""
    key = derive_key(master_password, salt)
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()


def decrypt_with_master(encrypted_data: str, master_password: str, salt: bytes) -> str:
    """Decrypt data using master password"""
    key = derive_key(master_password, salt)
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()


""" DATABASE """


class Password(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    login = Column(String, index=True)
    username = Column(String)
    password = Column(String)

    owner = relationship("User", back_populates="passwords")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, default=1)
    # The CheckConstraint ensures the id can ONLY be 1
    __table_args__ = (
        CheckConstraint(id == 1, name='only_one_row'),
    )
    # email = Column(String, unique=True)
    salt = Column(LargeBinary)  # 👈 SALT IS STORED HERE (not secret!)
    password_hash = Column(String)  # For authentication

    passwords = relationship(
        "Password", back_populates="owner", cascade="all, delete-orphan")


# Create the database tables
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


def create_session(user_id: int, master_password: str) -> str:
    """Create a new session for user"""
    session_token = secrets.token_urlsafe(32)
    active_session[session_token] = {
        "user_id": user_id,
        "master_password": master_password,  # ONLY in memory!
        "created_at": datetime.now()
    }
    print(active_session)
    return session_token


def get_current_session(request: Request):
    """Get the current session if valid"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        print("No Session_Token")
        return None

    session = active_session.get(session_token)
    print(f'active session: = > {active_session}')
    if not session:
        print("No active session")
        return None
    else:
        print(f'time, {datetime.now() - session["created_at"]}')

    # Check if session expired (optional)
    if (datetime.now() - session["created_at"]) > timedelta(hours=2):
        print(f'\ntime before delete, {
              datetime.now() - session["created_at"]}')
        del active_session[session_token]

        print("Session expired")
        return None

    session["created_at"] = datetime.now()

    return session


def login_required(api_route=False):
    """Decorator to require Login"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check if user has active session
            request: Request = kwargs.get("request")
            if not request:
                raise RuntimeError(
                    "Route must include 'request: Request' to use login_required")

            session = get_current_session(request)

            if not session:
                # No active session - block access
                if api_route:
                    # API route
                    raise HTTPException(
                        status_code=401, detail="Please login first")
                else:
                    # HTML route
                    return RedirectResponse(url="/login_form", status_code=303)

            # Add session to kwargs and call the function
            import inspect
            sig = inspect.signature(func)
            if 'session' in sig.parameters:
                kwargs['session'] = session

            # ONLY pass kwargs. Do not pass 'request' or '*args' separately.
            return await func(**kwargs)
        return wrapper
    return decorator


def verify_password(password: str, salt: bytes, stored_hash: bytes) -> bool:
    """Verify password against stored hash"""
    key = derive_key(password, salt).hex()
    return key == stored_hash


@app.get("/", response_class=HTMLResponse)
async def get_vault(request: Request):
    return templates.TemplateResponse("index.html",
                                      {"request": request})


@app.get("/api/password_default_data")
async def get_password_data():
    from password_gen import create_password, verify_password_strength, get_password_strength_percent
    password: str = create_password(12)
    strength: str = verify_password_strength(password)
    strength_value: int = get_password_strength_percent(password)
    default_password_length: int = 16

    return {
        "password": password,
        "strength": strength,
        "default_password_length": default_password_length,
        "strength_value": strength_value
    }


@app.get("/vault", response_class=HTMLResponse)
@login_required()
async def save_password(request: Request):
    return templates.TemplateResponse("vault.html",
                                      {"request": request})


@app.get("/register_form", response_class=HTMLResponse)
async def register_form(request: Request):
    # Check if a user already exist seeing that the application is designed
    # for one user, and redirect user to login_form to sign in
    db = SessionLocal()
    user = db.query(User).first()

    if user:
        return RedirectResponse(url="/login_form", status_code=303)

    return templates.TemplateResponse("register.html",
                                      {"request": request})


@app.get("/login_form", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html",
                                      {"request": request})


@app.post("/register")
async def register(
    master_password: str = Form(...),
):
    salt = secrets.token_bytes(16)
    key = derive_key(master_password, salt).hex()

    db = SessionLocal()

    new_user = User(
        salt=salt,
        password_hash=key
    )

    db.add(new_user)
    db.commit()
    db.close()

    return RedirectResponse(url="/login_form", status_code=303)

    """DATABASE APIs"""


@app.post("/login")
async def login(
    request: Request,
    master_password: str = Form(...),
):
    db = SessionLocal()

    user = db.query(User).first()

    if not verify_password(master_password, user.salt, user.password_hash):
        db.close()
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid master password"
            },
            status_code=400
        )
    db.close()

    # Create session
    session_token = create_session(user.id, master_password)

    # Set cookie and redirect
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Can't access via JavaScript
        secure=False,   # Set to True in production with HTTPS
        max_age=3600,   # 1 hour
        samesite="lax"
    )

    return response


@app.get("/logout")
async def logout(request: Request):
    """Logout - remove session"""
    session_token = request.cookies.get("session_token")
    if session_token and session_token in active_session:
        del active_session[session_token]

    response = RedirectResponse(url="/login_form", status_code=303)
    response.delete_cookie("session_token")
    return response


@app.get("/api/retreive_password")
@login_required(api_route=True)
async def retrieve_password(request: Request):
    db = SessionLocal()

    session_token = request.cookies.get("session_token")
    master_password = active_session.get(session_token)["master_password"]

    user = db.query(User).first()

    try:
        password_list = db.query(Password).all()
        for p in password_list:
            print(p)

        if not password_list:
            return {"message": "no passwords in database"}

        decrypted_data = []
        try:
            for p in password_list:
                decrypted_data.append({
                    "id": p.id,
                    "login": decrypt_with_master(
                        p.login,
                        master_password,
                        user.salt
                    ),
                    "username": decrypt_with_master(
                        p.username,
                        master_password,
                        user.salt
                    ),
                    "password": decrypt_with_master(
                        p.password,
                        master_password,
                        user.salt
                    ),
                })

        except Exception:
            print("unable to decrypt")

    finally:
        db.close()

    return {"password_data": decrypted_data}


class SavePassword(BaseModel):
    password: str
    account_name: str
    my_username: str


@app.post("/add_password")
@login_required(api_route=True)
async def add_password(
        new_login: Annotated[SavePassword, Form()],
        request: Request
):
    # Save new password to database
    db = SessionLocal()
    user = db.query(User).first()

    session_token = request.cookies.get("session_token")
    master_password = active_session.get(session_token)["master_password"]

    new_password = Password(
        user_id=user.id,
        login=encrypt_with_master(
            new_login.account_name,
            master_password,
            user.salt
        ),
        username=encrypt_with_master(
            new_login.my_username,
            master_password,
            user.salt
        ),
        # TODO: encrypt the password
        password=encrypt_with_master(
            new_login.password,
            master_password,
            user.salt
        )
    )

    print(new_login)

    db.add(new_password)
    db.commit()
    db.close()

    return RedirectResponse(url="/vault", status_code=303)


@ app.post("/delete/{password_id}")
@ login_required(api_route=True)
async def delete_password(password_id: int):

    db = SessionLocal()
    password = db.query(Password).filter(Password.id == password_id).first()
    if password:
        db.delete(password)
        db.commit()
        db.close()

        return RedirectResponse(url="/", status_code=303)

    """ Generate Password from server """


class PasswordSettings(BaseModel):
    password_length: int
    uppercase: bool
    numbers: bool
    symbols: bool


@ app.post("/generate_password")
async def generate_password(settings: PasswordSettings):

    from password_gen import create_password, verify_password_strength, get_password_strength_percent

    password: str = create_password(
        settings.password_length,
        settings.uppercase,
        settings.numbers,
        settings.symbols
    )
    strength: str = verify_password_strength(password)
    strength_value: int = get_password_strength_percent(password)

    return {
        "status": "success",
        "generated_password": password,
        "strength": strength,
        "strength_value": strength_value
    }
