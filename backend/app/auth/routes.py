import uuid
import hashlib
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import User, PortfolioSetup

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _make_user_id() -> str:
    """Generate a short unique user ID like TIQ-A3F9."""
    return "TIQ-" + uuid.uuid4().hex[:4].upper()


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
        course             = data.get("course"),
        year_of_study      = data.get("year_of_study"),
        participation_type = data.get("participation_type", "individual"),
        team_name          = data.get("team_name"),
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
