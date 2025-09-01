
import pandas as pd
import sqlite3
import argparse
from pathlib import Path

def load_csv_to_sqlite(csv_path: str, db_path: str = "accounting.db", table: str = "transactions"):
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}. Export your DataFrame first (df.to_csv('financial_accounting2.csv', index=False)).")
    # Read CSV and normalize
    df = pd.read_csv(csv_path)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ["Debit", "Credit"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    # Write to SQLite
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table, conn, if_exists="replace", index=False)
    finally:
        conn.close()
    print(f"Loaded {len(df)} rows into {db_path} (table '{table}').")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load a transactions CSV into a SQLite database.")
    parser.add_argument("--csv", default="transactions.csv", help="Path to transactions CSV (exported from your notebook).")
    parser.add_argument("--db", default="accounting.db", help="SQLite database filename to create/update.")
    parser.add_argument("--table", default="transactions", help="Table name (default: transactions).")
    args = parser.parse_args()
    load_csv_to_sqlite(args.csv, args.db, args.table)
