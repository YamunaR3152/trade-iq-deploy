# TradeIQ Academy — SalesTrading Platform

Quantitative Trading & Investment Simulation Platform for students.

---

## Project Structure

```
SalesTrading/
├── backend/           # Flask REST API
├── frontend/          # Expo React Native app
│   └── DRA App/
├── database/          # Database assets
├── engine/            # Scoring engine
└── docker-compose.yml # MySQL via Docker
```

---

## Prerequisites

- Python 3.13+
- Node.js 18+
- Docker Desktop

---

## MySQL (Docker)

MySQL runs via Docker Compose. The schema is auto-loaded on first start.

### Start

```bash
docker compose up -d
```

### Stop

```bash
docker compose down
```

### Connection details

| Field    | Value       |
|----------|-------------|
| Host     | `localhost` |
| Port     | `3306`      |
| Database | `tradeiq`   |
| User     | `root`      |
| Password | _(empty)_   |

### Tables

| Table               | Description                        |
|---------------------|------------------------------------|
| `users`             | Student accounts                   |
| `portfolio_setup`   | Portfolio config per user          |
| `trade_log`         | All buy/sell trades                |
| `holdings`          | Current stock holdings             |
| `investment_thesis` | Trade rationale submissions        |
| `thesis_scores`     | AI-scored thesis results           |
| `risk_metrics`      | Sharpe, beta, VaR per user         |
| `weekly_scores`     | Weekly score breakdown (100 pts)   |
| `leaderboard`       | Ranked leaderboard                 |
| `reports`           | Generated PDF report paths         |

---

## Backend (Flask API)

### Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env if needed (defaults work with docker compose)
```

### Start

```bash
python run.py
```

Runs on **http://localhost:5000**

### Environment variables (`.env`)

```
FLASK_ENV=development
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=tradeiq
DB_USER=root
DB_PASSWORD=
```

### API Endpoints

All endpoints except `/auth/register` and `/auth/login` require a JWT token:

```
Authorization: Bearer <token>
```

| Method | Route                          | Description                        |
|--------|--------------------------------|------------------------------------|
| POST   | `/auth/register`               | Register a new student             |
| POST   | `/auth/login`                  | Login, returns JWT token           |
| GET    | `/market/stock/<ticker>`       | Stock info (name, sector, beta)    |
| GET    | `/market/history/<ticker>`     | Price history + daily returns      |
| GET    | `/market/benchmark`            | S&P 500 benchmark data             |
| POST   | `/portfolio/trade`             | Execute buy/sell trade             |
| GET    | `/portfolio/holdings/<user_id>`| Current holdings                   |
| GET    | `/portfolio/summary/<user_id>` | Portfolio value and P&L            |
| GET    | `/analytics/scores/<user_id>`  | Full score breakdown               |
| GET    | `/analytics/leaderboard`       | Live leaderboard                   |

### Quick test

```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Your Name","email":"you@example.com","password":"secret123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"secret123"}'
```

---

## Frontend (Expo React Native)

### Setup

```bash
cd "frontend/DRA App"
npm install
```

### Start

```bash
# Web browser
npx expo start --web

# Android emulator
npx expo start --android

# iOS simulator
npx expo start --ios
```

Web runs on **http://localhost:8081**

### Tech stack

| Library              | Version  | Purpose                    |
|----------------------|----------|----------------------------|
| Expo                 | ~54.0.0  | React Native framework     |
| React Native         | 0.81.5   | Mobile UI                  |
| Expo Router          | ~6.0.15  | File-based navigation      |
| React Native Web     | ^0.21.0  | Web browser support        |
| Supabase JS          | ^2.107.0 | Auth / realtime (optional) |
| TypeScript           | ~5.9.2   | Type safety                |

---

## Running Everything

```bash
# 1. Start MySQL
docker compose up -d

# 2. Start Backend (new terminal)
cd backend
source venv/bin/activate
python run.py

# 3. Start Frontend (new terminal)
cd "frontend/DRA App"
npx expo start --web
```

| Service  | URL                      |
|----------|--------------------------|
| MySQL    | `localhost:3306`         |
| API      | http://localhost:5000    |
| Frontend | http://localhost:8081    |
