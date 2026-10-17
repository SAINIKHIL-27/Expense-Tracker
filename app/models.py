
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    expense_date: Mapped[date] = mapped_column(
        Date, nullable=False
    )

    description: Mapped[str] = mapped_column(
        String(200), nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    payment_method: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
