# TradeIQ Fixes & Remediation Report

This report is a standalone remediation plan for the current SalesTrading codebase.
It is written so a developer can understand what is wrong, why it matters, and exactly what to change without opening the source first.

## Executive Summary

| Feature | Severity | # of Risks | Estimated Fix Effort |
|---|---:|---:|---|
| User Registration and Login (JWT) | P0 | 5 | M |
| Secrets, Environment, and Runtime Config | P0 | 4 | M |
| Frontend Token Storage and API Logging | P0 | 4 | M |
| Database Engine Migration and Schema Integrity | P0 | 6 | L |
| Portfolio Trading and Holdings Reconciliation | P1 | 6 | L |
| Market Data and Search | P1 | 4 | M |
| Analytics, Scoring, and Leaderboard | P1 | 6 | L |
| API Contract Consistency and Validation | P2 | 5 | M |
| Containerization and Deployment Runtime | P2 | 4 | M |
| Caching, Background Jobs, and Observability | P3 | 5 | L |

## P0

### User Registration and Login (JWT)

#### Current Risks
- Passwords are hashed with SHA-256 in `backend/app/auth/routes.py` using `_hash_password()`, which is not a password hashing scheme and is too fast to resist offline cracking.
- Login compares `user.password_hash != _hash_password(password)` directly, which means there is no peppering, no adaptive work factor, and no migration path to stronger hashes.
- Registration issues a JWT immediately after creating the account, but the frontend stores that token in browser local storage or AsyncStorage in `frontend/DRA App/src/native/api.ts` and `frontend/DRA App/src/native/auth-store.ts`.
- There is no password reset, forgot-password, or email recovery path, so a user who loses access has no recovery workflow.
- `backend/app/auth/routes.py` generates user IDs with only four hex characters in `_make_user_id()`, which creates a small ID space and becomes collision-prone as the user count grows.

#### Severity Justification (Why P0)
- SHA-256 password hashing is a critical security flaw because any credential dump can be brute-forced much faster than with a memory-hard password hash. If one student password is exposed, the same password may be reused elsewhere.
- Direct string comparison of SHA-256 hashes is not the problem by itself; the real risk is that the hash algorithm is weak for password storage. The blast radius includes every account stored in the database.
- Storing JWTs in browser local storage is dangerous because any XSS bug in the frontend can expose the full session token. On native, AsyncStorage is not equivalent to an OS-backed secure enclave, so theft risk still exists on compromised devices or via debug builds.
- Missing password recovery creates a support and availability risk. If account access is lost, a student may be locked out permanently, which damages adoption and support burden.
- Short user IDs can collide, and collisions become a real operational issue if registration volume grows or if IDs are used in external reporting, URLs, or joins.

#### Exact Fix Instructions
1. Replace SHA-256 password hashing with Argon2.
2. Keep the stored password field long enough for the new hash format.
3. Add a `verify_password()` helper and use it during login.
4. Move JWT storage away from browser local storage and generic AsyncStorage.
5. Add password reset token creation, storage, expiry, and email delivery.
6. Increase user ID entropy or replace short custom IDs with a larger ID format.

Recommended hashing approach:
- Use `argon2-cffi` because Argon2id is memory-hard and is better suited to password storage than SHA-256 or plain bcrypt.
- If compatibility matters more than optimal resistance, bcrypt is acceptable, but Argon2 is the stronger default choice.

Before:

```python
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()
```

After:

```python
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

password_hasher = PasswordHasher()

def _hash_password(password: str) -> str:
    return password_hasher.hash(password)

def _verify_password(stored_hash: str, password: str) -> bool:
    try:
        return password_hasher.verify(stored_hash, password)
    except VerifyMismatchError:
        return False
```

Before:

```python
if not user or user.password_hash != _hash_password(password):
    return jsonify({"error": "Invalid email or password"}), 401
```

After:

```python
if not user or not _verify_password(user.password_hash, password):
    return jsonify({"error": "Invalid email or password"}), 401
```

Password reset workflow:
- Add a `password_reset_tokens` table with `user_id`, `token_hash`, `expires_at`, `used_at`, and `created_at`.
- Create a `/auth/forgot-password` endpoint that accepts an email address and always returns a neutral success response.
- Create a `/auth/reset-password` endpoint that accepts the token and new password.
- Email a one-time reset link containing a random token, but store only the token hash server-side.
- Expire the token after 15 to 60 minutes.
- Invalidate all prior login sessions after password change.

JWT storage approach:
- Use httpOnly, Secure, SameSite cookies for web if the frontend and backend can be deployed on compatible domains.
- For React Native, store only refresh credentials in a secure OS-backed store such as `expo-secure-store` or `react-native-keychain`.
- Keep the access token short-lived, for example 10 to 15 minutes, and rotate it through a refresh endpoint.
- Do not use browser local storage for long-lived authentication tokens if XSS is in scope.

User ID fix:
- Increase the random length from four hex characters to at least twelve or sixteen hex characters.
- Prefer a UUID or ULID if user IDs are exposed externally.

Suggested implementation sequence:
1. Add Argon2 hashing.
2. Add password reset tables and endpoints.
3. Replace token persistence.
4. Increase user ID entropy.
5. Add refresh token flow and optional email verification.

#### Optional Hardening (Nice-to-have, not blocking)
- Add email verification before account activation.
- Add login rate limiting per IP and per email.
- Add 2FA for admin or staff accounts.
- Add account lockout rules after repeated failed logins.
- Add password history checks to prevent immediate reuse.

#### Future Feature Recommendations
- Email verification to reduce fake or mistyped accounts.
- Refresh token rotation to reduce long-term token theft impact.
- Google OAuth to reduce password handling burden.
- 2FA for admins to protect high-privilege access.
- Audit logging for auth events to improve incident response.

#### Files/Modules Involved
- `backend/app/auth/routes.py` - replace SHA-256 hashing, add password reset endpoints, and upgrade account creation/login flow.
- `backend/app/models.py` - add password reset token model and widen `password_hash` storage if needed.
- `backend/migrations/schema.sql` - add password reset tables and update the password hash column size.
- `backend/app/__init__.py` - ensure JWT config and env-based secrets are loaded correctly.
- `frontend/DRA App/src/native/api.ts` - stop storing bearer tokens in local storage and centralize auth transport.
- `frontend/DRA App/src/native/auth-store.ts` - replace simple token persistence with secure storage and refresh handling.

#### Testing/Verification Checklist
- Register a user and confirm the stored password is an Argon2 hash, not SHA-256.
- Log in with a correct password and confirm token issuance still works.
- Log in with an incorrect password and confirm access is rejected.
- Request a password reset and confirm the server issues a one-time, expiring token.
- Reset the password with a valid token and confirm the old password no longer works.
- Verify the frontend no longer keeps a session token in browser local storage.
- Add unit tests for password hashing, token expiry, and login failure cases.

### Secrets, Environment, and Runtime Config

#### Current Risks
- The repository contains a checked-in `backend/.env` file with production-style database credentials and a remote TiDB host.
- The backend still depends on plain environment files for critical runtime settings, which means secrets can be copied, leaked, or deployed inconsistently if a secret manager is not introduced.
- `backend/config/settings.py` defines helper code for SSL/config behavior but does not enforce a complete secure configuration policy for production.
- The frontend has a hardcoded fallback backend URL in `frontend/DRA App/src/native/api.ts`.

#### Severity Justification (Why P0)
- Checked-in credentials are a system-wide incident if the repository is shared or leaked. The blast radius is full database access and possible account compromise.
- Hardcoded or stale runtime values cause deployment confusion and make it easy to point production traffic at the wrong database.
- A fallback backend URL that silently points to a hosted deployment can cause data leakage, incorrect environment targeting, or unpredictable cross-environment behavior.

#### Exact Fix Instructions
1. Remove all secrets from version-controlled files.
2. Keep only example defaults in `.env.example`.
3. Load every runtime secret from environment variables or a secret manager.
4. Split development, staging, and production settings.
5. Fail fast if a required production secret is missing.

Recommended config pattern:

```python
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
```

Rules for runtime config:
- Do not embed secrets in Python source.
- Do not keep real passwords in repository `.env` files.
- In production, source secrets from cloud secret storage.
- In development, keep a local `.env` that is excluded from version control.

Environment variables to define explicitly:
- `FLASK_ENV`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_SSL`
- `DB_SSL_VERIFY`
- `DB_SSL_CA`
- `REDIS_URL`
- `EXPO_PUBLIC_API_URL`

#### Optional Hardening (Nice-to-have, not blocking)
- Add startup validation that prints missing required variables.
- Split configuration into explicit `development`, `testing`, and `production` classes.
- Add secret rotation policy for production deployments.

#### Future Feature Recommendations
- Secret manager integration in GCP Secret Manager or AWS Secrets Manager.
- Configuration schema validation to catch bad deployments early.
- Automated checks that fail the build if a secret-like value is committed.

#### Files/Modules Involved
- `backend/.env` - remove real credentials and keep only safe local defaults.
- `backend/.env.example` - document every required variable without secrets.
- `backend/app/__init__.py` - build the SQLAlchemy URI from environment variables only.
- `backend/config/settings.py` - formalize environment-specific settings.
- `frontend/DRA App/src/native/api.ts` - remove hidden production fallback URLs or make them explicit per environment.
- `docker-compose.yml` - define service-local environment variables for container runs.

#### Testing/Verification Checklist
- Confirm no real secrets remain in tracked files.
- Start the backend with missing required variables and confirm it fails clearly.
- Start the backend with development variables and confirm it connects only to the intended database.
- Build the frontend in a staging-like environment and confirm the API base URL is correct.

### Frontend Token Storage and API Logging

#### Current Risks
- `frontend/DRA App/src/native/api.ts` stores JWTs in browser local storage when `window.localStorage` exists.
- `frontend/DRA App/src/native/auth-store.ts` stores user session state in `window.localStorage` on web and AsyncStorage on native, neither of which is an ideal secure token vault.
- `frontend/DRA App/src/native/api.ts` logs the API URL, HTTP status, response body, and fetch errors to the console.
- `frontend/DRA App/src/native/api.ts` keeps using bearer tokens automatically for every request once a token is available, which increases exposure if XSS or debugging leaks occur.

#### Severity Justification (Why P0)
- Local storage is a high-value target for XSS. If one injected script executes, the attacker can steal the token and act as the user.
- AsyncStorage is better than local storage for persistence, but it is still not a hardened secret store.
- Console logging full response bodies can leak sensitive data, including tokens on login responses, into browser logs and remote debugging sessions.

#### Exact Fix Instructions
1. Replace local storage token persistence with secure storage.
2. On web, use httpOnly cookies if the deployment allows cookie-based auth.
3. On native, use `expo-secure-store` or keychain-based storage.
4. Strip token and response logging from the production build.
5. Keep access tokens short-lived and rotate them with refresh tokens.

Recommended storage strategy:
- Web: httpOnly Secure SameSite cookies where domain architecture allows it.
- Native: OS-backed secure storage.
- Shared auth model: short-lived access token + refresh token rotation.

Before:

```typescript
if (typeof window !== "undefined" && window.localStorage) {
  window.localStorage.setItem(TOKEN_KEY, token);
}
```

After:

```typescript
import * as SecureStore from "expo-secure-store";

async function persistToken(token: string) {
  await SecureStore.setItemAsync(TOKEN_KEY, token);
}
```

Logging cleanup:
- Remove `console.log("API BASES = ...")`.
- Remove `console.log("API URL = ...")`.
- Remove `console.log("STATUS = ...")`.
- Remove `console.log("BODY = ...")`.
- Keep structured error logging only in non-production builds.

#### Optional Hardening (Nice-to-have, not blocking)
- Add token refresh preemption before expiry.
- Add device/session revocation in the backend.
- Add a dedicated logout endpoint that invalidates refresh tokens server-side.

#### Future Feature Recommendations
- Session management screen so users can revoke old devices.
- Login anomaly detection based on IP and device fingerprint changes.
- Secure analytics event logging that never prints tokens or PII.

#### Files/Modules Involved
- `frontend/DRA App/src/native/api.ts` - replace local storage auth persistence and remove token/body logs.
- `frontend/DRA App/src/native/auth-store.ts` - use secure storage for auth state and session refresh logic.
- `frontend/DRA App/src/native/constants.ts` - avoid embedding environment-sensitive behavior in global constants.
- `frontend/DRA App/src/native/types.ts` - adjust auth/session types if refresh tokens or session metadata are introduced.

#### Testing/Verification Checklist
- Sign in on web and confirm no JWT is stored in local storage.
- Sign in on native and confirm the token is stored in a secure store.
- Confirm production builds do not print response bodies or tokens to the console.
- Simulate an invalid token and confirm the user is cleanly signed out.

### Database Engine Migration and Schema Integrity

#### Current Risks
- The system is designed around a MySQL schema in `backend/migrations/schema.sql`, but the project now needs PostgreSQL.
- The schema file is used as a one-time bootstrap instead of a real migration system.
- The ORM model definitions in `backend/app/models.py` and the SQL schema are not perfectly aligned.
- Password hash storage is inconsistent: the schema uses a shorter `password_hash` column than a modern hash format may require.
- Some relationships and constraint behaviors are defined in SQL but not enforced consistently by application logic.
- The current development compose file still exposes the database through container-specific conventions that must change for PostgreSQL.

#### Severity Justification (Why P0)
- Database migration is a system-wide change. If it is done casually, it can corrupt user accounts, trades, holdings, and analytics history.
- Schema drift between ORM and SQL makes production failures likely when the database engine changes.
- A too-short password hash column can silently truncate stored hashes and break logins.

#### Exact Fix Instructions
1. Introduce PostgreSQL as the target database engine.
2. Replace the ad hoc schema bootstrap with migrations.
3. Reconcile every model in `backend/app/models.py` with the actual database schema.
4. Update the compose file to start PostgreSQL instead of MySQL.
5. Rework the database URL and driver to use PostgreSQL.
6. Verify all numeric, date, enum, and timestamp behaviors under PostgreSQL.

Recommended stack:
- Use PostgreSQL with `psycopg` or `psycopg2-binary`.
- Use Alembic via Flask-Migrate for schema migrations.
- Keep SQLAlchemy models as the source of truth for the ORM.

Before:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = _build_database_uri()
```

After:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{user}:{password}@{host}:{port}/{database}"
)
```

Schema migration rules:
- Never rely on a single `schema.sql` once the app is actively changing.
- Generate migration scripts for table creation, column changes, and constraints.
- Test migration up and down on a copy of production-like data.

PostgreSQL-specific design notes:
- Use `UUID` or longer string IDs where collisions matter.
- Use `CheckConstraint` for enum-like values if native enum management becomes cumbersome.
- Make sure `Numeric` precision matches the financial calculations used by the app.
- Use `TIMESTAMP WITH TIME ZONE` where cross-region deployment is expected.

#### Optional Hardening (Nice-to-have, not blocking)
- Add foreign key indexes where query volume is high.
- Add unique constraints for invariants such as one active portfolio setup per user.
- Add soft-delete flags for audit-heavy tables if the business needs retention.

#### Future Feature Recommendations
- Database backups and point-in-time recovery.
- Read replicas once analytics traffic grows.
- Logical migration checks in CI to catch schema drift.

#### Files/Modules Involved
- `backend/app/models.py` - align every model type, relationship, and constraint with PostgreSQL behavior.
- `backend/migrations/schema.sql` - replace with or deprecate in favor of versioned migrations.
- `backend/app/__init__.py` - switch SQLAlchemy URI and engine options to PostgreSQL.
- `backend/requirements.txt` - add the PostgreSQL driver and migration tooling.
- `docker-compose.yml` - run a PostgreSQL container for local development.
- `SETUP.md` - document the new DB host, port, and migration workflow.

#### Testing/Verification Checklist
- Create a fresh PostgreSQL database and apply the schema from migrations.
- Register a user, create a portfolio, and confirm rows are written correctly.
- Run buy and sell trades and verify the financial fields are preserved with correct precision.
- Confirm password hashes are stored fully without truncation.
- Drop and recreate the database and confirm migrations restore the schema cleanly.

## P1

### Portfolio Trading and Holdings Reconciliation

#### Current Risks
- `backend/app/portfolio/routes.py` updates cash balance, trade history, and holdings inside request handlers without an explicit transaction boundary or lock strategy.
- `_update_holding()` recalculates quantity and average buy price in application code, which is vulnerable to race conditions if two trades are submitted close together.
- `delete_holding()` deletes the holding and then deletes all trade log rows for that ticker and user, which destroys audit history.
- The buy path trusts submitted values such as `amount_invested`, `buy_price`, and `current_sell_price` if they are present, which can let client-supplied numbers shape calculations.
- The sell path assumes the portfolio and holdings are already in a consistent state and only checks a subset of invariants.
- Holdings and trade rows are updated using float conversions around values that are stored as `Numeric`, which increases rounding drift over time.

#### Severity Justification (Why P1)
- Trading and portfolio state are the core business records of the platform. If a trade is wrong, the leaderboard, analytics, and user trust all become unreliable.
- A race condition can let two simultaneous buys overspend cash or create an inconsistent average cost.
- Deleting trade logs removes the audit trail, making support investigations and score review impossible.

#### Exact Fix Instructions
1. Wrap the full trade execution flow in a database transaction.
2. Lock the user portfolio row while updating cash and holdings.
3. Recalculate holdings from persisted trades rather than trusting client-supplied money values.
4. Keep the trade log immutable.
5. Change delete-holding behavior to a soft close or a special administrative action, not a full history wipe.
6. Use decimal-safe arithmetic and avoid converting values to float until response serialization.

Recommended refactor:
- Put trade validation in a service layer.
- Use one function to compute position cost, quantity, and average price.
- Use another function to sync holding state from the latest trades.

Safer trade flow:

```python
with db.session.begin():
    portfolio = PortfolioSetup.query.filter_by(user_id=user_id).with_for_update().first()
    holding = Holding.query.filter_by(user_id=user_id, stock_ticker=ticker).with_for_update().first()
    # validate
    # compute
    # write TradeLog
    # update Holding
    # update cash_balance
```

Delete handling:
- Do not delete historical trade rows when a user removes a holding.
- If a clean-up action is needed, mark the holding as closed or archived.
- Preserve trade history for audits and score calculations.

Validation rules to add:
- Reject negative or zero quantities.
- Reject buy amounts greater than available cash.
- Reject sell quantities greater than the active quantity.
- Reject any request that tries to bypass allocation caps.

#### Optional Hardening (Nice-to-have, not blocking)
- Add per-user trade idempotency keys to prevent duplicate submissions.
- Add price slippage rules for market realism.
- Add a reconciliation job that compares holdings against trade history.

#### Future Feature Recommendations
- Trade audit trail viewer.
- Admin override workflow for fixing broken trades.
- Real-time notifications when a trade is executed.

#### Files/Modules Involved
- `backend/app/portfolio/routes.py` - move trade execution into a transaction-safe service and stop deleting trade logs.
- `backend/app/models.py` - add status fields if holdings need soft-close behavior.
- `backend/app/scoring/*` - ensure score calculations only read stable holding data.

#### Testing/Verification Checklist
- Execute two trades at the same time for the same user and confirm cash and quantity stay consistent.
- Buy a stock and confirm the average cost is correct.
- Sell part of a holding and confirm the remaining quantity and cash update correctly.
- Delete or close a holding and confirm the trade history remains intact.
- Add integration tests for over-allocation, oversell, and duplicate submission cases.

### Market Data and Search

#### Current Risks
- `backend/app/market/pipeline.py` depends on Yahoo Finance for prices, metadata, history, and benchmark data.
- The market endpoints swallow exceptions broadly and often return generic errors or empty data.
- `backend/app/market/routes.py` has no request-level retry or fallback policy for external data failures.
- The indices cache in `backend/app/market/routes.py` is an in-memory process-local cache, so it does not synchronize across backend instances.
- `search_stocks()` returns a generic result set without a persisted symbol master or internal validation layer.

#### Severity Justification (Why P1)
- Market data is a user-visible dependency for trading and portfolio calculations. If it fails, users cannot price positions or understand P&L.
- A process-local cache is fine for one process, but it becomes inconsistent and misleading when scaled horizontally.
- Broad exception handling makes it difficult to distinguish real data absence from network failure.

#### Exact Fix Instructions
1. Add structured retry and timeout behavior to market fetches.
2. Define fallback responses for price and metadata fetch failures.
3. Move the indices cache to Redis if available.
4. Validate date ranges and ticker formats before calling the external provider.
5. Add a local market symbol table if search traffic becomes important.

Better implementation pattern:
- Keep `YahooFinancePipeline` for provider access.
- Add an adapter service that normalizes error handling and caching.
- Return explicit error codes for malformed input versus provider failure.

Validation rules:
- `start` and `end` must be real dates.
- `start` must be earlier than `end`.
- Tickers must be normalized before external lookup.

#### Optional Hardening (Nice-to-have, not blocking)
- Add background refresh for popular market symbols.
- Cache historical responses by ticker and date range.
- Add provider health checks and circuit-breaking logic.

#### Future Feature Recommendations
- Redis-backed market cache.
- Multi-provider fallback for prices.
- Symbol search autocomplete backed by a local index.

#### Files/Modules Involved
- `backend/app/market/pipeline.py` - add stricter provider error handling and normalization.
- `backend/app/market/routes.py` - validate inputs, use shared caching, and return explicit provider failures.
- `backend/app/cache.py` - move cache storage into Redis in production.

#### Testing/Verification Checklist
- Request a valid ticker and confirm metadata and price data return correctly.
- Request an invalid ticker and confirm the error is explicit and stable.
- Request history with reversed dates and confirm validation fails.
- Run two backend instances and confirm shared cache behavior is consistent once Redis is enabled.

### Analytics, Scoring, and Leaderboard

#### Current Risks
- `backend/app/analytics/routes.py` computes scores synchronously during request handling, which is expensive and slow.
- The analytics flow can call external AI services via the OpenAI API when `OPENAI_API_KEY` is present, so scoring becomes dependent on an external service and on prompt payloads that include portfolio data and thesis text.
- `_leaderboard_cache` is in-memory and process-local, so leaderboard refreshes are not shared across instances.
- `WeeklyScore` and `Leaderboard` rows are recalculated in application code during user requests, which can block the response path.
- Some score logic depends on the current shape of `TradeLog`, `Holding`, and `PortfolioSetup`, so schema drift or inconsistent portfolio state can corrupt scoring outputs.
- Ownership checks are inconsistent across analytics endpoints: some routes enforce owner-or-admin access, while others such as risk retrieval and legacy compute paths do not apply the same explicit guard.

#### Severity Justification (Why P1)
- Analytics are business-critical because they drive leaderboard position and assessment outcomes. Incorrect scores can change rankings and user trust.
- External AI scoring can become slow, unavailable, or expensive. If it fails during peak use, leaderboard requests may time out.
- In-memory caching breaks under multiple workers or containers, causing inconsistent views of rankings.

#### Exact Fix Instructions
1. Move recomputation out of the request path for heavy operations.
2. Use a background job queue for full scoring and leaderboard refreshes.
3. Store leaderboard cache in Redis or another shared store.
4. Separate score calculation from score persistence.
5. Add a clear policy for when external AI is allowed, when local scoring is used, and how failures are handled.
6. Add authorization checks so users can only access their own detailed scores unless the caller has a privileged role.

Recommended architecture:
- Request handler enqueues a scoring job.
- Worker calculates score and writes `WeeklyScore` and `Leaderboard`.
- Request handler returns the last available score or job status.

External AI policy:
- Keep local rubric scoring as the fallback.
- Only call external AI when the key is present and the feature is intentionally enabled.
- Never let one AI timeout block the entire dashboard.

Authorization policy:
- Add explicit ownership checks for `/analytics/scores/<user_id>`.
- Add admin-only access if cross-user review is needed.

#### Optional Hardening (Nice-to-have, not blocking)
- Add score recalculation versioning so future rubric updates are traceable.
- Add audit records for score overrides or manual corrections.
- Add anomaly detection for unrealistic score jumps.

#### Future Feature Recommendations
- Job queue with Celery or RQ.
- Redis leaderboard cache.
- Admin review dashboard for disputed scores.

#### Files/Modules Involved
- `backend/app/analytics/routes.py` - separate request handling from recomputation and add ownership checks.
- `backend/app/scoring/*` - keep scoring formulas in isolated modules with tests.
- `backend/app/jobs.py` - use the job helper for asynchronous score refreshes.
- `backend/app/cache.py` - share leaderboard cache across instances.

#### Testing/Verification Checklist
- Recompute a user score and confirm it no longer blocks normal request handling.
- Simulate OpenAI failure and confirm local fallback scoring still works.
- Confirm one user cannot fetch another user’s private score unless authorized.
- Verify the leaderboard is the same across workers once shared cache is enabled.

## P2

### API Contract Consistency and Validation

#### Current Risks
- Frontend types in `frontend/DRA App/src/native/types.ts` and `frontend/DRA App/src/native/api.ts` do not perfectly match backend model fields.
- The frontend assumes some fields such as `course`, `participation_type`, and `team_name`, while the backend user model uses `university`, `year_of_study`, and other fields instead.
- Several backend endpoints rely on loosely validated JSON bodies and convert types manually inside route handlers.
- Some error responses are JSON with an `error` key while others may vary by endpoint, which complicates frontend handling.
- Query parameters such as dates and ticker values are accepted without a shared schema contract.

#### Severity Justification (Why P2)
- Contract drift does not necessarily break the whole system immediately, but it causes subtle frontend bugs, rejected requests, and inconsistent UI state.
- Weak validation increases the chance of bad data entering the database and breaking analytics later.

#### Exact Fix Instructions
1. Create a shared request/response schema contract.
2. Validate every inbound request body at the boundary.
3. Standardize error response structure across all endpoints.
4. Align frontend TypeScript types with the actual backend payloads.
5. Remove assumptions about fields that the backend never returns.

Recommended tools:
- `pydantic` or `marshmallow` for request validation.
- `Flask-Smorest` if the team wants schema-driven route documentation.
- TypeScript interfaces generated or manually aligned with backend DTOs.

#### Optional Hardening (Nice-to-have, not blocking)
- Publish an OpenAPI spec.
- Generate API clients from schema definitions.
- Add contract tests between frontend and backend.

#### Future Feature Recommendations
- Schema versioning for future API changes.
- Shared DTO layer or generated client types.

#### Files/Modules Involved
- `backend/app/auth/routes.py` - validate register and login payloads explicitly.
- `backend/app/portfolio/routes.py` - validate trade, holdings, and summary parameters.
- `backend/app/market/routes.py` - validate tickers and dates using shared validators.
- `frontend/DRA App/src/native/api.ts` - align request and response typing with backend payloads.
- `frontend/DRA App/src/native/types.ts` - remove fields that do not exist in the backend response model.

#### Testing/Verification Checklist
- Send malformed payloads to each endpoint and confirm the same style of validation error is returned.
- Run the frontend against the backend and confirm type mismatches are eliminated.
- Add schema tests for all public request payloads.

### Containerization and Deployment Runtime

#### Current Risks
- `docker-compose.yml` is built around a MySQL service and a backend service that expects local container networking behavior.
- The frontend container currently points to a hosted deployment URL rather than a coordinated local environment URL.
- The backend entrypoint waits for the database but depends on a specific host and port setup.
- Deployment guidance is split between README and setup docs, which makes it easy for the team to follow the wrong instructions.

#### Severity Justification (Why P2)
- These problems do not directly corrupt data, but they create failed deployments, confusion, and inconsistent environments.

#### Exact Fix Instructions
1. Rewrite compose to target PostgreSQL for local development.
2. Make frontend environment selection explicit per environment.
3. Ensure the backend container reads the correct DB host from compose.
4. Consolidate deployment instructions into one canonical document.

#### Optional Hardening (Nice-to-have, not blocking)
- Add a healthcheck to every container.
- Add explicit build targets for development and production images.

#### Future Feature Recommendations
- Separate compose overlays for development and production.
- Infrastructure-as-code for cloud deployment.

#### Files/Modules Involved
- `docker-compose.yml` - update the database service and frontend API URL strategy.
- `backend/entrypoint.sh` - keep startup waits aligned with the new database engine.
- `README.md` - make the local and production workflows unambiguous.
- `SETUP.md` - document the PostgreSQL flow and deployment differences.

#### Testing/Verification Checklist
- Start the full stack locally and confirm all services come up in the right order.
- Confirm the frontend talks to the intended backend URL in each environment.
- Confirm the backend waits for the database service successfully.

## P3

### Caching, Background Jobs, and Observability

#### Current Risks
- `backend/app/cache.py` falls back to process memory when Redis is unavailable, so cache state is not shared across workers or containers.
- `backend/app/jobs.py` uses a local `ThreadPoolExecutor`, which does not survive process restarts and does not provide durable job status.
- Logging is mostly ad hoc and request-level observability is limited.
- There are no formal metrics, alerts, or tracing hooks in the app runtime.
- The system lacks a documented backup and restore practice for the database.

#### Severity Justification (Why P3)
- These gaps do not block basic functionality, but they become expensive once the app has real users or more than one backend instance.

#### Exact Fix Instructions
1. Use Redis as the shared cache backend in production.
2. Replace threadpool jobs with a real queue if background work becomes business-critical.
3. Add structured logs with request identifiers.
4. Add health, readiness, and liveness checks.
5. Define database backup and restore procedures.

#### Optional Hardening (Nice-to-have, not blocking)
- Add metrics for trade latency, login failures, cache hit rate, and score job duration.
- Add distributed tracing if the backend gets split into more services.

#### Future Feature Recommendations
- Central logging in Cloud Logging, CloudWatch, or a similar platform.
- Alerting for auth failures, database latency, and market data outages.
- Job dashboards for queue length and failed scoring tasks.

#### Files/Modules Involved
- `backend/app/cache.py` - route cache storage through Redis.
- `backend/app/jobs.py` - replace the thread pool with a durable queue when needed.
- `backend/app/__init__.py` - add health and readiness endpoints if deployed behind an orchestrator.
- `backend/entrypoint.sh` - keep startup logs clean and production-safe.

#### Testing/Verification Checklist
- Confirm cache entries are shared between two backend instances.
- Confirm background jobs survive process restarts once a real queue is introduced.
- Confirm logs contain request context without leaking secrets.
- Confirm health checks behave correctly under startup and failure conditions.

## Suggested Fix Order

1. Remove secret exposure and unsafe auth storage.
2. Upgrade password hashing and add password recovery.
3. Move the backend and local development stack to PostgreSQL.
4. Add migrations and align schema with models.
5. Fix trade transaction safety and preserve audit history.
6. Stabilize market data failure handling and caching.
7. Move scoring and leaderboard refreshes out of the request path.
8. Standardize API validation and response shapes.
9. Harden Docker and deployment configuration.
10. Add Redis, background jobs, observability, and backup procedures.
