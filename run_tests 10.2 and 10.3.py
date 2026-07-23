import uuid
import requests
import threading
import concurrent.futures

BASE = "http://localhost:5000"

USER_DATA = {
    "email": "test_user@example.com",
    "password": "password123",
    "full_name": "Test User"
}

# 1. Try logging in first
login_res = requests.post(f"{BASE}/auth/login", json=USER_DATA)

# 2. If login fails, attempt to register
if login_res.status_code != 200:
    print("ℹ️ Test user not found. Attempting to register...")
    requests.post(f"{BASE}/auth/register", json=USER_DATA)
    login_res = requests.post(f"{BASE}/auth/login", json=USER_DATA)

if login_res.status_code == 200:
    data = login_res.json()
    
    # Extract TOKEN
    TOKEN = data.get("access_token") or data.get("token")
    
    # Extract USER_ID from standard login payload keys
    USER_ID = (
        data.get("user_id") 
        or data.get("id") 
        or (data.get("user") or {}).get("user_id") 
        or (data.get("user") or {}).get("id")
    )

    print("✅ Successfully logged in!")
    print(f"   USER_ID: {USER_ID}\n")
else:
    print(f"❌ Auth failed ({login_res.status_code}): {login_res.text}")
    exit(1)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def log_header(t):
    print(f"\n==========================================\n {t}\n==========================================")

def reset_account_state():
    """Clears existing AAPL holdings to ensure tests start with sufficient cash."""
    requests.delete(f"{BASE}/portfolio/holding/AAPL", headers=HEADERS)

def get_trades_count():
    res = requests.get(f"{BASE}/portfolio/trades/{USER_ID}", headers=HEADERS)
    if res.status_code == 200:
        t = res.json()
        return len(t) if isinstance(t, list) else len(t.get("trades", []))
    return 0

def test_section_a():
    log_header("SECTION A: Sequential Trade Correctness")
    reset_account_state()  # Ensure cash balance is restored
    r1 = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json={"stock_ticker": "AAPL", "trade_type": "BUY", "quantity": 5})
    print(f"A1 BUY Status: {r1.status_code} | Response: {r1.json()}")
    r2 = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json={"stock_ticker": "AAPL", "trade_type": "SELL", "quantity": 2})
    print(f"A2 SELL Status: {r2.status_code} | Response: {r2.json()}")

def test_section_b():
    log_header("SECTION B: Server Authority & Input Validation")
    r_manip = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json={"stock_ticker": "AAPL", "trade_type": "BUY", "quantity": 1000, "amount_invested": 1})
    print(f"B1 Price Attack Status: {r_manip.status_code} | {r_manip.json()}")
    r_oversell = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json={"stock_ticker": "AAPL", "trade_type": "SELL", "quantity": 999999})
    print(f"B4 Oversell Status: {r_oversell.status_code} | {r_oversell.json()}")
    r_ghost = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json={"stock_ticker": "ZZZZ", "trade_type": "SELL", "quantity": 1})
    print(f"B5 Ghost Sell Status: {r_ghost.status_code} | {r_ghost.json()}")

def test_section_c():
    log_header("SECTION C: Holding Deletion Audit Trail Check")
    before = get_trades_count()
    print(f"Trades count BEFORE deletion: {before}")
    r_del = requests.delete(f"{BASE}/portfolio/holding/AAPL", headers=HEADERS)
    print(f"Delete AAPL Status: {r_del.status_code} | {r_del.json()}")
    after = get_trades_count()
    print(f"Trades count AFTER deletion: {after}")
    if before == after and before > 0:
        print("SUCCESS: Trade history intact after deleting holding!")

def test_section_d():
    log_header("SECTION D: Idempotency Checks")
    key = str(uuid.uuid4())
    p = {"stock_ticker": "AAPL", "trade_type": "BUY", "quantity": 3, "idempotency_key": key}
    r1 = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json=p)
    r2 = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json=p)
    
    t1_data = r1.json() if r1.status_code in (200, 201) else {}
    t2_data = r2.json() if r2.status_code in (200, 201) else {}
    
    t1 = t1_data.get("trade_id") or (t1_data.get("trade") or {}).get("trade_id")
    t2 = t2_data.get("trade_id") or (t2_data.get("trade") or {}).get("trade_id")
    
    print(f"D1 First Req: {r1.status_code}, Trade ID: {t1}")
    print(f"D1 Duplicate Req: {r2.status_code}, Trade ID: {t2}")
    if t1 and t1 == t2:
        print("SUCCESS: Duplicate idempotency key returned exact same trade ID!")
    else:
        print("FAIL: Duplicate idempotency key created multiple trades or failed!")

def test_section_e():
    log_header("SECTION E: Concurrency & Lock Proof")
    
    # Reset balance before running concurrency tests so cash doesn't run out
    reset_account_state()

    # --- E1: 5 Parallel BUYs ---
    print("\n--- E1: 5 Parallel BUYs ---")
    res = []
    def buy():
        try:
            r = requests.post(f"{BASE}/portfolio/trade", headers=HEADERS, json={"stock_ticker": "AAPL", "trade_type": "BUY", "quantity": 1}, timeout=5)
            res.append((r.status_code, r.json()))
        except Exception as e:
            res.append((500, {"error": str(e)}))
            
    threads = [threading.Thread(target=buy) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    successes = sum(1 for status, _ in res if status in (200, 201))
    print(f"E1 Completed: {successes}/5 succeeded.")

    # --- E2: 5 Parallel Requests (Same Idempotency Key) ---
    print("\n--- E2: 5 Parallel Requests (Same Idempotency Key) ---")
    key = str(uuid.uuid4())
    e2_res = []
    
    def buy_idemp():
        try:
            r = requests.post(
                f"{BASE}/portfolio/trade", 
                headers=HEADERS, 
                json={"stock_ticker": "AAPL", "trade_type": "BUY", "quantity": 1, "idempotency_key": key},
                timeout=5
            )
            data = r.json()
        except Exception as e:
            data = {"error": str(e), "raw_status": 500}
            r = type('obj', (object,), {'status_code': 500})()
        e2_res.append((r.status_code, data))

    # 1. Start and join parallel threads
    threads_idemp = [threading.Thread(target=buy_idemp) for _ in range(5)]
    for t in threads_idemp: t.start()
    for t in threads_idemp: t.join()

    # 2. Extract trade IDs returned by responses
    trade_ids = []
    statuses = []
    for status_code, body in e2_res:
        statuses.append(status_code)
        if isinstance(body, dict):
            tid = body.get("trade_id") or (body.get("trade") or {}).get("trade_id") or (body.get("trade") or {}).get("id")
            if tid:
                trade_ids.append(tid)

    unique_trade_ids = set(trade_ids)
    print(f"E2 Response Statuses: {statuses}")
    print(f"E2 Unique Trade IDs Created: {len(unique_trade_ids)}")

    # 3. Validation
    if len(unique_trade_ids) == 1:
        print("SUCCESS: Concurrency locking works! Exactly 1 trade created across 5 identical parallel requests.")
    else:
        print(f"FAIL: Expected 1 unique trade ID, but got {len(unique_trade_ids)}: {unique_trade_ids}")

if __name__ == '__main__':
    if not TOKEN or not USER_ID:
        print('Error: TOKEN and USER_ID environment variables must be set.')
    else:
        test_section_a()
        test_section_b()
        test_section_c()
        test_section_d()
        test_section_e()