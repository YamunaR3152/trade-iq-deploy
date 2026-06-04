from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models import (
    User, Leaderboard, WeeklyScore, RiskMetrics,
    TradeLog, Holding, PortfolioSetup,
)
from app.market.pipeline import YahooFinancePipeline
from app.scoring.final_scoring_engine import TradeIQScoringEngine

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")
pipeline     = YahooFinancePipeline()


# ─────────────────────────────────────────
# GET /analytics/leaderboard?week=<n>
# Returns ranked leaderboard for a given week (defaults to latest)
# ─────────────────────────────────────────

@analytics_bp.get("/leaderboard")
@jwt_required()
def get_leaderboard():
    week = request.args.get("week", type=int)

    query = Leaderboard.query
    if week:
        query = query.filter_by(week_number=week)

    entries = query.order_by(Leaderboard.rank_position.asc()).all()

    return jsonify({
        "week":    week,
        "count":   len(entries),
        "entries": [e.to_dict() for e in entries],
    }), 200


# ─────────────────────────────────────────
# GET /analytics/scores/<user_id>
# Full score breakdown for a student
# ─────────────────────────────────────────

@analytics_bp.get("/scores/<string:user_id>")
@jwt_required()
def get_scores(user_id):
    scores = WeeklyScore.query\
        .filter_by(user_id=user_id)\
        .order_by(WeeklyScore.week_number.desc())\
        .all()

    return jsonify({
        "user_id": user_id,
        "scores":  [s.to_dict() for s in scores],
    }), 200


# ─────────────────────────────────────────
# GET /analytics/risk/<user_id>
# Latest risk metrics for a student
# ─────────────────────────────────────────

@analytics_bp.get("/risk/<string:user_id>")
@jwt_required()
def get_risk(user_id):
    risk = RiskMetrics.query.filter_by(user_id=user_id).first()
    if not risk:
        return jsonify({"error": "No risk metrics found"}), 404
    return jsonify({"user_id": user_id, "risk": risk.to_dict()}), 200


# ─────────────────────────────────────────
# POST /analytics/compute/<user_id>
# Recalculate scores for a student on demand
# (for testing / manual trigger before weekly batch)
# ─────────────────────────────────────────

@analytics_bp.post("/compute/<string:user_id>")
@jwt_required()
def compute_scores(user_id):
    portfolio = PortfolioSetup.query.filter_by(user_id=user_id).first()
    if not portfolio:
        return jsonify({"error": "Portfolio not found"}), 404

    trades   = TradeLog.query.filter_by(user_id=user_id).all()
    holdings = Holding.query.filter_by(user_id=user_id).all()
    risk     = RiskMetrics.query.filter_by(user_id=user_id).first()

    if not trades:
        return jsonify({"error": "No trades found — cannot score"}), 400

    # ── Portfolio return ──────────────────
    total_capital     = float(portfolio.total_capital)
    cash_balance      = float(portfolio.cash_balance)
    holdings_value    = sum(float(h.market_value or 0) for h in holdings)
    total_portfolio   = cash_balance + holdings_value
    portfolio_return  = ((total_portfolio - total_capital) / total_capital) * 100
    net_profit        = total_portfolio - total_capital

    # ── Benchmark return (YTD S&P 500) ───
    # Approximation — weekly batch will use exact date-matched returns
    benchmark_return = 10.0  # placeholder; replaced by pipeline in batch job

    # ── Risk metrics ─────────────────────
    sharpe   = float(risk.sharpe_ratio or 0) if risk else 0.0
    drawdown = float(risk.max_drawdown or 0) if risk else 0.0
    beta     = float(risk.beta or 1.0)       if risk else 1.0

    # ── Strategy inputs ───────────────────
    sectors     = len(set(t.sector for t in trades if t.sector))
    alloc_vals  = [float(t.allocation_percent or 0) for t in trades]
    max_alloc   = max(alloc_vals) if alloc_vals else 0.0
    weeks_active= len(set(t.trade_date.isocalendar()[1] for t in trades if t.trade_date))

    buy_trades  = [t for t in trades if t.trade_type == "BUY"]
    correct_dir = sum(
        1 for t in buy_trades
        if t.current_sell_price and t.buy_price
        and float(t.current_sell_price) > float(t.buy_price)
    )

    # ── Execution inputs ──────────────────
    tagged_trades  = [t for t in trades if any([t.tag1, t.tag2, t.tag3])]
    all_tags       = []
    for t in trades:
        all_tags += [x for x in [t.tag1, t.tag2, t.tag3] if x]
    unique_tags    = len(set(all_tags))
    with_thesis    = sum(1 for t in trades if t.thesis)

    # ── Thesis ────────────────────────────
    # Pulled from latest thesis_scores row; defaults to 0 if none scored yet
    clarity = financial_logic = risk_awareness = market_understanding = 0.0

    data = {
        "portfolio_return_pct": round(portfolio_return, 4),
        "benchmark_return_pct": benchmark_return,
        "net_profit":           round(net_profit, 4),
        "total_capital":        total_capital,
        "sharpe":               sharpe,
        "drawdown_percent":     drawdown,
        "beta":                 beta,
        "sectors":              sectors,
        "max_allocation":       max_alloc,
        "weeks_active":         weeks_active,
        "correct_direction":    correct_dir,
        "total_trades":         len(trades),
        "unique_tags":          unique_tags,
        "trades_with_thesis":   with_thesis,
        "clarity":              clarity,
        "financial_logic":      financial_logic,
        "risk_awareness":       risk_awareness,
        "market_understanding": market_understanding,
    }

    result = TradeIQScoringEngine.score_student(data)

    return jsonify({
        "user_id": user_id,
        "inputs":  data,
        "scores":  result,
    }), 200
