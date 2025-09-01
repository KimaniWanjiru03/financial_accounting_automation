
# Accounting Analytics App (Step-by-Step)

This mini project takes you from **DataFrame in Jupyter** → **SQLite DB** → **Streamlit dashboard**.

## 0) Export your DataFrame to CSV (from your notebook)

```python
# In your Finance_accounting_automation.ipynb
df.to_csv("financial_accounting.csv", index=False)
```

This creates `financial_accounting.csv` in the current working directory.

## 1) Create the SQLite database

```bash
# Navigate to the project folder
cd accounting_app

# (Optional) Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Load your CSV into SQLite
python db_setup.py --csv ../transactions.csv --db accounting.db --table transactions
```
> Adjust the `--csv` path if your CSV is elsewhere.

## 2) Run the Streamlit app

```bash
streamlit run app.py
```

- In the sidebar, keep `accounting.db` and `transactions` unless you changed them.
- Use the filters (date, accounts, customers, etc.).
- Explore the tabs: Trial Balance, Income Statement, Balance Sheet, Cash Flow, Aging, Transactions, Error Checks.

## Notes
- The **Cash Flow** tab uses a simplified approach: rows where `Payment_Method == "Cash"` are treated as affecting cash. Debits = inflows, Credits = outflows.
- The **Aging Report** is date-driven; it uses the **Date** column to compute days outstanding and buckets the **Debit** side for AR/AP as an approximation.
- Error checks include overall trial balance equality, per-row balance flags, and simple anomaly checks (negative values, missing categories).

## Troubleshooting
- If the app says it can't find the DB, ensure you've run the `db_setup.py` step and that `accounting.db` is in the same folder as `app.py` (or adjust the sidebar path).
- If dates look odd, confirm your CSV `Date` column is in `YYYY-MM-DD` format.

Happy building!
