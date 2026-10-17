
import sys
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )
        print("SQLAlchemy connection successful!")
        print("Database and user:", result.fetchone())

except SQLAlchemyError as error:
    print("SQLAlchemy connection failed.")
    print(error)
