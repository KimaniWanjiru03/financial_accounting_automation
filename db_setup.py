
import pandas as pd
import sqlite3
import argparse
from pathlib import Path

def init_db(db_path="journal_entries.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        JE_ID TEXT PRIMARY KEY,
        Date TEXT,
        Description TEXT,
        Debit_Account TEXT,
        Debit_Category TEXT,
        Debit_Amount REAL,
        Credit_Account TEXT,
        Credit_Category TEXT,
        Credit_Amount REAL,
        Transaction_Type TEXT,
        Customer_Vendor TEXT,
        Payment_Method TEXT,
        Reference TEXT
    )
    """)
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {db_path}")

if __name__ == "__main__":
    init_db()

