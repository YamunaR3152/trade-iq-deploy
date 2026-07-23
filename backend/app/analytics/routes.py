# this is backend\app\analytics\routes.py
from datetime import date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import limiter
from app.repositories.user_repository import is_admin
from app.services import analytics_service as service
from app.services.analytics_service import AnalyticsError

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.errorhandler(AnalyticsError)
def handle_analytics_error(e: AnalyticsError):
    return jsonify({"error": e.message}), e.status_code


@analytics_bp.get("/leaderboard")
@limiter.limit("60 per minute")
@jwt_required()
def get_leaderboard():
    week = request.args.get("week", default=date.today().isocalendar()[1], type=int)
    result = service.get_leaderboard_service(week)
    return jsonify(result), 200


@analytics_bp.get("/scores/<string:user_id>")
@limiter.limit("60 per minute")
@jwt_required()
def get_scores(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to view scores for this user"}), 403

    result = service.get_scores_service(user_id)
    return jsonify(result), 200


@analytics_bp.get("/risk/<string:user_id>")
@limiter.limit("60 per minute")
@jwt_required()
def get_risk(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to view risk metrics for this user"}), 403

    result = service.get_risk_service(user_id)
    return jsonify(result), 200


@analytics_bp.post("/compute-legacy/<string:user_id>")
@limiter.limit("20 per minute")
@jwt_required()
def compute_scores(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to compute legacy scores for this user"}), 403

    result = service.compute_legacy_scores_service(user_id)
    return jsonify({"message": "Legacy scores computed", **result}), 200


@analytics_bp.post("/compute/<string:user_id>")
@limiter.limit("20 per minute")
@jwt_required()
def compute_and_persist_scores(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id != user_id and not is_admin(current_user_id):
        return jsonify({"error": "Not authorized to compute scores for this user"}), 403

    week_number = request.args.get("week", default=date.today().isocalendar()[1], type=int)
    result = service.compute_and_persist_scores_service(user_id, week_number)
    return jsonify({"message": "Scores computed", **result}), 200