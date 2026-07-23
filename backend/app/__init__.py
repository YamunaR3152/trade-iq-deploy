import logging
import os
import ssl
import time
import uuid
import psutil  # <--- Added for P3 Telemetry
from flask import Flask, g, jsonify, request
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

# Ensure environment variables are loaded from .env before config checks run
load_dotenv(override=True)

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from app.extensions import db, jwt, cors, limiter
from app.cache import cache_backend
from sqlalchemy.engine import URL

logger = logging.getLogger(__name__)

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
    )


def setup_logging(app: Flask):
    """Configures centralized structured logging."""
    log_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s'
    )

    # 1. Console Handler (Render / Docker / stdout)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)

    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)

    # 2. Rotating File Handler (Local / Persistent storage)
    if not os.path.exists("logs"):
        os.makedirs("logs")

    file_handler = RotatingFileHandler("logs/tradeiq.log", maxBytes=10_000_000, backupCount=5)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("[TradeIQ] Centralized logging initialized successfully.")


def _build_database_uri() -> str:
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    database = os.getenv("DB_NAME", "tradeiq")
    username = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "yamuna")

    # Construct clean connection string directly to ensure exact password string handling
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"


def _check_required_config() -> None:
    """Fail loudly and clearly if required settings are missing."""
    required = ["SECRET_KEY", "JWT_SECRET_KEY", "DB_HOST", "DB_NAME", "DB_USER"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError(
            "Backend cannot start — missing required environment variable(s): "
            f"{', '.join(missing)}. Check your backend/.env file."
        )

    known_weak_values = {
        "mysecretkey123",
        "jwtkey456",
        "change-me-to-a-long-random-string",
        "change-me-to-another-long-random-string",
        "dev-secret",
        "dev-jwt-secret",
    }
    if (
        os.getenv("SECRET_KEY") in known_weak_values
        or os.getenv("JWT_SECRET_KEY") in known_weak_values
    ):
        print(
            "⚠️ WARNING: SECRET_KEY or JWT_SECRET_KEY is still a placeholder value. "
            "Generate a real random value before using this anywhere other than local dev."
        )


def _build_engine_options() -> dict:
    options = {"pool_pre_ping": True, "pool_recycle": 280}

    if os.getenv("DB_SSL", "false").lower() == "true":
        ca_path = os.getenv(
            "DB_SSL_CA",
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "tidb-ca.pem"),
        )
        ctx = ssl.create_default_context(cafile=ca_path)
        options["connect_args"] = {"ssl": ctx}

    return options


def create_app() -> Flask:
    _check_required_config()
    app = Flask(__name__)

    # 🚀 Setup Structured Logging right after initializing Flask app instance
    setup_logging(app)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = _build_database_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = _build_engine_options()

    app.logger.info(
        f"[TradeIQ] Starting up — DB host: {os.getenv('DB_HOST')} | "
        f"DB name: {os.getenv('DB_NAME')} | "
        f"SSL: {os.getenv('DB_SSL', 'false')} | "
        f"Env: {os.getenv('FLASK_ENV', 'development')}"
    )

    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # CORS configuration
    default_origins = "http://localhost:8081,http://localhost:8082"
    allowed_origins = [
        origin.strip()
        for origin in os.getenv("ALLOWED_CORS_ORIGINS", default_origins).split(",")
        if origin.strip()
    ]
    cors.init_app(app, resources={r"/*": {"origins": allowed_origins}})

    # ------------------------------------------------------------------
    # Request-ID Tracing Middleware
    # ------------------------------------------------------------------
    @app.before_request
    def set_request_id():
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:8]
        g.request_id = request_id

    @app.after_request
    def add_request_id_header(response):
        if hasattr(g, "request_id"):
            response.headers["X-Request-ID"] = g.request_id
        return response

    # ------------------------------------------------------------------
    # Blueprints
    # ------------------------------------------------------------------
    from app.auth.routes import auth_bp
    from app.market.routes import market_bp
    from app.portfolio.routes import portfolio_bp
    from app.analytics.routes import analytics_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(market_bp)
    app.register_blueprint(portfolio_bp)
    app.register_blueprint(analytics_bp)

    # ------------------------------------------------------------------
    # Health Check Endpoints (With DB Latency & Telemetry)
    # ------------------------------------------------------------------
    @app.get("/health/live")
    def health_live():
        """Liveness probe."""
        return jsonify({"status": "ok"}), 200

    @app.get("/health/ready")
    def health_ready():
        """Readiness check validating DB latency, System Telemetry, Cache, and Limiter."""
        checks = {}
        overall_ok = True

        # 1. Database Latency Check
        start_time = time.time()
        try:
            db.session.execute(db.text("SELECT 1")).scalar()
            latency_ms = round((time.time() - start_time) * 1000, 2)
            checks["database"] = {"status": "connected", "latency_ms": latency_ms}
        except Exception as exc:
            checks["database"] = {"status": f"unreachable: {str(exc)}"}
            overall_ok = False

        # 2. System Resource Telemetry
        try:
            memory = psutil.virtual_memory()
            checks["system"] = {
                "memory_usage_percent": memory.percent,
                "cpu_usage_percent": psutil.cpu_percent(interval=None),
            }
            if memory.percent > 90:
                overall_ok = False
        except Exception:
            checks["system"] = "telemetry_unavailable"

        # 3. Cache & Limiter Checks
        checks["cache_backend"] = cache_backend()
        redis_url = os.getenv("REDIS_URL", "").strip()
        checks["rate_limiter_backend"] = "redis" if redis_url else "memory"

        status_code = 200 if overall_ok else 503
        return jsonify({
            "status": "ok" if overall_ok else "unhealthy",
            "app": "TradeIQ Academy",
            "checks": checks
        }), status_code

    @app.get("/health")
    def health_legacy():
        return health_ready()

    return app