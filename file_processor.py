import pandas as pd
import streamlit as st
from datetime import datetime

def process_uploaded_file(uploaded_file):
    """Process uploaded Excel or CSV file"""
    try:
        if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xls'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload Excel or CSV.")
            return None
        
        # Validate required columns
        required_columns = ["Date", "Account", "Description", "Debit", "Credit", 
                           "Category", "Transaction_Type", "Customer_Vendor", 
                           "Payment_Method", "Reference"]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None
        
        # Convert date column and format as string
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            # Convert to string format for database storage
            df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
        
        # Convert numeric columns
        for col in ["Debit", "Credit"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        
        # Generate JE_ID if not present
        if "JE_ID" not in df.columns:
            import uuid
            df["JE_ID"] = [f"JE-{uuid.uuid4().hex[:8]}" for _ in range(len(df))]
                
        return df
        
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None