import uuid
import hashlib
import os
from datetime import date, datetime, timezone
from functools import lru_cache

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
import jwt
import requests

from app.extensions import db
from app.models import User, PortfolioSetup

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _make_user_id() -> str:
    """Generate a short unique user ID like TIQ-A3F9."""
    return "TIQ-" + uuid.uuid4().hex[:4].upper()


def _get_firebase_project_id() -> str:
    return os.getenv("FIREBASE_PROJECT_ID", "tradeiq-26")


@lru_cache(maxsize=1)
def _get_firebase_public_certs() -> dict:
    response = requests.get(
        "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def _verify_firebase_id_token(id_token: str) -> dict:
    project_id = _get_firebase_project_id()
    unverified_header = jwt.get_unverified_header(id_token)
    cert = _get_firebase_public_certs().get(unverified_header.get("kid"))
    if not cert:
        _get_firebase_public_certs.cache_clear()
        cert = _get_firebase_public_certs().get(unverified_header.get("kid"))
    if not cert:
        raise ValueError("Could not find Firebase public key for token.")

    payload = jwt.decode(
        id_token,
        cert,
        algorithms=["RS256"],
        audience=project_id,
        issuer=f"https://securetoken.google.com/{project_id}",
    )
    if payload.get("exp", 0) < datetime.now(timezone.utc).timestamp():
        raise ValueError("Firebase token has expired.")
    return payload


def _ensure_default_portfolio(user_id: str) -> None:
    if PortfolioSetup.query.filter_by(user_id=user_id).first():
        return
    db.session.add(
        PortfolioSetup(
            user_id=user_id,
            total_capital=10000.00,
            cash_balance=10000.00,
        )
    )


# ─────────────────────────────────────────
# POST /auth/register
# ─────────────────────────────────────────

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    required = ["full_name", "email", "password"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        user_id            = _make_user_id(),
        full_name          = data["full_name"],
        email              = data["email"],
        password_hash      = _hash_password(data["password"]),
        age                = data.get("age"),
        date_of_birth      = data.get("date_of_birth"),
        phone_number       = data.get("phone_number"),
        university         = data.get("university"),
        year_of_study      = data.get("year_of_study"),
        role               = data.get("role", "student"),
    )
    db.session.add(user)

    # Auto-create portfolio with default £10,000 capital
    portfolio = PortfolioSetup(
        user_id            = user.user_id,
        total_capital      = data.get("total_capital", 10000.00),
        cash_balance       = data.get("total_capital", 10000.00),
        risk_appetite      = data.get("risk_appetite"),
        investment_horizon = data.get("investment_horizon"),
        competition_round  = data.get("competition_round"),
    )
    db.session.add(portfolio)
    db.session.commit()

    token = create_access_token(identity=user.user_id)
    return jsonify({
        "message": "Registration successful",
        "user":    user.to_dict(),
        "token":   token,
    }), 201


# ─────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    email    = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or user.password_hash != _hash_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=user.user_id)
    return jsonify({
        "message": "Login successful",
        "user":    user.to_dict(),
        "token":   token,
    }), 200


@auth_bp.post("/google")
def google_auth():
    data = request.get_json(silent=True)
    if not data or not data.get("id_token"):
        return jsonify({"error": "Firebase ID token required"}), 400

    try:
        firebase_user = _verify_firebase_id_token(data["id_token"])
    except Exception as exc:
        return jsonify({"error": f"Invalid Google sign-in token: {exc}"}), 401

    email = (firebase_user.get("email") or "").strip().lower()
    full_name = (firebase_user.get("name") or email.split("@")[0] or "Google User").strip()
    firebase_uid = firebase_user.get("sub")

    if not email:
        return jsonify({"error": "Google account did not provide an email address"}), 400

    user = User.query.filter_by(email=email).first()
    is_new_user = user is None

    if is_new_user:
        user = User(
            user_id=_make_user_id(),
            full_name=full_name,
            email=email,
            password_hash=_hash_password(f"firebase:{firebase_uid}"),
            role="student",
        )
        db.session.add(user)
        db.session.flush()
    elif full_name and not user.full_name:
        user.full_name = full_name

    _ensure_default_portfolio(user.user_id)
    db.session.commit()

    token = create_access_token(identity=user.user_id)
    return jsonify({
        "message": "Google authentication successful",
        "user": user.to_dict(),
        "token": token,
        "is_new_user": is_new_user,
    }), 200 if not is_new_user else 201
