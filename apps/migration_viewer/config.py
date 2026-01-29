"""Database configuration for Migration Viewer."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5433)),
    "database": os.getenv("DB_NAME", "goreos_model"),
    "user": os.getenv("DB_USER", "goreos"),
    "password": os.getenv("DB_PASSWORD", "goreos_2026"),
}

DATABASE_URL = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# Pagination
DEFAULT_PAGE_SIZE = 20
PAGE_SIZE_OPTIONS = [10, 20, 50, 100]
