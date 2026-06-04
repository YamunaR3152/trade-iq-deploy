# TradeIQ Academy — Backend

Quantitative Trading & Investment Simulation Platform.

## Project Structure

```
tradeiq/
├── app/
│   ├── __init__.py              # App factory (create_app)
│   ├── extensions.py            # db, jwt, cors instances
│   ├── models.py                # SQLAlchemy models (all 9 tables)
│   │
│   ├── auth/                    # Authentication module
│   │   ├── __init__.py
│   │   └── routes.py            # POST /auth/register, /auth/login
│   │
│   ├── market/                  # Market data pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py          # YahooFinancePipeline (from notebook)
│   │   └── routes.py            # GET /market/stock, /market/history, /market/benchmark
│   │
│   ├── portfolio/               # Portfolio & trading engine
│   │   ├── __init__.py
│   │   └── routes.py            # POST /portfolio/trade, GET /portfolio/holdings, /portfolio/summary
│   │
│   ├── scoring/                 # Scoring engines
│   │   ├── __init__.py
│   │   ├── roi_engine.py
│   │   ├── risk_engine.py
│   │   ├── strategy_engine.py
│   │   ├── execution_engine.py
│   │   ├── thesis_engine.py
│   │   └── final_scoring_engine.py
│   │
│   └── analytics/               # Analytics + leaderboard
│       ├── __init__.py
│       └── routes.py            # GET /analytics/leaderboard, /analytics/scores/:user_id
│
├── config/
│   └── settings.py              # Config classes (Dev / Prod)
│
├── migrations/
│   └── schema.sql               # Full MySQL schema
│
├── .env.example                 # Environment variable template
├── requirements.txt
└── run.py                       # Entry point
```

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your DB credentials and secret keys

# 4. Create the database
mysql -u root -p < migrations/schema.sql

# 5. Run the server
python run.py
```

## API Overview

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/auth/register` | Register a new student |
| POST | `/auth/login` | Login, returns JWT |
| GET | `/market/stock/<ticker>` | Stock info (name, sector, beta) |
| GET | `/market/history/<ticker>` | Price history + daily returns |
| GET | `/market/benchmark` | S&P 500 benchmark data |
| POST | `/portfolio/trade` | Execute buy/sell trade |
| GET | `/portfolio/holdings/<user_id>` | Current holdings |
| GET | `/portfolio/summary/<user_id>` | Portfolio value, P&L |
| GET | `/analytics/scores/<user_id>` | Full score breakdown |
| GET | `/analytics/leaderboard` | Live leaderboard |
