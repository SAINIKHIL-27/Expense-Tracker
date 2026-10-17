
import sys
from pathlib import Path

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import Base, engine
from app.models import Expense

try:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print("Table created or already exists: expenses")

except Exception as error:
    print("Failed to create database tables.")
    print(error)
