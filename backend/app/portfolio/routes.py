# backend/app/portfolio/routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import limiter
from app.repositories.user_repository import is_admin
from app.services.portfolio_service import (
    execute_trade,
    get_holdings,
    delete_holding,
    get_summary,
    get_trades,
    PortfolioError,
)

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")


@portfolio_bp.errorhandler(PortfolioError)
def handle_portfolio_error(e: PortfolioError):
    return jsonify({"error": e.message}), e.status_code


@portfolio_bp.post("/trade")
@limiter.limit("120 per minute")
@jwt_required()
def trade():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}

    # Extract X-Idempotency-Key from headers if present and not in JSON payload
    if "idempotency_key" not in data:
        header_key = request.headers.get("X-Idempotency-Key")
        if header_key:
            data["idempotency_key"] = header_key

    result = execute_trade(user_id, data)

    # 🚀 AUTO-SCORE HOOK (Safely imported inside hook to prevent boot crashes)
    try:
        from app.analytics.routes import compute_user_score
        compute_user_score(user_id)
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(
            f"Auto-scoring background hook skipped/failed for user {user_id}: {e}"
        )

    # Return 200 OK if duplicate request was ignored, otherwise 201 Created
    is_duplicate = result.get("message") == "Duplicate request ignored."
    status_code = 200 if is_duplicate else 201
    message = "Duplicate request ignored" if is_duplicate else "Trade executed"
    trade_id = result.get("trade_id") or (result.get("trade") or {}).get("id")
    return jsonify({
        "message": message,
        "trade_id": trade_id,
        "trade": result["trade"],
        "cash_balance": result["cash_balance"],
    }), status_code


@portfolio_bp.get("/holdings/<string:user_id>")
@jwt_required()
def holdings(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to view holdings for this user"}), 403
    return jsonify(get_holdings(user_id)), 200


@portfolio_bp.delete("/holding/<path:ticker>")
@portfolio_bp.delete("/holdings/<path:ticker>")
@jwt_required()
def remove_holding(ticker):
    user_id = get_jwt_identity()
    result = delete_holding(user_id, ticker)
    return jsonify({"message": "Holding deleted", **result}), 200


@portfolio_bp.get("/summary/<string:user_id>")
@jwt_required()
def summary(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to view summary for this user"}), 403
    result = get_summary(user_id)
    return jsonify(result), 200


@portfolio_bp.get("/trades/<string:user_id>")
@jwt_required()
def trades(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to view trades for this user"}), 403
    return jsonify(get_trades(user_id)), 200