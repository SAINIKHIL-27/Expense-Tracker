
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load .env from the project root.
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# Read database settings.
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT", "5432")

# Check that required settings exist.
if not all([db_user, db_password, db_host, db_name]):
    raise RuntimeError(
        "Missing database settings. Check your .env file."
    )

# Build the connection URL safely.
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_host,
    port=int(db_port),
    database=db_name,
)

# Create the SQLAlchemy engine.
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

# Create a factory for database sessions.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

# Parent class for our database models.
class Base(DeclarativeBase):
    pass
