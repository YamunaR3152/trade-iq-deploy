# TradeIQ Fix Roadmap

This document is the implementation roadmap for the current SalesTrading project.
It is intentionally detailed so the team can use it as the primary working reference while fixing the system.

The goal is not to rewrite everything blindly.
The goal is to stabilize what already exists, move the backend onto PostgreSQL, fix the known problem areas, and prepare the system for production and scale without breaking the frontend contract more than necessary.

## Core Decision

### Recommended path

Use an incremental backend rebuild inside this repository instead of a total restart.

Why this is the better path:

1. The frontend already depends on a working API shape.
2. The business logic already exists in the current backend.
3. The scoring, portfolio, and market flows are valuable and expensive to rediscover from scratch.
4. A full rewrite usually takes longer than expected and introduces new bugs while solving old ones.

### When a full rewrite would make sense

Only choose a clean-slate backend if at least one of these is true:

1. The current API contract is too broken to preserve.
2. The current backend logic is impossible to untangle safely.
3. The project needs a new domain model that is fundamentally different from the current one.
4. The team has enough time to rebuild, retest, and re-integrate every frontend flow.

### Practical recommendation

Keep the frontend contract stable, replace the backend storage and security foundations first, then refactor the business logic into cleaner layers.

---

## Phase 0: Inventory and Freeze

### Goal

Build a complete map of the current system before changing behavior.

This phase prevents accidental breakage by making the current application understandable in one place.

### Why this phase comes first

If you change auth, database, scoring, and deployment without a full inventory, you will miss hidden dependencies and break the frontend in ways that are difficult to trace.

### What to inventory

#### Backend routes

List every API endpoint and note:

- HTTP method
- route path
- auth requirement
- request payload
- response payload
- database tables touched
- external services called
- whether the endpoint is used by the frontend

Primary files:

- `backend/app/auth/routes.py`
- `backend/app/market/routes.py`
- `backend/app/portfolio/routes.py`
- `backend/app/analytics/routes.py`

#### Database tables

List every table and note:

- table purpose
- primary key
- foreign keys
- nullable fields
- default values
- whether the frontend reads or writes the data
- which backend file writes it
- which backend file reads it

Primary files:

- `backend/app/models.py`
- `backend/migrations/schema.sql`

#### Frontend API usage

List every frontend call and note:

- exact endpoint called
- whether it sends a bearer token
- whether it reads auth state from storage
- whether it depends on local or production URLs

Primary files:

- `frontend/DRA App/src/native/api.ts`
- `frontend/DRA App/src/native/auth-store.ts`
- `frontend/DRA App/src/native/types.ts`

#### Runtime configuration

List every runtime setting currently used by:

- Flask
- JWT
- database
- CORS
- cache
- external scoring services
- frontend API base URL

Primary files:

- `backend/.env`
- `backend/.env.example`
- `backend/app/__init__.py`
- `backend/config/settings.py`
- `docker-compose.yml`

### Deliverables for this phase

1. An API inventory document.
2. A database table map.
3. A frontend-to-backend endpoint map.
4. A list of risky configuration values.
5. A list of endpoints that are clearly broken, stale, or duplicated.

### Exit criteria

Do not start refactoring until you can answer these questions:

- Which endpoints are used by the frontend today?
- Which routes are still legacy or duplicate paths?
- Which tables contain the source of truth for each feature?
- Which values are hardcoded and should move to environment variables?

---

## Phase 1: Security and Runtime Stabilization

### Goal

Stop the backend from being unsafe, confusing, or environment-dependent.

This phase is about making the current code predictable and safe enough to keep building on.

### Problems to fix

#### 1. Hardcoded runtime configuration

The backend must not depend on hardcoded database credentials or hidden production URLs.

What to change:

- Load secrets from environment variables.
- Remove hardcoded database URLs from Python source.
- Make development, staging, and production settings explicit.

Files:

- `backend/app/__init__.py`
- `backend/config/settings.py`
- `backend/.env`
- `backend/.env.example`

#### 2. Weak password hashing

Passwords should not be hashed with SHA-256.

What to change:

- Replace SHA-256 with Argon2id or bcrypt.
- Add a verification helper.
- Keep the stored password field wide enough for the new hash format.

Files:

- `backend/app/auth/routes.py`
- `backend/app/models.py`
- `backend/migrations/schema.sql`

#### 3. Unsafe frontend token storage

Bearer tokens should not be left in browser local storage if XSS is a realistic threat.

What to change:

- Use httpOnly cookies on web if the deployment supports them.
- Use secure OS-backed storage on native if the platform supports it.
- Introduce a refresh token flow if the app needs longer sessions.

Files:

- `frontend/DRA App/src/native/api.ts`
- `frontend/DRA App/src/native/auth-store.ts`

#### 4. Overly permissive CORS

Open CORS is convenient for development but too loose for production.

What to change:

- Restrict allowed origins to the actual frontend domains.
- Separate local dev origins from production domains.

Files:

- `backend/app/__init__.py`
- `backend/config/settings.py`

#### 5. Weak operational visibility

The backend needs clearer startup behavior and logging.

What to change:

- Ensure startup fails loudly when required settings are missing.
- Add structured request and error logging.
- Make the health endpoint reflect the actual app state clearly.

Files:

- `backend/entrypoint.sh`
- `backend/app/__init__.py`
- `backend/app/extensions.py`

### Implementation order inside this phase

1. Move all runtime config into environment variables.
2. Replace password hashing.
3. Fix token storage strategy.
4. Restrict CORS.
5. Improve startup logging and health checks.

### Acceptance criteria

This phase is done when:

- no real secrets remain in tracked source files
- logins still work after the hashing change
- the frontend no longer keeps long-lived tokens in unsafe storage
- CORS is not open to every origin in production
- the backend boot process fails clearly if required settings are missing

---

## Phase 2: Database Migration to PostgreSQL

### Goal

Move the app from MySQL-oriented assumptions to PostgreSQL without losing user data or breaking the application.

### Why this is a major phase

The database is the backbone of the platform.
If the migration is handled poorly, you can lose:

- users
- trades
- holdings
- scores
- leaderboard history
- reports

### What to change

#### 1. Database driver and connection string

Replace the current MySQL connection path with PostgreSQL.

Recommended driver:

- `psycopg` or `psycopg2-binary`

Recommended ORM path:

- SQLAlchemy for ORM
- Alembic or Flask-Migrate for schema changes

Files:

- `backend/app/__init__.py`
- `backend/requirements.txt`

#### 2. Container runtime

The local development database should run as PostgreSQL in Docker Compose.

What to update:

- replace the MySQL service
- update port mapping
- update environment variables
- update startup wait logic

Files:

- `docker-compose.yml`
- `backend/entrypoint.sh`

#### 3. Schema and constraints

The schema must be checked for PostgreSQL compatibility.

What to review:

- enum behavior
- timestamp defaults
- numeric precision
- foreign key behavior
- string length constraints
- indexing strategy

Files:

- `backend/app/models.py`
- `backend/migrations/schema.sql`

#### 4. Migration strategy

Stop relying on a one-time schema SQL file once the project starts evolving.

What to introduce:

- versioned migration scripts
- repeatable schema changes
- upgrade and downgrade support

Files:

- `backend/migrations/`
- `backend/requirements.txt`

### Data migration plan

#### Step 1: Create a PostgreSQL test database

Set up a clean Postgres instance and apply the new schema there first.

#### Step 2: Compare schemas

Verify every table from MySQL has an equivalent in PostgreSQL.

#### Step 3: Move seed data

Export the current data and import it into the PostgreSQL structure.

#### Step 4: Validate business behavior

Check:

- user registration
- login
- trade execution
- holdings update
- portfolio summary
- leaderboard generation

#### Step 5: Switch the app

Only point the application to PostgreSQL after the test migration behaves correctly.

### Postgres-specific details to verify

- `Numeric` precision is preserved.
- date and timestamp values remain accurate.
- foreign keys behave as intended on delete.
- enum-like values are not silently broken.
- indexes exist for frequent lookup columns.

### Acceptance criteria

This phase is complete when:

- the app runs against PostgreSQL locally
- existing core flows still work
- schema creation and migration are reproducible
- old MySQL assumptions no longer appear in runtime config

---

## Phase 3: Backend Restructuring

### Goal

Make the backend maintainable by moving business logic out of route handlers and into clearer layers.

### Why this phase matters

Right now the backend mixes:

- HTTP request handling
- data validation
- business logic
- scoring logic
- database updates

That makes each file harder to understand, test, and change.

### What to change

#### 1. Separate layers

Split code into:

- routes/controllers
- service layer
- database/repository layer
- schemas/validators

#### 2. Centralize repeated logic

Common patterns to extract:

- user lookup
- portfolio lookup
- holding sync
- trade validation
- score calculation
- error formatting

#### 3. Standardize response shapes

Every endpoint should return predictable JSON:

- success responses with consistent keys
- error responses with consistent keys and HTTP codes

### Files that should be reorganized first

- `backend/app/auth/routes.py`
- `backend/app/portfolio/routes.py`
- `backend/app/market/routes.py`
- `backend/app/analytics/routes.py`
- `backend/app/scoring/*`

### Suggested target structure

- `backend/app/services/auth_service.py`
- `backend/app/services/portfolio_service.py`
- `backend/app/services/scoring_service.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/repositories/trade_repository.py`
- `backend/app/schemas/`

### What not to overdo

Do not over-engineer into too many layers too early.

The goal is not theoretical cleanliness.
The goal is:

- easier debugging
- easier testing
- lower risk changes
- cleaner ownership of logic

### Acceptance criteria

This phase is complete when:

- route handlers are much shorter
- validation is centralized
- repeated code is removed
- responses are consistent
- the backend is easier to reason about

---

## Phase 4: Apply the PDF Fixes

### Goal

Turn the PDF findings into concrete code changes, feature by feature.

### Why this phase exists

The PDF is the issue list.
This roadmap tells you how to execute that issue list without losing the broader project structure.

### Workflow for each fix

For every item in the PDF, follow the same loop:

1. Name the issue.
2. Identify the affected files.
3. Reproduce the behavior.
4. Decide whether the issue is security, data integrity, UI contract, deployment, or performance.
5. Fix the root cause.
6. Add a test or verification step.
7. Confirm the frontend still works.

### Categories you should expect in the PDF work

- auth and account recovery
- password hashing
- token/session handling
- DB schema mismatches
- trade correctness
- holdings reconciliation
- analytics and leaderboard accuracy
- market data reliability
- production deployment settings

### Practical order within PDF-driven fixes

1. auth and security issues
2. database consistency issues
3. trading and portfolio logic issues
4. analytics/leaderboard issues
5. deployment hardening
6. frontend contract alignment

### Acceptance criteria

This phase is complete when:

- each PDF item has a concrete code change
- the team can trace every fix to a file and a test
- no PDF item remains “understood but not implemented”

---

## Phase 5: Testing and Verification

### Goal

Make sure every important behavior is protected before more changes are made.

### Why this matters

Without tests, each future change will be risky.
Testing is what allows the project to keep moving after the backend is cleaned up.

### Minimum test coverage

#### Auth

- register user
- login user
- reject invalid password
- reject duplicate email
- verify password reset flow

#### Portfolio

- buy trade reduces cash and creates holdings
- sell trade increases cash and reduces holdings
- oversell is rejected
- overspend is rejected

#### Analytics

- score calculation returns expected totals
- leaderboard refresh works
- owner/admin authorization is enforced

#### Database

- schema builds cleanly
- migrations apply successfully
- critical columns preserve precision and length

#### Frontend contract

- endpoints return the expected shapes
- auth token flow works after storage changes

### Recommended test types

- unit tests for pure logic
- integration tests for API endpoints
- migration tests for database schema
- contract tests for frontend-facing payloads

### Acceptance criteria

This phase is complete when:

- core flows are covered by tests
- bugs in trade, auth, or analytics can be reproduced and verified quickly
- database or schema changes can be checked safely before deployment

---

## Phase 6: Production Readiness

### Goal

Prepare the system for real users and real deployment, not just local development.

### What production readiness means here

The app should be able to run with:

- real secrets
- real logging
- real database backups
- real HTTPS
- real domain restrictions
- predictable startup and shutdown

### What to change

#### 1. Secrets management

Move away from plain `.env` files for production secrets.

Use:

- GCP Secret Manager
- AWS Secrets Manager
- or another secret manager approved by the deployment environment

Files:

- `backend/app/__init__.py`
- `backend/config/settings.py`
- deployment config files

#### 2. Production server

Use a real WSGI server in production.

The current pattern should remain:

- Flask for application code
- Gunicorn or equivalent for serving requests

Files:

- `backend/entrypoint.sh`
- `backend/Dockerfile`

#### 3. HTTPS and CORS

Production traffic should be HTTPS only, and CORS should be limited to the real frontend domain.

#### 4. Database backup policy

The database must have:

- automated backups
- restore procedure
- retention policy
- recovery testing

#### 5. Monitoring and alerts

Add:

- health checks
- error alerts
- latency monitoring
- uptime monitoring
- resource alerts

### Deployment choices

#### On GCP

Suggested components:

- Cloud Run for backend
- Cloud SQL for PostgreSQL
- Secret Manager for credentials
- Cloud Logging for logs
- Cloud Monitoring for alerts

#### On AWS

Suggested components:

- ECS or App Runner for backend
- RDS for PostgreSQL
- Secrets Manager for secrets
- CloudWatch for logs and metrics
- S3 for generated files and reports

### Acceptance criteria

This phase is complete when:

- the backend can deploy with environment-specific settings
- secrets are not stored in source
- the app is secured for public access
- backups and monitoring exist

---

## Phase 7: Scale Readiness

### Goal

Make the system able to handle more users, more requests, and more background work.

### What scaling means for this project

The first scaling pressure points are likely:

- market data calls
- scoring jobs
- leaderboard refreshes
- portfolio recalculation
- authentication traffic

### What to add

#### 1. Shared cache

Use Redis instead of in-memory cache.

Why:

- one process should not own the cache
- multiple backend instances need shared values

Files:

- `backend/app/cache.py`

#### 2. Background jobs

Move expensive scoring and report generation out of request handlers.

Why:

- user requests stay fast
- expensive calculations become more reliable
- retries become possible

Files:

- `backend/app/jobs.py`
- `backend/app/analytics/routes.py`
- `backend/app/scoring/*`

#### 3. Queue worker

If the app grows, a real queue is better than a simple thread pool.

Potential tools:

- Celery
- RQ
- Dramatiq

#### 4. Load balancing and autoscaling

When traffic grows, the backend should not rely on one process or one host.

#### 5. Database resilience

Plan for:

- backups
- read replicas
- failover
- connection pooling

### What not to rely on at scale

- in-memory cache only
- synchronous expensive work inside requests
- one backend instance
- one unprotected database

### Acceptance criteria

This phase is complete when:

- multiple backend instances behave consistently
- cache is shared
- scoring is no longer a bottleneck inside web requests
- database failure and recovery are planned, not improvised

---

## Phase 8: Frontend Integration Checks

### Goal

Keep the UI working while the backend changes.

### Why this matters

The frontend can break even when the backend “works” if request paths, response shapes, or token storage behavior change.

### What to verify

#### Auth flow

- registration still creates a user
- login still returns usable auth state
- logout clears the session
- password reset works end to end

#### Portfolio flow

- buy and sell forms still submit correctly
- holdings and summary screens still render
- deleted/closed holdings behave as expected

#### Analytics flow

- scores page still loads
- leaderboard still loads
- owner/admin visibility still works

#### Environment switching

- local dev points to local backend
- staging points to staging backend
- production points to production backend

### Frontend files to watch closely

- `frontend/DRA App/src/native/api.ts`
- `frontend/DRA App/src/native/auth-store.ts`
- `frontend/DRA App/src/native/types.ts`
- `frontend/DRA App/src/native/main-app.tsx`
- `frontend/DRA App/src/native/pages/*`

### Acceptance criteria

This phase is complete when:

- the frontend works with the new backend contract
- no hidden API URL remains in production logic
- auth and portfolio screens still function after storage and token changes

---

## Phase 9: Suggested Release Strategy

### Goal

Ship the work in a way that reduces risk.

### Recommended release sequence

#### Release 1

- security cleanup
- environment cleanup
- password hash upgrade

#### Release 2

- PostgreSQL migration
- schema alignment
- local Docker updates

#### Release 3

- portfolio trade safety
- holdings reconciliation
- audit-preserving changes

#### Release 4

- analytics stabilization
- leaderboard consistency
- shared cache groundwork

#### Release 5

- production deployment
- secrets management
- monitoring and backups

#### Release 6

- background jobs
- Redis cache
- scale improvements

### Why this sequence works

It prioritizes:

1. security
2. data integrity
3. core business logic
4. operational stability
5. scale

That order avoids building advanced infrastructure on top of unsafe foundations.

---

## Suggested Fix Order

1. Freeze and inventory the current system.
2. Remove hardcoded secrets and unsafe token storage.
3. Upgrade password hashing and add password recovery.
4. Move the app to PostgreSQL.
5. Add migrations and align schema with models.
6. Refactor backend layers for maintainability.
7. Fix trade and holdings correctness.
8. Stabilize analytics and leaderboard behavior.
9. Add tests around all core flows.
10. Harden production deployment.
11. Add Redis, queues, observability, and backup workflows.
12. Verify frontend integration after every major backend change.

---

## Detailed Execution Guide

### Phase 0 in practice

Do these tasks in order:

1. Open each backend route file and make a route index with method, path, auth, and input/output.
2. Open `backend/app/models.py` and map each model to the table it represents.
3. Open `frontend/DRA App/src/native/api.ts` and list every backend endpoint used by the app.
4. Search the repo for hardcoded URLs, secrets, and database credentials.
5. Mark every endpoint as `active`, `legacy`, or `duplicate`.
6. Identify which frontend screens depend on each endpoint.
7. Identify which routes are only used for demo or legacy behavior.

Useful output from this phase:

- a route catalog
- a model-to-table catalog
- a frontend API usage list
- a secrets and configuration risk list

Recommended file to create for this work:

- `docs/tradeiq-route-inventory.md`

### Phase 1 in practice

Security cleanup should happen in a specific order because some fixes depend on others.

1. Fix backend configuration loading first.
2. Replace password hashing second.
3. Fix frontend auth token persistence third.
4. Restrict CORS fourth.
5. Add password reset and recovery fifth.
6. Add login throttling and optional verification after the base auth flow works.

Specific implementation details:

- Add a `PASSWORD_HASH_SCHEME` decision and keep it consistent across register and login.
- Add a `JWT_ACCESS_TOKEN_EXPIRES` setting and make the token lifetime explicit.
- Add a `REFRESH_TOKEN_EXPIRES` setting if refresh tokens are introduced.
- Add `ALLOWED_CORS_ORIGINS` instead of a wildcard origin list.
- Add a `SECURE_SESSION_STORAGE` strategy for web and native separately.

Suggested acceptance tests:

1. New user registration stores a strong password hash.
2. Login with a valid password succeeds.
3. Login with an invalid password fails.
4. Session storage does not expose tokens in browser local storage.
5. Password reset links expire and cannot be reused.
6. A missing required env variable stops startup early.

### Phase 2 in practice

PostgreSQL migration should be run as a controlled, reversible exercise.

#### Step A: Prepare the schema

1. Copy the current table structure into a PostgreSQL migration set.
2. Update column sizes where hashes or IDs need more room.
3. Review enum-like columns for PostgreSQL compatibility.
4. Confirm foreign keys and cascades behave correctly.

#### Step B: Prepare data conversion

1. Export current tables.
2. Map every MySQL type to its PostgreSQL equivalent.
3. Load a copy into a test database.
4. Verify row counts and key fields after import.

#### Step C: Switch the application

1. Change the SQLAlchemy URI.
2. Change Docker Compose service definitions.
3. Update local development instructions.
4. Confirm backend boot waits for PostgreSQL.

#### Step D: Verify critical flows

1. Register a user.
2. Log in.
3. Submit a trade.
4. Load holdings.
5. Load portfolio summary.
6. Load leaderboard and score pages.

Data quality checks:

- no truncation of password hashes
- no precision loss in monetary fields
- no missing foreign key relationships
- no silent enum failures

### Phase 3 in practice

Refactoring should follow feature boundaries, not file size only.

Recommended split order:

1. auth service
2. portfolio service
3. market data service
4. analytics/scoring service
5. shared database helpers
6. request validation layer

Rules for the refactor:

- Do not change the frontend contract unless necessary.
- Do not change business rules while moving code unless you are fixing a real bug.
- Do not mix refactor-only changes with behavior changes in the same commit if you can avoid it.

### Phase 4 in practice

The PDF fixes should be handled feature by feature, and each feature should use the same structure:

1. observe
2. reproduce
3. isolate
4. patch
5. verify

For each fix item:

- write down the exact symptom
- identify the file path
- identify the user impact
- choose the minimal safe change
- add a test or manual verification step
- record the follow-up risk if any remains

### Phase 5 in practice

Testing should be built around the highest-risk flows.

Minimum test sequence:

1. auth tests
2. trade tests
3. holdings tests
4. summary tests
5. analytics tests
6. migration tests
7. frontend contract tests

Recommended regression guardrails:

- one test for each major API endpoint
- one test for each major database write path
- one test for each major score calculation path

### Phase 6 in practice

Production readiness is not just deployment.
It also means operational control.

Add these runbook items:

- how to rotate JWT secrets
- how to rotate DB credentials
- how to restore a backup
- how to redeploy safely
- how to check service health
- how to rollback a bad release

### Phase 7 in practice

Scale work should be added only after the system is correct and tested.

Recommended order:

1. Redis cache
2. queue-based jobs
3. shared background scoring
4. database backup/replica plan
5. autoscaling deployment
6. observability dashboards

### Phase 8 in practice

Frontend integration should be verified on every backend release.

Checklist:

- auth screens still load
- onboarding still saves correctly
- trade forms still submit correctly
- leaderboard still renders
- score pages still load
- logout still clears session state

### Suggested delivery milestones

#### Milestone 1: Safety baseline

Deliver:

- environment cleanup
- auth hardening
- token storage fix
- no hardcoded secrets

#### Milestone 2: Data platform switch

Deliver:

- PostgreSQL working locally
- migrations in place
- schema validated

#### Milestone 3: Behavior correctness

Deliver:

- trade flow corrected
- holdings reconciliation fixed
- analytics output stabilized

#### Milestone 4: Production and scale

Deliver:

- deployment config
- monitoring
- Redis
- job queue
- backup strategy

### Suggested team workflow

If more than one person is working on this, split ownership like this:

- one person on auth and config
- one person on PostgreSQL migration
- one person on portfolio/trading logic
- one person on analytics and scoring
- one person on frontend contract alignment

### Suggested change management rules

- Keep each phase in its own branch or commit group if possible.
- Do not deploy partial auth changes without verifying login and recovery.
- Do not switch databases until migration tests pass.
- Do not expose production URLs or secrets in docs or code samples.

---

## Appendix A: Phase Risk and Effort Matrix

| Phase | Main Risk if Skipped | Dependency Blocks | Estimated Effort |
|---|---|---|---|
| Phase 0 Inventory and Freeze | You will refactor the wrong files and miss hidden dependencies. | All later phases | S |
| Phase 1 Security and Runtime Stabilization | Secrets, weak auth, and unsafe storage remain exposed while other work proceeds. | Phases 2-8 are safer after this | M |
| Phase 2 PostgreSQL Migration | Schema drift and broken production deployment if the old DB assumptions stay in place. | Phase 1 should already be stable | L |
| Phase 3 Backend Restructuring | The codebase stays hard to maintain and every later fix takes longer. | Easier after Phase 2 | L |
| Phase 4 PDF Fixes | The documented problems remain open and the team has no implementation sequence. | Depends on Phases 0-3 for context | L |
| Phase 5 Testing and Verification | Regressions will spread unnoticed while the project changes. | Should begin as soon as core flows are stable | M |
| Phase 6 Production Readiness | Deployments remain fragile, insecure, and difficult to support. | Safer after Phases 1-5 | M |
| Phase 7 Scale Readiness | The system may work for demos but fail as usage grows. | Should wait until correctness is stable | L |
| Phase 8 Frontend Integration Checks | UI breaks can slip through unnoticed while backend changes continue. | Must be done after every meaningful backend release | M |

### How to use this matrix

1. If a phase has a large dependency block, do not start a later phase first unless the blocker is understood and intentionally accepted.
2. If a phase has a large effort estimate, split it into smaller sub-deliveries rather than merging it with unrelated work.
3. If a phase is listed as a dependency for many other phases, treat it as a release blocker.

---

## Appendix B: Dependency Map

### Phase 0 depends on

- nothing before it

### Phase 1 depends on

- the current route and model inventory
- knowledge of the frontend auth flow
- knowledge of the current runtime config

### Phase 2 depends on

- Phase 0 inventory of tables and models
- Phase 1 cleanup of runtime config
- a decision on the target PostgreSQL driver and migration tool

### Phase 3 depends on

- Phase 0 route map
- Phase 2 schema alignment
- Phase 1 config cleanup

### Phase 4 depends on

- Phase 0 system inventory
- Phase 1 security fixes
- Phase 2 database migration plan
- Phase 3 refactor boundaries

### Phase 5 depends on

- stable auth flows
- stable trade and portfolio flows
- stable analytics payloads

### Phase 6 depends on

- secure secrets handling
- PostgreSQL deployment path
- tested API behavior
- consistent CORS and auth policies

### Phase 7 depends on

- stable core functionality
- production-ready database behavior
- a working cache or queue strategy

### Phase 8 depends on

- every frontend endpoint used in production
- the final API contract
- auth token storage changes

---

## Appendix C: Phase-by-Phase Delivery Notes

### Phase 0 delivery notes

This is a research and mapping phase.
Do not make behavior changes here unless you find a severe production blocker that can be fixed safely and independently.

### Phase 1 delivery notes

This is the foundation phase for security and runtime stability.
If any auth or configuration change breaks login, stop and fix that before moving on.

### Phase 2 delivery notes

Treat this as a data platform migration, not a simple package upgrade.
Plan for test runs, data verification, and a rollback path.

### Phase 3 delivery notes

Prefer smaller refactors that make the code easier to understand.
Avoid “big bang” cleanups that move too many responsibilities at once.

### Phase 4 delivery notes

Work through the PDF in the same order the risk appears in the app.
Auth and data correctness should come before convenience fixes.

### Phase 5 delivery notes

Testing is not a final polish step here.
It is a protection layer that should be added as soon as a core path is stable enough to test.

### Phase 6 delivery notes

Production readiness means the app can be supported by someone who is not the original developer.
That means clear logs, clear health signals, clear secrets handling, and clear restore instructions.

### Phase 7 delivery notes

Scale work should be added only after correctness and safety are already in place.
Scaling a broken system only makes the broken behavior happen faster.

### Phase 8 delivery notes

Every backend change should be validated against the frontend flows that depend on it.
If the frontend changes are larger than expected, document the contract difference immediately.

---

## Appendix D: Short Implementation Rules

1. Do not mix security fixes with data migration unless the fix is required for migration.
2. Do not replace the database before you know exactly which tables and columns the frontend actually uses.
3. Do not use local process memory for anything that must survive multiple workers.
4. Do not rely on browser local storage for long-lived auth if XSS is a realistic concern.
5. Do not delete audit history during normal user actions.
6. Do not run expensive scoring work synchronously if it can be moved to a background job.
7. Do not call a phase done until the verification checklist passes.
