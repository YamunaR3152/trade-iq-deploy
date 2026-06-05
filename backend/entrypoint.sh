#!/bin/sh
set -e

echo "Waiting for MySQL at ${DB_HOST:-localhost}:${DB_PORT:-3306}..."
python - <<'PYEOF'
import socket, time, os, sys
host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "3306"))
for attempt in range(30):
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
        print(f"MySQL is ready at {host}:{port}")
        sys.exit(0)
    except OSError:
        print(f"Attempt {attempt + 1}/30: MySQL not ready, retrying in 2s...")
        time.sleep(2)
print("ERROR: MySQL did not start within 60s.", file=sys.stderr)
sys.exit(1)
PYEOF

exec flask run --host=0.0.0.0 --port=5000
