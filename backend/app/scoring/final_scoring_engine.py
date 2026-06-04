import pandas as pd

from app.scoring.roi_engine       import total_return_score, benchmark_score, net_profit_score, roi_score
from app.scoring.risk_engine      import sharpe_score, drawdown_score, beta_score, risk_score
from app.scoring.strategy_engine  import diversification_score, consistency_score, prediction_score, strategy_score
from app.scoring.execution_engine import classification_score, documentation_score, execution_score
from app.scoring.thesis_engine    import ai_thesis_score


# =====================================
# FINAL SCORING ENGINE
# =====================================

class TradeIQScoringEngine:

    # ── ROI (50) ──────────────────────

    @staticmethod
    def roi_score(
        portfolio_return_pct: float,
        benchmark_return_pct: float,
        net_profit:           float,
        total_capital:        float = 10000.0,
    ) -> float:
        trs = total_return_score(portfolio_return_pct)
        bs  = benchmark_score(portfolio_return_pct, benchmark_return_pct)
        nps = net_profit_score(net_profit, total_capital)
        return roi_score(trs, bs, nps)

    # ── Risk (20) ─────────────────────

    @staticmethod
    def risk_score(
        sharpe:           float,
        drawdown_percent: float,
        beta:             float,
    ) -> float:
        sh = sharpe_score(sharpe)
        dd = drawdown_score(drawdown_percent)
        bt = beta_score(beta)
        return risk_score(sh, dd, bt)

    # ── Strategy (15) ─────────────────

    @staticmethod
    def strategy_score(
        sectors:           int,
        max_allocation:    float,
        weeks_active:      int,
        correct_direction: int,
        total_trades:      int,
    ) -> float:
        dv = diversification_score(sectors, max_allocation)
        cs = consistency_score(weeks_active)
        pr = prediction_score(correct_direction, total_trades)
        return strategy_score(dv, cs, pr)

    # ── Execution (10) ────────────────

    @staticmethod
    def execution_score(
        unique_tags:       int,
        trades_with_thesis:int,
        total_trades:      int,
    ) -> float:
        cl = classification_score(unique_tags, total_trades)
        dc = documentation_score(trades_with_thesis, total_trades)
        return execution_score(cl, dc)

    # ── Thesis (5) ────────────────────

    @staticmethod
    def thesis_score(
        clarity:              float,
        financial_logic:      float,
        risk_awareness:       float,
        market_understanding: float,
    ) -> float:
        return ai_thesis_score(
            clarity,
            financial_logic,
            risk_awareness,
            market_understanding,
        )

    # ── Final (100) ───────────────────

    @staticmethod
    def final_score(
        roi:       float,
        risk:      float,
        strategy:  float,
        execution: float,
        thesis:    float,
    ) -> float:
        return round(roi + risk + strategy + execution + thesis, 2)

    # ── Full pipeline (one call) ──────

    @classmethod
    def score_student(cls, data: dict) -> dict:
        """
        Compute every sub-score and the final score from a single dict.

        Expected keys:
            portfolio_return_pct, benchmark_return_pct, net_profit, total_capital
            sharpe, drawdown_percent, beta
            sectors, max_allocation, weeks_active, correct_direction, total_trades
            unique_tags, trades_with_thesis
            clarity, financial_logic, risk_awareness, market_understanding
        """
        roi       = cls.roi_score(
            data["portfolio_return_pct"],
            data["benchmark_return_pct"],
            data["net_profit"],
            data.get("total_capital", 10000.0),
        )
        risk      = cls.risk_score(
            data["sharpe"],
            data["drawdown_percent"],
            data["beta"],
        )
        strat     = cls.strategy_score(
            data["sectors"],
            data["max_allocation"],
            data["weeks_active"],
            data["correct_direction"],
            data["total_trades"],
        )
        execution = cls.execution_score(
            data["unique_tags"],
            data["trades_with_thesis"],
            data["total_trades"],
        )
        thesis    = cls.thesis_score(
            data["clarity"],
            data["financial_logic"],
            data["risk_awareness"],
            data["market_understanding"],
        )
        final = cls.final_score(roi, risk, strat, execution, thesis)

        return {
            "roi_score":       roi,
            "risk_score":      risk,
            "strategy_score":  strat,
            "execution_score": execution,
            "thesis_score":    thesis,
            "final_score":     final,
        }


# =====================================
# LEADERBOARD RANKING
# =====================================

def rank_students(df: pd.DataFrame) -> pd.DataFrame:
    """Add a Rank column to a DataFrame that has a 'Final Score' column."""
    df["Rank"] = (
        df["Final Score"]
        .rank(ascending=False, method="dense")
        .astype(int)
    )
    return df.sort_values("Rank")
