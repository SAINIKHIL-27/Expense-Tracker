import calendar
from datetime import date

import requests
import streamlit as st

API = "http://127.0.0.1:8000/api"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Health", "Entertainment", "Other"]
METHODS = ["UPI", "Cash", "Card", "Net Banking"]

st.set_page_config(page_title="Expense Tracker")


def call(method, path, **kwargs):
    try:
        return requests.request(method, API + path, timeout=5, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error("Backend is not running. Start it with: uvicorn main:app --reload")
        st.stop()


def expense_form(key, e=None):
    """One form used for both Add and Edit. Returns the data when Save is clicked."""
    with st.form(key):
        d = st.date_input("Date", date.fromisoformat(e["expense_date"]) if e else date.today())
        desc = st.text_input("Description", e["description"] if e else "")
        cat = st.selectbox("Category", CATEGORIES,
                           index=CATEGORIES.index(e["category"]) if e and e["category"] in CATEGORIES else 0)
        amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0, value=e["amount"] if e else 0.0)
        pay = st.selectbox("Payment method", METHODS,
                           index=METHODS.index(e["payment_method"]) if e and e["payment_method"] in METHODS else 0)
        notes = st.text_area("Notes (optional)", (e["notes"] or "") if e else "")
        saved = st.form_submit_button("Save")
    if saved:
        return {"expense_date": str(d), "description": desc, "category": cat,
                "amount": str(amt), "payment_method": pay, "notes": notes or None}


def category_table(data):
    return [{"Category": k, "Total (₹)": v} for k, v in data.items()]


# Show a message saved before a rerun
if "msg" in st.session_state:
    st.success(st.session_state.pop("msg"))

st.title("Monthly Expense Tracker")
page = st.sidebar.radio("Go to", ["Dashboard", "Add Expense", "All Expenses",
                                  "Daily Report", "Monthly Report", "Yearly Report"])

# ---------------- Dashboard ----------------
if page == "Dashboard":
    d = call("GET", "/dashboard").json()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Today", f"₹{d['today']}")
    c2.metric("This month", f"₹{d['month']}")
    c3.metric("This year", f"₹{d['year']}")
    c4.metric("Expenses recorded", d["count"])
    st.subheader("Recent expenses")
    if d["recent"]:
        st.dataframe(d["recent"], hide_index=True)
    else:
        st.info("No expenses yet. Use 'Add Expense' in the sidebar.")

# ---------------- Add ----------------
elif page == "Add Expense":
    st.header("Add Expense")
    data = expense_form("add")
    if data:
        r = call("POST", "/expenses", json=data)
        if r.status_code == 201:
            st.session_state["msg"] = "Expense saved!"
            st.rerun()
        else:
            st.error("Rejected: description is required and amount must be greater than 0.")

# ---------------- All expenses + edit + delete ----------------
elif page == "All Expenses":
    st.header("All Expenses (latest first)")
    rows = call("GET", "/expenses").json()
    if not rows:
        st.info("No expenses yet.")
    else:
        st.dataframe(rows, hide_index=True)
        choice = st.selectbox("Select an expense ID to edit or delete", [r["id"] for r in rows])
        e = next(r for r in rows if r["id"] == choice)

        st.subheader("Edit")
        data = expense_form(f"edit_{choice}", e)
        if data:
            r = call("PUT", f"/expenses/{choice}", json=data)
            if r.status_code == 200:
                st.session_state["msg"] = "Expense updated!"
                st.rerun()
            else:
                st.error("Rejected: description is required and amount must be greater than 0.")

        st.subheader("Delete")
        if st.checkbox(f"Yes, I want to delete expense #{choice}"):  # confirmation step
            if st.button("Delete now"):
                call("DELETE", f"/expenses/{choice}")
                st.session_state["msg"] = "Expense deleted!"
                st.rerun()

# ---------------- Daily ----------------
elif page == "Daily Report":
    st.header("Daily Report")
    day = st.date_input("Select a date", date.today())
    r = call("GET", "/reports/daily", params={"day": str(day)}).json()
    c1, c2 = st.columns(2)
    c1.metric("Total spent", f"₹{r['total']}")
    c2.metric("Transactions", r["count"])
    if r["expenses"]:
        st.dataframe(r["expenses"], hide_index=True)
    else:
        st.info("No expenses on this date.")

# ---------------- Monthly ----------------
elif page == "Monthly Report":
    st.header("Monthly Report")
    year = st.number_input("Year", 2000, 2100, date.today().year)
    month = st.selectbox("Month", range(1, 13), index=date.today().month - 1,
                         format_func=lambda m: calendar.month_name[m])
    r = call("GET", "/reports/monthly", params={"year": year, "month": month}).json()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"₹{r['total']}")
    c2.metric("Transactions", r["count"])
    c3.metric("Average per day", f"₹{r['average_daily']}")
    if r["count"]:
        st.subheader("By category")
        st.dataframe(category_table(r["by_category"]), hide_index=True)
        st.subheader("All expenses this month")
        st.dataframe(r["expenses"], hide_index=True)
    else:
        st.info("No expenses in this month.")

# ---------------- Yearly ----------------
elif page == "Yearly Report":
    st.header("Yearly Report")
    year = st.number_input("Year", 2000, 2100, date.today().year)
    r = call("GET", "/reports/yearly", params={"year": year}).json()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total", f"₹{r['total']}")
    c2.metric("Transactions", r["count"])
    c3.metric("Highest month", r["highest_month"] or "-")
    st.subheader("Month by month")
    st.dataframe([{"Month": calendar.month_name[i + 1], "Total (₹)": t}
                  for i, t in enumerate(r["monthly_totals"])], hide_index=True)
    if r["count"]:
        st.subheader("By category")
        st.dataframe(category_table(r["by_category"]), hide_index=True)