# db_io.py
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "journal_entries.db"

def init_db():
    conn = sqlite3.connect("accounting.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        JE_ID TEXT,
        Date TEXT,
        Account TEXT,
        Description TEXT,
        Debit REAL,
        Credit REAL,
        Category TEXT,
        Transaction_Type TEXT,
        Customer_Vendor TEXT,
        Payment_Method TEXT,
        Reference TEXT,
        PRIMARY KEY (JE_ID, Date, Account, Debit, Credit)
    )
    """)
    
    conn.commit()
    conn.close()

# ---------- Insert ----------
def insert_entries(entries, db_path="accounting.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if it doesn't exist with correct schema
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal_entries (
        JE_ID TEXT,
        Date TEXT,
        Account TEXT,
        Description TEXT,
        Debit REAL,
        Credit REAL,
        Category TEXT,
        Transaction_Type TEXT,
        Customer_Vendor TEXT,
        Payment_Method TEXT,
        Reference TEXT,
        PRIMARY KEY (JE_ID, Date, Account, Debit, Credit)
    )
    """)

    rows_to_insert = []
    for e in entries:
        # Handle JE_ID - generate if not present
        je_id = e.get("JE_ID")
        if not je_id:
            import uuid
            je_id = f"JE-{uuid.uuid4().hex[:8]}"
        
        # Convert date to string format - FIX FOR TIMESTAMP ISSUE
        date_value = e.get("Date")
        if hasattr(date_value, 'strftime'):  # If it's a date-like object
            date_value = date_value.strftime("%Y-%m-%d")
        elif date_value is None:
            date_value = ""
        else:
            date_value = str(date_value)
        
        # Convert numeric fields safely
        debit = pd.to_numeric(e.get("Debit", 0), errors='coerce') or 0
        credit = pd.to_numeric(e.get("Credit", 0), errors='coerce') or 0

        rows_to_insert.append((
            je_id,
            date_value,  # Now properly converted to string
            e.get("Account"),
            e.get("Description"),
            debit,
            credit,
            e.get("Category"),
            e.get("Transaction_Type"),
            e.get("Customer_Vendor"),
            e.get("Payment_Method"),
            e.get("Reference")
        ))

    # Insert new rows with conflict handling
    if rows_to_insert:
        cursor.executemany("""
            INSERT OR IGNORE INTO journal_entries (
                JE_ID, Date, Account, Description, Debit, Credit, 
                Category, Transaction_Type, Customer_Vendor, Payment_Method, Reference
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, rows_to_insert)
        conn.commit()

    conn.close()
    return True

# ---------- Fetch ----------
def fetch_entries(db_path="accounting.db"):
    conn = sqlite3.connect(db_path)
    
    # Check if table exists first
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='journal_entries'
    """)
    table_exists = cursor.fetchone()
    
    if not table_exists:
        conn.close()
        return pd.DataFrame()
    
    df = pd.read_sql("SELECT * FROM journal_entries", conn)
    conn.close()

    # Ensure numeric columns are properly converted
    for col in ['Debit', 'Credit']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df


# ---------- Delete / Reset ----------
def reset_db(db_path=DB_PATH):
    """Clear the journal_entries table (useful for testing)."""
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM journal_entries")
    conn.commit()
    conn.close()
    print("🗑️ Cleared journal_entries table")

if __name__ == "__main__":
    # Example test
    dummy_entries = [
        {
            "Date": "2025-09-25",
            "Description": "Invoice 001",
            "Debit_Account": "Accounts Receivable",
            "Debit_Category": "Asset",
            "Debit_Amount": 1000,
            "Credit_Account": "Revenue",
            "Credit_Category": "Revenue",
            "Credit_Amount": 1000,
            "Transaction_Type": "Invoice",
            "Customer_Vendor": "Client A",
            "Payment_Method": None,
            "Reference": "INV-001"
        }
    ]
    insert_entries(dummy_entries)
    print(fetch_entries().head())
