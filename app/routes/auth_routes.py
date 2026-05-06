from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.auth import (
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    add_flash_message,
    get_current_user,
    get_password_hash,
    get_user_by_email,
    login_user,
    logout_user,
    pop_flash_messages,
    validate_password,
    verify_password,
)
from app.database import get_db
from app.models import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/signup")
def signup_page(request: Request, db: Session = Depends(get_db)):
    if get_current_user(request, db):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
        context={
            "request": request,
            "flashes": pop_flash_messages(request),
            "page_title": "Create Account",
        },
    )


@router.post("/signup")
def signup(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    cleaned_name = full_name.strip()
    cleaned_email = email.lower().strip()
    cleaned_password = password or ""
    cleaned_confirm_password = confirm_password or ""

    if len(cleaned_name) < 3:
        add_flash_message(request, "danger", "Full name must contain at least 3 characters.")
        return RedirectResponse(url="/signup", status_code=303)

    if cleaned_password != cleaned_confirm_password:
        add_flash_message(request, "danger", "Passwords do not match.")
        return RedirectResponse(url="/signup", status_code=303)

    password_error = validate_password(cleaned_password)
    if password_error:
        add_flash_message(request, "danger", password_error)
        return RedirectResponse(url="/signup", status_code=303)

    if len(cleaned_confirm_password.encode("utf-8")) > MAX_PASSWORD_LENGTH:
        add_flash_message(
            request,
            "danger",
            f"Password confirmation must not be longer than {MAX_PASSWORD_LENGTH} characters.",
        )
        return RedirectResponse(url="/signup", status_code=303)

    existing_user = get_user_by_email(db, cleaned_email)
    if existing_user:
        add_flash_message(request, "warning", "An account with that email already exists.")
        return RedirectResponse(url="/signup", status_code=303)

    new_user = User(
        full_name=cleaned_name,
        email=cleaned_email,
        password_hash="",
    )
    try:
        new_user.password_hash = get_password_hash(cleaned_password)
    except ValueError as exc:
        add_flash_message(request, "danger", str(exc))
        return RedirectResponse(url="/signup", status_code=303)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    add_flash_message(request, "success", "Your account has been created successfully. Please log in.")
    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    if get_current_user(request, db):
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
            "flashes": pop_flash_messages(request),
            "page_title": "Login",
        },
    )


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    password_error = validate_password(password or "")
    if password_error:
        add_flash_message(
            request,
            "danger",
            f"Password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters long.",
        )
        return RedirectResponse(url="/login", status_code=303)

    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        add_flash_message(request, "danger", "Invalid email or password. Please try again.")
        return RedirectResponse(url="/login", status_code=303)

    login_user(request, user)
    add_flash_message(request, "success", f"Welcome back, {user.full_name}.")
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    logout_user(request)
    add_flash_message(request, "info", "You have been logged out.")
    return RedirectResponse(url="/", status_code=303)
