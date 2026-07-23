# this is backend/app/auth/routes.py
from flask import Blueprint, jsonify, request
from app.extensions import limiter
from app.services.auth_service import register_user, login_user, AuthError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.errorhandler(AuthError)
def handle_auth_error(e: AuthError):
    return jsonify({"error": e.message}), e.status_code


@auth_bp.post("/register")
@limiter.limit("10 per hour")
def register():
    user, token = register_user(request.get_json(silent=True))
    return jsonify({
        "message": "Registration successful",
        "user": user,
        "token": token,
    }), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    user, token = login_user(request.get_json(silent=True))
    return jsonify({
        "message": "Login successful",
        "user": user,
        "token": token,
    }), 200