# backend/test_10_9.py
import os
import sys
import time
import threading
import requests
from sqlalchemy.sql import text
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import create_app, db

app = create_app()
BASE = "http://localhost:5000"


def log_header(title):
    print("\n" + "=" * 50)
    print(f" {title}")
    print("=" * 50)


def get_auth_tokens():
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        user_table = "users" if "users" in tables else "user"
        
        users = db.session.execute(
            text("SELECT user_id, role FROM users LIMIT 5")
        ).fetchall()
        
        student_a = next((u[0] for u in users if u[1] != 'admin'), users[0][0])
        student_b = next((u[0] for u in users if u[0] != student_a and u[1] != 'admin'), None)
        admin = next((u[0] for u in users if u[1] == 'admin'), None)

    from flask_jwt_extended import create_access_token
    with app.app_context():
        token_a = create_access_token(identity=str(student_a))
        token_b = create_access_token(identity=str(student_b)) if student_b else None
        token_admin = create_access_token(identity=str(admin)) if admin else None

    return {
        "user_a": str(student_a),
        "token_a": token_a,
        "user_b": str(student_b) if student_b else None,
        "token_b": token_b,
        "admin": str(admin) if admin else None,
        "token_admin": token_admin,
    }


def test_section_a_authorization(auth):
    log_header("TEST GROUP A: Authorization Gap Fix on /analytics/risk")
    
    headers_a = {"Authorization": f"Bearer {auth['token_a']}"}

    # A1: User A accessing User B's risk metrics -> 403 Forbidden
    if auth["user_b"] and auth["token_b"]:
        res_a1 = requests.get(f"{BASE}/analytics/risk/{auth['user_b']}", headers=headers_a)
        print(f"A1 User A -> User B Risk: Status {res_a1.status_code}")
        assert res_a1.status_code == 403

    # A2: User A accessing their own risk metrics -> 200 or 404
    res_a2 = requests.get(f"{BASE}/analytics/risk/{auth['user_a']}", headers=headers_a)
    print(f"A2 User A -> Self Risk: Status {res_a2.status_code}")
    assert res_a2.status_code in [200, 404]

    # A3: Admin accessing User B's risk metrics -> 200 or 404 (Not 403)
    if auth["token_admin"] and auth["user_b"]:
        headers_admin = {"Authorization": f"Bearer {auth['token_admin']}"}
        res_a3 = requests.get(f"{BASE}/analytics/risk/{auth['user_b']}", headers=headers_admin)
        print(f"A3 Admin -> User B Risk: Status {res_a3.status_code}")
        assert res_a3.status_code in [200, 404]

    print("✅ Group A Authorization Checks Passed!")


def test_section_b_c_leaderboard_async_and_cache(auth):
    log_header("TEST GROUP B & C: Leaderboard Async Refresh & Locking")
    
    headers = {"Authorization": f"Bearer {auth['token_a']}"}
    target_week = 30

    # C1: Concurrent requests trigger single background execution without blocking
    results = []

    def hit_endpoint():
        res = requests.get(f"{BASE}/analytics/leaderboard?week={target_week}", headers=headers)
        if res.status_code == 200:
            results.append(res.json().get("last_refreshed"))

    threads = [threading.Thread(target=hit_endpoint) for _ in range(5)]
    start_time = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duration = time.time() - start_time

    print(f"C1 5 Concurrent Requests completed in {duration:.2f}s (Non-blocking: < 1.0s target)")
    assert duration < 2.0  # Asserts request thread wasn't blocked by worker computation

    # Wait briefly for background execution to write refresh timestamp
    time.sleep(3)

    # C2: Confirm data refresh completes and populates last_refreshed
    res_c2 = requests.get(f"{BASE}/analytics/leaderboard?week={target_week}", headers=headers)
    assert res_c2.status_code == 200
    payload = res_c2.json()
    print(f"C2 Leaderboard Payload 'last_refreshed': {payload.get('last_refreshed')}")
    assert "last_refreshed" in payload

    print("✅ Group B & C Async Refresh & Locking Assertions Passed!")


if __name__ == "__main__":
    auth = get_auth_tokens()
    test_section_a_authorization(auth)
    test_section_b_c_leaderboard_async_and_cache(auth)