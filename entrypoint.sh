#!/bin/sh
set -e

echo "Waiting for database..."
python - <<'PY'
import os, asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

db_url = os.environ["DATABASE_URL"]
engine = create_async_engine(db_url, echo=False)

async def main():
    for i in range(60):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database is ready ✅")
            await engine.dispose()
            return
        except Exception as e:
            print(f"DB not ready yet ({i+1}/60): {e}")
            await asyncio.sleep(1)
    raise SystemExit("Database not ready after 60s")

asyncio.run(main())
PY

echo "Running migrations with advisory lock..."
python - <<'PY'
import os, subprocess, asyncio
import asyncpg

db_url = os.environ["DATABASE_URL"]
lock_id = int(os.getenv("MIGRATION_LOCK_ID"))

async def main():
    pg_url = db_url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(pg_url)
    try:
        print(f"Acquiring advisory lock {lock_id}...")
        await conn.execute("SELECT pg_advisory_lock($1);", lock_id)

        print("Applying alembic migrations...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)

        print("Releasing advisory lock...")
        await conn.execute("SELECT pg_advisory_unlock($1);", lock_id)
    finally:
        await conn.close()

asyncio.run(main())
PY

echo "Starting API..."
exec uvicorn app.setup:app --host 0.0.0.0 --port 8000

