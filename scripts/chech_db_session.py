
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal

try:
    with SessionLocal() as session:
        result = session.execute(
            text("SELECT current_database()")
        )
        print("Session opened successfully!")
        print("Database:", result.scalar())

    print("Session closed successfully!")

except SQLAlchemyError:
    print("Database session test failed.")
    print("Check your database connection and configuration.")
