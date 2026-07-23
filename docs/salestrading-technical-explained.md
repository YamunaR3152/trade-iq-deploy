# SalesTrading Explained in Simple Words

This document explains the SalesTrading project in plain language. It is written for someone who does not know the system yet and wants to understand what the project is, how it works, and why each part exists.

## 1. What This Project Is

SalesTrading is a student trading simulation platform.

In simple words, it is an app where users:
- create an account
- log in
- search stocks
- see stock prices and historical data
- buy or sell simulated stocks
- track their portfolio
- submit investment reasoning
- get scored
- see a leaderboard

The idea is to give students a realistic trading and investing experience without using real money.

## 2. Why This Project Exists

This project is useful because it simulates how a trading desk or investment challenge works.

It helps users practice:
- stock selection
- portfolio building
- risk awareness
- writing investment reasoning
- understanding performance
- comparing against others

So when we say this project to a user, we can explain it like this:

"SalesTrading is a learning and competition platform where users simulate trades, manage a portfolio, and get scored on performance and decision-making."

## 3. Main Parts of the System

The project has three big parts:

- Frontend
- Backend
- Database

### Frontend
The frontend is the screen the user sees.

It shows:
- login and registration pages
- stock search
- trade pages
- portfolio summary
- scores and leaderboard

It is built with Expo and React Native, and the web version is hosted on Vercel.

### Backend
The backend is the brain of the app.

It does things like:
- check login credentials
- save trades
- calculate portfolio values
- fetch stock prices
- compute scores
- return data to the frontend

It is built with Flask in Python.

### Database
The database stores all important data permanently.

It keeps:
- users
- trades
- holdings
- scores
- portfolio details
- reports

Without the database, the app would forget everything when it closes.

## 4. How the App Works End to End

Here is the flow in simple terms:

1. A user opens the frontend.
2. The frontend sends a request to the backend.
3. The backend checks if the user is allowed to do that action.
4. The backend reads or writes data in the database.
5. If needed, the backend also pulls market data from Yahoo Finance.
6. The backend sends the response back to the frontend.
7. The frontend shows the result to the user.

Example:
- A user buys a stock.
- The frontend sends the buy request.
- The backend checks the price and the cash balance.
- The backend saves the trade.
- The backend updates the holdings and portfolio.
- The frontend shows the updated portfolio.

## 5. Product Goals

The project tries to achieve these goals:

- let users register and log in safely
- allow users to trade simulated stocks
- keep track of the portfolio
- show performance clearly
- score the user on trading quality
- support competition and leaderboards

These goals are the reason the project has authentication, trading, analytics, and score calculation.

## 6. Technology Stack in Simple Words

### Expo
Expo helps build the frontend app quickly using React Native.

### React Native
React Native lets the same code work like a web app and mobile-style app.

### TypeScript
TypeScript is used so the frontend code is less error-prone.

### Flask
Flask is a Python web framework used to build the backend API.

### SQLAlchemy
SQLAlchemy helps the backend talk to the database in a clean way.

### PyMySQL
PyMySQL is the connector that lets Python talk to a MySQL-style database.

### Gunicorn
Gunicorn runs the Flask app properly in production.

### yfinance
yfinance is used to fetch stock and market data from Yahoo Finance.

### Docker
Docker helps run the backend and database locally in containers.

### Vercel
Vercel hosts the frontend on the web.

### Render or AWS
These can host the backend service.

### TiDB Cloud or MySQL
This hosts the database in production.

## 7. Why We Use These Tools

We use these tools because:

- Expo and React Native make the frontend easier to manage
- Flask is lightweight and good for API work
- SQLAlchemy makes database code cleaner
- MySQL-compatible databases are good for structured trading data
- yfinance gives access to live market data without building a market engine from scratch
- Docker makes local setup easier
- Vercel makes frontend deployment simple
- Render or AWS can host the backend reliably

## 8. Frontend Explained

The frontend is the user-facing part of SalesTrading.

It is responsible for:
- showing screens
- collecting user input
- displaying stock data
- showing the portfolio
- showing scores and leaderboard data

### Why it matters
Without the frontend, the user would have no interface to interact with the system.

### How it connects to the backend
The frontend sends API requests to the backend using a backend URL stored in `EXPO_PUBLIC_API_URL`.

That means the frontend does not store business logic. It just sends and receives data.

## 9. Backend Explained

The backend is where the important logic happens.

It is responsible for:
- logging users in and out
- checking tokens
- saving trade data
- calculating results
- fetching market data
- computing scores
- returning JSON responses

### Why it matters
The backend protects the rules of the app.

For example:
- the frontend cannot directly decide a trade result
- the backend must validate the request
- the backend checks cash, holdings, and portfolio rules

## 10. What Backend Modules Are

Backend modules are smaller folders inside the backend, each with a special job.

### `auth`
This module handles login and registration.

Why it exists:
- users need accounts
- the app needs to verify identity
- JWT tokens are created here

### `market`
This module handles stock and market data.

Why it exists:
- users need live prices
- users need stock search
- users need historical market data
- users need benchmark data

### `portfolio`
This module handles trading and holdings.

Why it exists:
- when a user buys or sells, the app must update the portfolio
- holdings must be saved
- cash balance must change
- portfolio summary must be calculated

### `analytics`
This module handles scoring and leaderboard work.

Why it exists:
- the app needs to score users
- it needs weekly score snapshots
- it needs to rank users on a leaderboard

### `scoring`
This module contains the actual scoring formulas.

Why it exists:
- keeps score rules separate from API routes
- makes the code easier to maintain

### `cache.py`
This is used for temporary storage of data that is expensive to calculate again.

Why it exists:
- reduces repeated work
- improves speed
- can use Redis when available

### `jobs.py`
This is a lightweight helper for background work.

Why it exists:
- some tasks should not block the user request
- heavy tasks can be moved off the main API path later

## 11. What the API Routes Are For

API routes are the URLs the frontend calls.

Think of them as service doors.

### Authentication routes
- `/auth/register` creates a user
- `/auth/login` logs a user in

Why they exist:
- every app with accounts needs a way to create and verify users

### Market routes
- `/market/stock/<ticker>` gets stock information
- `/market/history/<ticker>` gets historical prices
- `/market/benchmark` gets benchmark index data
- `/market/price/<ticker>` gets the current price
- `/market/indices` shows a list of tracked indices and large stocks
- `/market/search` helps search stocks

Why they exist:
- users need market data before making trade decisions

### Portfolio routes
- `/portfolio/trade` places a buy or sell order
- `/portfolio/holdings/<user_id>` shows current holdings
- `/portfolio/summary/<user_id>` shows total portfolio value and returns
- `/portfolio/trades/<user_id>` shows trade history

Why they exist:
- these are the core trading features of the app

### Analytics routes
- `/analytics/leaderboard` shows rankings
- `/analytics/scores/<user_id>` shows score breakdown
- `/analytics/compute/<user_id>` computes and saves scores
- `/analytics/compute-legacy/<user_id>` is an older scoring flow
- `/analytics/risk/<user_id>` returns risk metrics

Why they exist:
- the app is not just for trading
- it also evaluates user performance

### Health route
- `/health` checks if the backend is alive

Why it exists:
- hosting platforms use it to see if the app is healthy
- it helps with debugging

## 12. Database Tables in Simple Words

The database tables are like separate sheets in a notebook.

Each table stores one kind of information.

### `users`
Stores user account details.

Why:
- the app needs to know who the user is

### `portfolio_setup`
Stores the starting portfolio settings for a user.

Why:
- each user needs an initial capital amount and portfolio setup

### `trade_log`
Stores every buy and sell action.

Why:
- users need a history of all their trades
- scores and portfolio changes depend on these trades

### `holdings`
Stores what the user currently owns.

Why:
- the app needs to know open positions
- portfolio value depends on it

### `investment_thesis`
Stores the reason a user gave for making a trade.

Why:
- the platform scores the quality of reasoning, not just the result

### `thesis_scores`
Stores the score for a thesis.

Why:
- the app needs to record how good the reasoning was

### `risk_metrics`
Stores risk calculations.

Why:
- the app wants to measure whether the user is too risky or too concentrated

### `weekly_scores`
Stores scores by week.

Why:
- rankings are updated weekly
- the app needs past score history

### `leaderboard`
Stores ranking information.

Why:
- the app needs to compare users and sort them by score

### `reports`
Stores references to generated reports.

Why:
- if the app creates downloadable reports, the file path must be saved

## 13. Why the Tables Are Designed This Way

The tables are split by purpose so the data stays organized.

For example:
- user info is in one table
- trade history is in another table
- scores are in separate tables

This is done because:
- it avoids mixing unrelated data
- it makes queries clearer
- it makes updates safer
- it keeps the database structured

## 14. How Trading Works

When a user buys or sells a stock:

1. The frontend sends the trade request.
2. The backend checks the user token.
3. The backend fetches the latest price.
4. The backend checks if the user has enough cash or holdings.
5. The backend saves the trade.
6. The backend updates the holdings table.
7. The backend updates the cash balance.
8. The frontend shows the result.

Why this is important:
- it ensures trades are valid
- it keeps the portfolio accurate
- it prevents fake or invalid orders

## 15. How Portfolio Summary Works

The portfolio summary shows:
- total capital
- cash balance
- holdings value
- total portfolio value
- total profit or loss
- return percentage

Why it exists:
- users need to know how well their portfolio is doing
- it is one of the main views of the app

How it is calculated:
- backend reads the cash balance
- backend reads the holdings
- backend gets live prices
- backend adds everything together

## 16. How Analytics and Scores Work

The analytics section is the “evaluation” part of the system.

It gives users scores based on:
- portfolio performance
- risk management
- thesis quality
- execution quality
- strategy quality

Why it exists:
- the platform is not only about trading
- it is also about learning and judging decision quality

### Leaderboard
The leaderboard ranks users.

Why it exists:
- users can compare themselves to others
- competitions need rankings

### Weekly scores
Scores are stored per week.

Why:
- the app may score users repeatedly over time
- weekly history helps track performance trends

## 17. Why yfinance Is Used

yfinance is used to pull stock and market data from Yahoo Finance.

Why we use it:
- it is fast to integrate
- it gives stock prices and histories
- it avoids building a market data pipeline from scratch

What it is used for:
- current stock price
- historical data
- benchmark data
- index snapshots

Limitations:
- it depends on an external service
- responses can sometimes be slow
- data availability is not fully under our control

## 18. Why Caching Is Used

Caching means storing data temporarily so we do not calculate it again every time.

Why:
- faster responses
- lower load on external data sources
- better performance

In this project:
- market indices can be cached
- Redis can be used if available
- otherwise the app falls back to memory cache

Why Redis matters:
- memory cache only works inside one running server
- Redis can be shared across many backend instances

## 19. Why Environment Variables Are Used

Environment variables are used for secrets and deployment settings.

Why:
- secrets should not be hardcoded in code
- different environments need different values
- production should be safer than development

Examples:
- database host
- database password
- JWT secret
- frontend API URL

## 20. Why SSL/TLS Is Used for the Database

SSL/TLS protects the data sent between the backend and the database.

Why:
- stops traffic from being read in plain text
- protects credentials and data in transit
- is important for production databases

## 21. Why Gunicorn Is Used

Gunicorn is the production server for the Flask app.

Why:
- Flask’s built-in server is only for development
- Gunicorn is more stable for real hosting
- it can run multiple workers

## 22. Why Docker Is Used

Docker packages the app and database setup into containers.

Why:
- makes local setup easier
- keeps environments consistent
- helps move from local to cloud more easily

## 23. Why Vercel Is Used

Vercel hosts the frontend.

Why:
- easy deployment
- good for web apps
- works well with Git-based deploys
- handles frontend hosting cleanly

## 24. Why Render or AWS Are Used

These are used for the backend because the backend needs a server that stays running and handles API requests.

Why:
- frontend hosting alone is not enough
- backend needs a web service
- cloud hosting is needed for public access

## 25. Why TiDB Cloud or MySQL Is Used

The database needs to store structured records like users, trades, and scores.

Why:
- relational data fits this app well
- MySQL-compatible databases are common and reliable
- TiDB Cloud works with MySQL-style connections

## 26. Security in Simple Words

Security means protecting the app, users, and data.

What security does here:
- verifies user identity
- limits access using JWT
- protects database traffic with SSL/TLS
- stores secrets outside the code

What still needs improvement:
- stronger password hashing
- stricter CORS rules
- better audit logs
- more production security controls

## 27. Scaling in Simple Words

Scaling means making the app able to handle more users and more traffic.

What exists now:
- a working backend
- a working database
- basic caching

What is still missing for large scale:
- load balancing
- autoscaling
- distributed cache
- queue workers
- backups and failover
- observability

Why this matters:
- a small app can run on one server
- a large app needs more infrastructure

## 28. Observability in Simple Words

Observability means being able to see what the system is doing.

It includes:
- logs
- alerts
- uptime checks
- performance tracking
- error monitoring

Why it matters:
- helps find problems quickly
- helps understand app behavior
- helps with production support

## 29. Known Gaps

This project is functional, but not perfect.

Some gaps are:
- password hashing should be stronger
- rate limiting is optional, not fully enforced everywhere
- cache fallback is still local-only if Redis is not used
- background jobs are not fully implemented
- scaling architecture is not fully complete

## 30. Future Improvements

If the project grows, these are the next upgrades:
- use bcrypt or Argon2 for passwords
- add Redis for shared cache
- add Celery or RQ for background jobs
- add stronger monitoring and logs
- add role-based access control
- add API rate limiting
- add better deployment automation
- add test coverage for all main flows

## 31. Final Simple Summary

SalesTrading is a simulated trading and investment learning platform.

In simple words:
- users sign up
- they trade virtual stocks
- the app tracks their portfolio
- the app scores them
- the app ranks them on a leaderboard

The frontend is the visible interface, the backend does the logic, and the database stores everything. The project already works as a complete app, but if it needs to serve many users in production, it still needs stronger security, caching, monitoring, and scaling support.

