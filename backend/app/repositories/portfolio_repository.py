# backend/app/repositories/portfolio_repository.py
from app.extensions import db
from app.models import Holding, PortfolioSetup, TradeLog


def find_portfolio(user_id: str) -> PortfolioSetup | None:
    return PortfolioSetup.query.filter_by(user_id=user_id).first()


def find_holding(user_id: str, ticker: str) -> Holding | None:
    return Holding.query.filter_by(user_id=user_id, stock_ticker=ticker.upper()).first()


def find_portfolio_for_update(user_id: str) -> PortfolioSetup | None:
    return PortfolioSetup.query.filter_by(user_id=user_id).with_for_update().first()


def find_holding_for_update(user_id: str, ticker: str) -> Holding | None:
    return Holding.query.filter_by(user_id=user_id, stock_ticker=ticker.upper()).with_for_update().first()


def find_active_holdings(user_id: str) -> list[Holding]:
    return Holding.query.filter_by(user_id=user_id).all()


def find_latest_trade(user_id: str, ticker: str) -> TradeLog | None:
    return TradeLog.query.filter_by(
        user_id=user_id,
        stock_ticker=ticker.upper(),
    ).order_by(TradeLog.created_at.desc()).first()


def find_latest_thesis_trade(user_id: str, ticker: str) -> TradeLog | None:
    return TradeLog.query.filter_by(
        user_id=user_id,
        stock_ticker=ticker.upper(),
    ).filter(
        TradeLog.thesis.isnot(None),
        TradeLog.thesis != "",
    ).order_by(TradeLog.created_at.desc()).first()


def find_trades_for_user(user_id: str) -> list[TradeLog]:
    return (
        TradeLog.query.filter_by(user_id=user_id)
        .order_by(TradeLog.created_at.desc())
        .all()
    )


# ─── ADDED HERE ───────────────────────────────────────────────
def find_trade_by_idempotency_key(key: str) -> TradeLog | None:
    return TradeLog.query.filter_by(idempotency_key=key).first()
# ───────────────────────────────────────────────────────────────


def create_trade(**fields) -> TradeLog:
    trade = TradeLog(**fields)
    db.session.add(trade)
    return trade


def create_holding(**fields) -> Holding:
    holding = Holding(**fields)
    db.session.add(holding)
    return holding


def delete_holding(holding: Holding) -> None:
    db.session.delete(holding)


def delete_trades_for_ticker(user_id: str, ticker: str) -> None:
    TradeLog.query.filter_by(user_id=user_id, stock_ticker=ticker.upper()).delete(
        synchronize_session=False
    )


def flush() -> None:
    db.session.flush()


def save() -> None:
    db.session.commit()