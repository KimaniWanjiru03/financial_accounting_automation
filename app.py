
import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path

from accounting_analytics import AccountingAnalytics

st.set_page_config(page_title="Accounting Dashboard", layout="wide")

st.title("📚 Accounting Analytics Dashboard")
st.caption("Trial Balance • Income Statement • Balance Sheet • Cash Flow • Aging • Drill-down • Error checks")

# ---- Data source ----
db_path = st.sidebar.text_input("SQLite DB path", value="accounting.db")
table_name = st.sidebar.text_input("Table name", value="transactions")

@st.cache_data(show_spinner=False)
def load_df(db_path: str, table_name: str):
    p = Path(db_path)
    if not p.exists():
        st.error(f"Database not found: {p}")
        st.stop()
    conn = sqlite3.connect(p.as_posix())
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Debit", "Credit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df

df = load_df(db_path, table_name)

# ---- Sidebar filters ----
st.sidebar.header("Filters")
min_date = pd.to_datetime(df["Date"]).min()
max_date = pd.to_datetime(df["Date"]).max()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date))

accounts = sorted([a for a in df["Account"].dropna().unique()])
customers = sorted([c for c in df["Customer_Vendor"].dropna().unique()])
txn_types = sorted([t for t in df["Transaction_Type"].dropna().unique()])
pay_methods = sorted([p for p in df["Payment_Method"].dropna().unique()])

sel_accounts = st.sidebar.multiselect("Accounts", accounts, default=[])
sel_customers = st.sidebar.multiselect("Customers/Vendors", customers, default=[])
sel_txn_types = st.sidebar.multiselect("Transaction Types", txn_types, default=[])
sel_pay_methods = st.sidebar.multiselect("Payment Methods", pay_methods, default=[])

# Apply filters using the analytics class
analytics = AccountingAnalytics(df)
analytics = analytics.filter(
    start_date=date_range[0] if isinstance(date_range, (list, tuple)) else min_date,
    end_date=date_range[1] if isinstance(date_range, (list, tuple)) else max_date,
    accounts=sel_accounts or None,
    customers=sel_customers or None,
    txn_types=sel_txn_types or None,
    payment_methods=sel_pay_methods or None
)

filtered = analytics.df

# ---- KPI Row ----
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Debits", f"${filtered['Debit'].sum():,.2f}")
with col2:
    st.metric("Total Credits", f"${filtered['Credit'].sum():,.2f}")
is_df = analytics.income_statement()
with col3:
    st.metric("Revenue", f"${float(is_df.loc[is_df['Category']=='Revenue','Amount']):,.2f}")
with col4:
    st.metric("Net Profit", f"${float(is_df.loc[is_df['Category']=='Net Profit','Amount']):,.2f}")

st.divider()

# ---- Tabs ----
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Trial Balance", "Income Statement", "Balance Sheet", "Cash Flow", "Aging", "Transactions", "Error Checks"
])

with tab1:
    st.subheader("Trial Balance")
    st.dataframe(analytics.trial_balance(), use_container_width=True)

with tab2:
    st.subheader("Income Statement")
    st.dataframe(is_df, use_container_width=True)

with tab3:
    st.subheader("Balance Sheet")
    st.dataframe(analytics.balance_sheet(), use_container_width=True)

with tab4:
    st.subheader("Cash Flow (cash-based, simplified)")
    st.dataframe(analytics.cash_flow(), use_container_width=True)

with tab5:
    st.subheader("Aging Report")
    aging_account = st.selectbox("Account", ["Accounts Receivable", "Accounts Payable"])
    st.dataframe(analytics.aging_report(aging_account), use_container_width=True)

with tab6:
    st.subheader("Transaction Drill-down")
    st.dataframe(filtered, use_container_width=True)
    st.download_button("Download filtered CSV", data=filtered.to_csv(index=False), file_name="filtered_transactions.csv")

with tab7:
    st.subheader("Error Checks")
    ec = analytics.error_checks()
    st.write(f"Trial Balance: **{ec['trial_balance_status']}**")
    st.write(f"Total Debits: ${ec['total_debits']:,.2f} • Total Credits: ${ec['total_credits']:,.2f}")
    st.markdown("**Unbalanced Entries**")
    st.dataframe(ec["unbalanced_entries"], use_container_width=True)
    st.markdown("**Anomalies (negatives or missing category)**")
    st.dataframe(ec["anomalies"], use_container_width=True)

st.caption("Tip: Update your CSV → re-run db_setup.py → refresh this app to see new data.")
