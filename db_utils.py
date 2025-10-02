import sqlite3
import pandas as pd
from pathlib import Path

def init_database(db_path="accounting.db"):
    """Initialize database with required tables"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create transactions table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    return True

def insert_dataframe_to_db(df, db_path="accounting.db", table_name="transactions"):
    """Insert a DataFrame into the database"""
    init_database(db_path)
    
    conn = sqlite3.connect(db_path)
    try:
        df.to_sql(table_name, conn, if_exists="append", index=False)
        return True
    except Exception as e:
        print(f"Error inserting data: {e}")
        return False
    finally:
        conn.close()

def get_all_data(db_path="accounting.db", table_name="transactions"):
    """Retrieve all data from the database"""
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        return df
    except Exception as e:
        print(f"Error retrieving data: {e}")
        return pd.DataFrame()
    finally:
        conn.close()