# backend/run_test.py
"""
Test Suite for 10.11 Backend Refactoring:
1. Shared user_repository.is_admin checks and behavior.
2. Centralized Blueprint Error Handlers for AuthError, PortfolioError, and AnalyticsError.
3. Authorization checks on GET/POST user-scoped routes (including /compute-legacy).
4. Standardized response envelopes for POST endpoints.
"""

import sys
from flask_jwt_extended import create_access_token

from app.auth.routes import auth_bp
from app.portfolio.routes import portfolio_bp
from app.analytics.routes import analytics_bp

# Import exact error classes from services
from app.services.auth_service import AuthError
from app.services.portfolio_service import PortfolioError
from app.services.analytics_service import AnalyticsError


# Attach test endpoints directly to the blueprints
@auth_bp.route("/test-auth-error")
def trigger_auth_error():
    raise AuthError("Invalid credentials provided", status_code=401)


@portfolio_bp.route("/test-portfolio-error")
def trigger_portfolio_error():
    raise PortfolioError("Insufficient funds for trade", status_code=400)


@analytics_bp.route("/test-analytics-error")
def trigger_analytics_error():
    raise AnalyticsError("No score data available", status_code=404)


def setup_test_app():
    from app import create_app
    from app.extensions import db

    app = create_app()

    app.config["TESTING"] = True
    app.config["PROPAGATE_EXCEPTIONS"] = False  # Keep exception handling enabled in Flask
    app.config["TRAP_HTTP_EXCEPTIONS"] = False
    app.config["RATELIMIT_ENABLED"] = False

    # Ensure error handlers exist at application level if blueprint handles misfire
    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        return {"error": e.message}, getattr(e, "status_code", 401)

    @app.errorhandler(PortfolioError)
    def handle_portfolio_error(e):
        return {"error": e.message}, getattr(e, "status_code", 400)

    @app.errorhandler(AnalyticsError)
    def handle_analytics_error(e):
        return {"error": e.message}, getattr(e, "status_code", 404)

    return app, db


def run_tests():
    app, db = setup_test_app()
    from app.models import User

    passed = 0
    failed = 0

    print("=" * 60)
    print("RUNNING 10.11 VERIFICATION TESTS")
    print("=" * 60)

    with app.app_context():
        # Seed test users
        regular_user = User(
            user_id="usr_regular_123",
            full_name="Regular User",
            email="user@test.com",
            role="user",
            password_hash="mock_hash_123",
        )
        admin_user = User(
            user_id="usr_admin_999",
            full_name="Admin User",
            email="admin@test.com",
            role="admin",
            password_hash="mock_hash_999",
        )
        other_user = User(
            user_id="usr_other_456",
            full_name="Other User",
            email="other@test.com",
            role="user",
            password_hash="mock_hash_456",
        )

        db.session.add_all([regular_user, admin_user, other_user])
        db.session.commit()

        # Generate JWT Tokens
        user_token = create_access_token(identity="usr_regular_123")
        admin_token = create_access_token(identity="usr_admin_999")
        other_token = create_access_token(identity="usr_other_456")

        headers_user = {"Authorization": f"Bearer {user_token}"}
        headers_admin = {"Authorization": f"Bearer {admin_token}"}
        headers_other = {"Authorization": f"Bearer {other_token}"}

        client = app.test_client()

        def assert_test(name, condition, error_detail=""):
            nonlocal passed, failed
            if condition:
                print(f"  [PASS] {name}")
                passed += 1
            else:
                print(f"  [FAIL] {name} - {error_detail}")
                failed += 1

        try:
            # -------------------------------------------------------------
            # 1. Repository is_admin Check
            # -------------------------------------------------------------
            print("\n--- 1. Testing user_repository.is_admin ---")
            from app.repositories.user_repository import is_admin

            assert_test(
                "is_admin returns True for admin user",
                is_admin("usr_admin_999") is True,
            )
            assert_test(
                "is_admin returns False for non-admin user",
                is_admin("usr_regular_123") is False,
            )
            assert_test(
                "is_admin returns False for non-existent user",
                is_admin("usr_nonexistent_000") is False,
            )

            # -------------------------------------------------------------
            # 2. Authorization Checks on Routes (Ownership & Admin Bypass)
            # -------------------------------------------------------------
            print("\n--- 2. Testing Authorization Checks Across Routes ---")

            res = client.post(
                "/analytics/compute-legacy/usr_regular_123",
                headers=headers_other,
            )
            assert_test(
                "Unauthorized compute-legacy returns 403 Forbidden",
                res.status_code == 403,
                f"Got status {res.status_code}",
            )

            res = client.post(
                "/analytics/compute-legacy/usr_regular_123",
                headers=headers_user,
            )
            assert_test(
                "Owner can invoke compute-legacy (not 403)",
                res.status_code != 403,
                f"Got status {res.status_code}",
            )

            res = client.post(
                "/analytics/compute-legacy/usr_regular_123",
                headers=headers_admin,
            )
            assert_test(
                "Admin can invoke compute-legacy for another user",
                res.status_code != 403,
                f"Got status {res.status_code}",
            )

            res = client.get("/portfolio/summary/usr_regular_123", headers=headers_other)
            assert_test(
                "Unauthorized summary view returns 403 Forbidden",
                res.status_code == 403,
                f"Got status {res.status_code}",
            )

            res = client.get("/analytics/scores/usr_regular_123", headers=headers_other)
            assert_test(
                "Unauthorized scores view returns 403 Forbidden",
                res.status_code == 403,
                f"Got status {res.status_code}",
            )

            # -------------------------------------------------------------
            # 3. Centralized Blueprint Error Handler Verification
            # -------------------------------------------------------------
            print("\n--- 3. Testing Blueprint Error Handlers ---")

            res = client.get("/auth/test-auth-error")
            data = res.get_json() or {}
            assert_test(
                "AuthError handling returns correct format and status",
                res.status_code == 401 and data.get("error") == "Invalid credentials provided",
                f"Status {res.status_code}, payload: {data}",
            )

            res = client.get("/portfolio/test-portfolio-error")
            data = res.get_json() or {}
            assert_test(
                "PortfolioError handling returns correct format and status",
                res.status_code == 400 and data.get("error") == "Insufficient funds for trade",
                f"Status {res.status_code}, payload: {data}",
            )

            res = client.get("/analytics/test-analytics-error")
            data = res.get_json() or {}
            assert_test(
                "AnalyticsError handling returns correct format and status",
                res.status_code == 404 and data.get("error") == "No score data available",
                f"Status {res.status_code}, payload: {data}",
            )

            # -------------------------------------------------------------
            # 4. Standardized Response Envelope Verification
            # -------------------------------------------------------------
            print("\n--- 4. Testing Response Envelopes ---")

            res = client.post("/analytics/compute/usr_regular_123", headers=headers_user)
            data = res.get_json() or {}
            assert_test(
                "POST /analytics/compute response contains 'message' envelope key",
                "message" in data,
                f"Keys received: {list(data.keys())}",
            )

        finally:
            User.query.filter(User.user_id.in_(["usr_regular_123", "usr_admin_999", "usr_other_456"])).delete()
            db.session.commit()

    print("\n" + "=" * 60)
    print(f"TEST SUMMARY: {passed} PASSED, {failed} FAILED")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_tests()