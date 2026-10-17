import warnings
from datetime import datetime

from sqlalchemy import Column, Date, DateTime, Integer, Numeric, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

warnings.filterwarnings("ignore")  # hides a harmless SQLite-Decimal warning

engine = create_engine("sqlite:///expenses.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    expense_date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String, nullable=False)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.now)


Base.metadata.create_all(engine)  # creates expenses.db and the table if missing