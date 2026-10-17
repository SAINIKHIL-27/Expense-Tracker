# Monthly Expense Tracker

A personal expense tracker built with FastAPI, SQLite and Streamlit.
Record daily spending and view daily, monthly and yearly summaries.

## Features
- Add, edit, delete expenses (with delete confirmation)
- Dashboard: today, this month, this year, recent expenses
- Daily, monthly (with category breakdown, daily average) and yearly reports
- JSON REST API with automatic Swagger docs
- Input validation (amount > 0, required fields)

## Tech stack
Python, FastAPI, SQLAlchemy, SQLite, Streamlit, Uvicorn

## Setup
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run (two terminals)
```
uvicorn main:app --reload
streamlit run app.py
```
App: http://localhost:8501 | API docs: http://127.0.0.1:8000/docs

## Database
Table `expenses`: id, expense_date, description, category, amount, payment_method, notes, created_at

## API endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | /api/expenses | List expenses (optional ?day=) |
| GET | /api/expenses/{id} | One expense |
| POST | /api/expenses | Create |
| PUT | /api/expenses/{id} | Update |
| DELETE | /api/expenses/{id} | Delete |
| GET | /api/reports/daily | Daily totals |
| GET | /api/reports/monthly | Monthly totals |
| GET | /api/reports/yearly | Yearly totals |

## Screenshots
(add screenshots here)

## Future improvements
Login, CSV export, charts, budgets, Docker deployment