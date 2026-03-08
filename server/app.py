
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from typing import Annotated

from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import secrets

from pydantic import BaseModel

from state import active_session
from src.password_gen import (
    create_password,
    verify_password_strength,
    get_password_strength_percent
)
from src.helper import (
    derive_key,
    decrypt_with_master,
    encrypt_with_master,
    verify_password
)
from src.database import (
    Password,
    User,
    Base
)
from src.session_manager import (
    login_required,
    create_session,
)

# FAST API
app = FastAPI()
app.mount("/static", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="templates")

# DATABASE
SQLALCHEMY_DATABASE_URL = "sqlite:///./password.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={
    "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
                                      {"request": request})


@app.get("/api/password_default_data")
async def get_password_data():
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


@app.post("/delete/{password_id}")
@login_required(api_route=True)
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


@app.post("/generate_password")
async def generate_password(settings: PasswordSettings):

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
