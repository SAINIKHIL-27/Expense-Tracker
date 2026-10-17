import calendar
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Expense, SessionLocal

app = FastAPI(title="Monthly Expense Tracker")


# ---------- Validation (Pydantic) ----------
class ExpenseIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    expense_date: date
    description: str = Field(min_length=1)
    category: str = Field(min_length=1)
    amount: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    payment_method: str = Field(min_length=1)
    notes: Optional[str] = None


# ---------- Helpers ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def to_dict(e):
    return {
        "id": e.id,
        "expense_date": str(e.expense_date),
        "description": e.description,
        "category": e.category,
        "amount": float(e.amount),
        "payment_method": e.payment_method,
        "notes": e.notes,
    }


def expenses_where(db, *filters, limit=None):
    q = db.query(Expense).filter(*filters)
    q = q.order_by(Expense.expense_date.desc(), Expense.id.desc())  # latest first
    if limit:
        q = q.limit(limit)
    return [to_dict(e) for e in q.all()]


def totals(db, *filters):
    total, count = db.query(
        func.coalesce(func.sum(Expense.amount), 0), func.count(Expense.id)
    ).filter(*filters).one()
    return round(float(total), 2), count


def by_category(db, *filters):
    total = func.sum(Expense.amount)
    rows = (db.query(Expense.category, total).filter(*filters)
            .group_by(Expense.category).order_by(total.desc()).all())
    return {cat: round(float(t), 2) for cat, t in rows}


def month_filter(year, month):
    start = date(year, month, 1)
    end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return [Expense.expense_date >= start, Expense.expense_date < end]


def year_filter(year):
    return [Expense.expense_date >= date(year, 1, 1), Expense.expense_date < date(year + 1, 1, 1)]


# ---------- Expense endpoints (CRUD) ----------
@app.get("/api/expenses")
def list_expenses(day: Optional[date] = None, db: Session = Depends(get_db)):
    filters = [Expense.expense_date == day] if day else []
    return expenses_where(db, *filters)


@app.get("/api/expenses/{expense_id}")
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    e = db.get(Expense, expense_id)
    if not e:
        raise HTTPException(404, "Expense not found")
    return to_dict(e)


@app.post("/api/expenses", status_code=201)
def create_expense(data: ExpenseIn, db: Session = Depends(get_db)):
    e = Expense(**data.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return to_dict(e)


@app.put("/api/expenses/{expense_id}")
def update_expense(expense_id: int, data: ExpenseIn, db: Session = Depends(get_db)):
    e = db.get(Expense, expense_id)
    if not e:
        raise HTTPException(404, "Expense not found")
    for field, value in data.model_dump().items():
        setattr(e, field, value)
    db.commit()
    return to_dict(e)


@app.delete("/api/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    e = db.get(Expense, expense_id)
    if not e:
        raise HTTPException(404, "Expense not found")
    db.delete(e)
    db.commit()
    return {"message": "Deleted"}


# ---------- Reports ----------
@app.get("/api/reports/daily")
def daily_report(day: date, db: Session = Depends(get_db)):
    f = [Expense.expense_date == day]
    total, count = totals(db, *f)
    return {"date": str(day), "total": total, "count": count, "expenses": expenses_where(db, *f)}


@app.get("/api/reports/monthly")
def monthly_report(year: int = Query(ge=2000, le=2100), month: int = Query(ge=1, le=12),
                   db: Session = Depends(get_db)):
    f = month_filter(year, month)
    total, count = totals(db, *f)
    days = calendar.monthrange(year, month)[1]
    return {
        "year": year, "month": month, "total": total, "count": count,
        "average_daily": round(total / days, 2),
        "by_category": by_category(db, *f),
        "expenses": expenses_where(db, *f),
    }


@app.get("/api/reports/yearly")
def yearly_report(year: int = Query(ge=2000, le=2100), db: Session = Depends(get_db)):
    f = year_filter(year)
    total, count = totals(db, *f)
    month_col = func.strftime("%m", Expense.expense_date)
    rows = db.query(month_col, func.sum(Expense.amount)).filter(*f).group_by(month_col).all()
    monthly = [0.0] * 12
    for m, t in rows:
        monthly[int(m) - 1] = round(float(t), 2)
    highest = calendar.month_name[monthly.index(max(monthly)) + 1] if max(monthly) > 0 else None
    return {"year": year, "total": total, "count": count, "monthly_totals": monthly,
            "highest_month": highest, "by_category": by_category(db, *f)}


# ---------- Dashboard ----------
@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    t = date.today()  # calculated dynamically, never hardcoded
    return {
        "today": totals(db, Expense.expense_date == t)[0],
        "month": totals(db, *month_filter(t.year, t.month))[0],
        "year": totals(db, *year_filter(t.year))[0],
        "count": db.query(func.count(Expense.id)).scalar(),
        "recent": expenses_where(db, limit=5),
    }