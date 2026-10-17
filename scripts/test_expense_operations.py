
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import SessionLocal
from app.models import Expense

session = SessionLocal()
test_expense_id = None

try:
    # Create a test expense.
    expense = Expense(
        expense_date=date(2026, 10, 17),
        description="Test Lunch",
        category="Food",
        amount=Decimal("150.00"),
        payment_method="Cash",
        notes="Temporary test record",
    )

    session.add(expense)
    session.commit()
    session.refresh(expense)

    test_expense_id = expense.id
    print("Expense saved successfully!")
    print("Generated ID:", test_expense_id)

    # Retrieve the saved expense.
    saved_expense = session.get(Expense, test_expense_id)

    if saved_expense:
        print("Expense retrieved successfully!")
        print("Description:", saved_expense.description)
        print("Amount:", saved_expense.amount)

    # Delete the temporary test record.
    session.delete(saved_expense)
    session.commit()
    print("Test expense deleted successfully!")

except Exception as error:
    session.rollback()
    print("Expense operation failed.")
    print(type(error).__name__, error)

finally:
    session.close()
    print("Database session closed.")
