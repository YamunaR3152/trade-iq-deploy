# this is backend/app/services/auth_service.py
import uuid
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash

from app.repositories import user_repository


class AuthError(Exception):
    """Raised when a registration/login request is invalid.
    Carries the HTTP status code the route should respond with."""
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _hash_password(password: str) -> str:
    return generate_password_hash(password)


def _verify_password(stored_hash: str, password: str) -> bool:
    return check_password_hash(stored_hash, password)


def _make_user_id() -> str:
    return "TIQ-" + uuid.uuid4().hex[:4].upper()


def register_user(data: dict) -> tuple[dict, str]:
    """Returns (user_dict, token). Raises AuthError if the request is invalid."""
    if not data:
        raise AuthError("JSON body required", 400)

    required = ["full_name", "email", "password"]
    missing = [f for f in required if not data.get(f)]
    if missing:
        raise AuthError(f"Missing fields: {', '.join(missing)}", 400)

    if user_repository.find_user_by_email(data["email"]):
        raise AuthError("Email already registered", 409)

    user = user_repository.create_user(
        user_id=_make_user_id(),
        full_name=data["full_name"],
        email=data["email"],
        password_hash=_hash_password(data["password"]),
        age=data.get("age"),
        date_of_birth=data.get("date_of_birth"),
        phone_number=data.get("phone_number"),
        university=data.get("university"),
        year_of_study=data.get("year_of_study"),
        role=data.get("role", "student"),
    )

    user_repository.create_portfolio_setup(
        user_id=user.user_id,
        total_capital=data.get("total_capital", 10000.00),
        cash_balance=data.get("total_capital", 10000.00),
        risk_appetite=data.get("risk_appetite"),
        investment_horizon=data.get("investment_horizon"),
        competition_round=data.get("competition_round"),
    )

    user_repository.save()

    token = create_access_token(identity=user.user_id)
    return user.to_dict(), token


def login_user(data: dict) -> tuple[dict, str]:
    """Returns (user_dict, token). Raises AuthError if the request is invalid."""
    if not data:
        raise AuthError("JSON body required", 400)

    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        raise AuthError("Email and password required", 400)

    user = user_repository.find_user_by_email(email)
    if not user or not _verify_password(user.password_hash, password):
        raise AuthError("Invalid email or password", 401)

    token = create_access_token(identity=user.user_id)
    return user.to_dict(), token