# =====================================
# ROI SCORE (50)
# =====================================
#
# Breakdown:
#   total_return_score  → /20
#   benchmark_score     → /20
#   net_profit_score    → /10
# =====================================


# Total Return Score (/20)
# Maps portfolio return % to a 0-20 score.
# 0% return = 0 pts, 30%+ return = 20 pts (linear, capped)

def total_return_score(portfolio_return_pct: float) -> float:
    score = min(20, max(0, (portfolio_return_pct / 30) * 20))
    return round(score, 2)


# Benchmark Score (/20)
# Rewards outperforming the S&P 500.
# Matching benchmark = 10 pts, +10% alpha = 20 pts, -10% = 0 pts

def benchmark_score(
    portfolio_return_pct: float,
    benchmark_return_pct: float,
) -> float:
    alpha = portfolio_return_pct - benchmark_return_pct
    score = min(20, max(0, 10 + (alpha / 10) * 10))
    return round(score, 2)


# Net Profit Score (/10)
# Absolute profit contribution relative to starting capital.
# ≥ £500 profit on £10k = full marks

def net_profit_score(
    net_profit:    float,
    total_capital: float = 10000.0,
) -> float:
    if total_capital == 0:
        return 0.0
    pct = (net_profit / total_capital) * 100
    score = min(10, max(0, (pct / 5) * 10))
    return round(score, 2)


# Aggregate ROI Score (/50)

def roi_score(
    total_return_score: float,
    benchmark_score:    float,
    net_profit_score:   float,
) -> float:
    return round(
        total_return_score + benchmark_score + net_profit_score,
        2,
    )
