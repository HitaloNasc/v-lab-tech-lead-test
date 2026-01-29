#!/bin/bash
set -e

echo "Waiting for database..."
python - <<'PY'
import os, time, sys
import psycopg2

url = os.environ.get('DATABASE_URL')
if not url:
    print('DATABASE_URL not set', file=sys.stderr)
    sys.exit(1)

max_tries = 60
for i in range(max_tries):
    try:
        conn = psycopg2.connect(dsn=url)
        conn.close()
        print('Database is ready')
        sys.exit(0)
    except Exception:
        print(f'Database not ready, retrying ({i+1}/{max_tries})...')
        time.sleep(1)
print('Timed out waiting for database', file=sys.stderr)
sys.exit(1)
PY

echo "Running alembic migrations..."
python -m alembic upgrade head

echo "Starting application: $@"
exec "$@"
