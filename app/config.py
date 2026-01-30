import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

MIGRATION_LOCK_ID: int = int(os.getenv("MIGRATION_LOCK_ID"))

JWT_SECRET: str = os.getenv("JWT_SECRET")

JWT_ALG: str = os.getenv("JWT_ALG")

ACCESS_TOKEN_EXPIRE_MIN: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN"))

CORS_ORIGINS: str = os.getenv("CORS_ORIGINS")

SEED_ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "admin@local").strip().lower()
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD", "admin123")
SEED_ADMIN_NAME = os.getenv("SEED_ADMIN_NAME", "Admin")

def cors_origins_list() -> List[str]:
    raw = CORS_ORIGINS.strip()
    if not raw:
        return []
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]