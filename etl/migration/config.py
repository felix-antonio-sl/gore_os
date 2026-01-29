"""
Migration configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from project root .env
PROJECT_ROOT = Path(__file__).parent.parent.parent
env_file = PROJECT_ROOT / '.env'
if env_file.exists():
    load_dotenv(env_file)

# Database
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5433))  # Docker container port
DB_NAME = os.getenv('DB_NAME', 'goreos_model')  # Actual database name
DB_USER = os.getenv('DB_USER', 'goreos')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'goreos_2026')  # Default dev password

# Migration
NORMALIZED_DIR = Path(__file__).parent.parent / 'normalized'
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 1000))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
