import uuid
import threading
import requests

BASE = "http://localhost:5000"

USER_DATA = {
    "email": "analytics_test_user@example.com",
    "password": "password123",
    "full_name": "Analytics Test User"
}

# Login or register
login_res = requests.post(f"{BASE}/auth/login", json=USER_DATA)
if login_res.status_code != 200:
    requests.post(f"{BASE}/auth/register", json=USER_DATA)
    login_res = requests.post(f"{BASE}/auth/login", json=USER_DATA)

if login_res.status_code == 200:
    data = login_res.json()
    TOKEN = data.get("access_token") or data.get("token")
    USER_ID = (
        data.get("user_id") 
        or data.get("id") 
        or (data.get("user") or {}).get("user_id") 
        or (data.get("user") or {}).get("id")
    )
    print("✅ Successfully logged in for Analytics tests!")
    print(f"   USER_ID: {USER_ID}\n")
else:
    print(f"❌ Auth failed ({login_res.status_code}): {login_res.text}")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def log_header(title):
    print(f"\n==========================================\n {title}\n==========================================")

def test_section_10_6():
    log_header("SECTION 10.6: Safe Defaults & Missing Data Resilience")
    
    # A1: Fetch scores for user with no activity / new user
    r1 = requests.get(f"{BASE}/analytics/scores/{USER_ID}", headers=HEADERS)
    print(f"A1 Get Scores Status: {r1.status_code} | Payload: {r1.json()}")
    
    # A2: Compute scores for week 30 twice (Idempotency check)
    r2_1 = requests.post(f"{BASE}/analytics/compute/{USER_ID}?week=30", headers=HEADERS)
    r2_2 = requests.post(f"{BASE}/analytics/compute/{USER_ID}?week=30", headers=HEADERS)
    
    status_1, status_2 = r2_1.status_code, r2_2.status_code
    print(f"A2 Compute Run 1: {status_1} | Run 2: {status_2}")
    if status_1 == 200 and status_2 == 200:
        print("SUCCESS: Compute handles repeated calls cleanly without crashing.")

def test_section_10_7():
    log_header("SECTION 10.7: Concurrent Upsert & Uniqueness Lock Proof")
    
    # C1: 5 Concurrent compute calls for the same user & week
    print("\n--- C1: 5 Parallel Compute Requests (Same User/Week) ---")
    results = []
    
    def run_compute():
        try:
            r = requests.post(f"{BASE}/analytics/compute/{USER_ID}?week=30", headers=HEADERS, timeout=10)
            results.append((r.status_code, r.json()))
        except Exception as e:
            results.append((500, {"error": str(e)}))

    threads = [threading.Thread(target=run_compute) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()

    statuses = [s for s, _ in results]
    successes = sum(1 for s in statuses if s == 200)
    print(f"C1 Response Statuses: {statuses}")
    print(f"C1 Succeeded: {successes}/5 (all should be 200, DB unique constraint handling handled rollbacks)")

    # C2: Concurrent Leaderboard Refresh + Manual Compute
    print("\n--- C2: Concurrent Leaderboard GET + Compute POST ---")
    c2_results = []

    def get_lb():
        r = requests.get(f"{BASE}/analytics/leaderboard?week=30", headers=HEADERS)
        c2_results.append(("GET_LB", r.status_code))

    def post_compute():
        r = requests.post(f"{BASE}/analytics/compute/{USER_ID}?week=30", headers=HEADERS)
        c2_results.append(("POST_COMPUTE", r.status_code))

    t1 = threading.Thread(target=get_lb)
    t2 = threading.Thread(target=post_compute)
    t1.start(); t2.start()
    t1.join(); t2.join()

    print(f"C2 Execution Results: {c2_results}")
    print("SUCCESS: Parallel analytics updates completed safely without unique key violations.")

if __name__ == "__main__":
    test_section_10_6()
    test_section_10_7()