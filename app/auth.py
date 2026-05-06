from fastapi import Request
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User

MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 72


def validate_password(password: str) -> str | None:
    if not password:
        return "Password is required."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
    if len(password.encode("utf-8")) > MAX_PASSWORD_LENGTH:
        return f"Password must not be longer than {MAX_PASSWORD_LENGTH} characters."
    return None


def get_password_hash(password: str) -> str:
    password_error = validate_password(password)
    if password_error:
        raise ValueError(password_error)
    return generate_password_hash(password, method="pbkdf2:sha256", salt_length=16)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False

    try:
        return check_password_hash(hashed_password, plain_password)
    except (ValueError, TypeError):
        # Old or malformed hashes should fail closed without breaking login.
        return False


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower().strip()).first()


def login_user(request: Request, user: User) -> None:
    request.session["user_id"] = user.id


def logout_user(request: Request) -> None:
    request.session.pop("user_id", None)


def get_current_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()


def add_flash_message(request: Request, category: str, message: str) -> None:
    flashes = request.session.get("flash_messages", [])
    flashes.append({"category": category, "message": message})
    request.session["flash_messages"] = flashes


def pop_flash_messages(request: Request) -> list[dict[str, str]]:
    flashes = request.session.get("flash_messages", [])
    request.session["flash_messages"] = []
    return flashes
