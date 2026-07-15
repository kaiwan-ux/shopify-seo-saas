#!/usr/bin/env python3
"""Docker entrypoint: wait for DB, run migrations, start the app."""

import asyncio
import subprocess
import sys
import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config.settings import get_settings


async def wait_for_database(max_retries: int = 30, delay: float = 2.0) -> None:
    settings = get_settings()
    engine = create_async_engine(str(settings.database_url))

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            print("Database is ready.")
            return
        except Exception:
            await engine.dispose()
            print(f"Database unavailable (attempt {attempt}/{max_retries}) — retrying in {delay}s...")
            time.sleep(delay)

    print("Could not connect to database.", file=sys.stderr)
    sys.exit(1)


def run_migrations() -> None:
    print("Running database migrations...")
    result = subprocess.run(["alembic", "upgrade", "head"], check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> None:
    asyncio.run(wait_for_database())
    run_migrations()
    print("Starting application...")
    os_exec = subprocess.run(sys.argv[1:], check=False)
    sys.exit(os_exec.returncode)


if __name__ == "__main__":
    main()
