import streamlit as st
import pandas as pd
import io
import os 

from db_io import insert_entries, fetch_entries, init_db
from file_processor import process_uploaded_file
from accounting_analytics import load_data_from_db, AccountingAnalytics
from ocr import OCRExtractor
import tempfile
import openai
from openai import OpenAIError, RateLimitError
from openai import OpenAI

import io
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")



# Ensure DB schema exists
init_db()

# Lazy import OCR (so Streamlit doesn’t fail if Tesseract not installed yet)


def run_ocr(uploaded_doc):

    # Initialize OCR extractor
    extractor = OCRExtractor(api_key=api_key)

    # Save uploaded PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_doc.read())
        tmp_path = tmp.name

    # Extract all entries
    entries = extractor.extract_all_entries(tmp_path)

    # Create DataFrame
    df = pd.DataFrame(entries)

    # ---------------- Robust Cleaning ----------------
    for col in ['Debit', 'Credit']:
        if col in df.columns:
            # Convert all values to string first, strip whitespace
            df[col] = df[col].astype(str).str.strip()
            
            # Remove any commas, currency symbols, or stray characters
            df[col] = df[col].str.replace(r'[^0-9.\-]', '', regex=True)
            
            # Convert to numeric, invalid parsing becomes NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill NaN with 0
            df[col] = df[col].fillna(0)
    return df



# App title
st.set_page_config(page_title="Accounting Pipeline", layout="wide")
st.title("📊 Automated Accounting Pipeline")

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("📁 Data Management")

    upload_choice = st.radio(
        "Choose upload type",
        ["Excel/CSV", "Raw Document (OCR)"]
    )

    if upload_choice == "Excel/CSV":
        uploaded_file = st.file_uploader("Upload Excel/CSV", type=["xlsx", "csv"])
        if uploaded_file:
            df = process_uploaded_file(uploaded_file)
            if df is not None:
                # Convert dates to string format before insertion
                if 'Date' in df.columns:
                    df['Date'] = df['Date'].astype(str)
                
                if insert_entries(df.to_dict(orient="records")):
                    st.success("✅ Excel data successfully added to DB!")
                    # Excel download fallback
                    buffer = io.BytesIO()
                    df.to_excel(buffer, index=False, engine="openpyxl")
                    buffer.seek(0)
                    st.download_button(
                        "⬇️ Download Backup Excel",
                        buffer,
                        file_name="backup.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

    elif upload_choice == "Raw Document (OCR)":
        uploaded_doc = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
        if uploaded_doc:
            with st.spinner("🔍 Extracting data with OCR..."):
                df = run_ocr(uploaded_doc)
                if df is not None:
                    if insert_entries(df.to_dict(orient="records")):
                        st.success("✅ OCR data successfully added to DB!")
                        # Excel download fallback
                        buffer = io.BytesIO()
                        df.to_excel(buffer, index=False, engine="openpyxl")
                        buffer.seek(0)
                        st.download_button(
                            "⬇️ Download Extracted Excel",
                            buffer,
                            file_name="ocr_extract.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

# ---------------- Main Tabs ----------------
st.header("📊 Analytics & Reports")
data = load_data_from_db()

if not data.empty:
    analytics = AccountingAnalytics(data)

    tab0, tab1, tab2, tab3, tab4 = st.tabs(
        ["📑 Data Preview", "📈 KPIs", "📊 Trial Balance", "💰 Income Statement", "📃 Balance Sheet"]
    )

    with tab0:
        st.subheader("📑 Preview of Journal Entries")
        st.dataframe(data, use_container_width=True)

    with tab1:
        st.subheader("📈 Key Performance Indicators")
    
        # Convert Debit and Credit columns to numeric, coercing errors to 0
        data['Debit'] = pd.to_numeric(data['Debit'], errors='coerce').fillna(0)
        data['Credit'] = pd.to_numeric(data['Credit'], errors='coerce').fillna(0)
        
        st.metric("Total Debits", f"{data['Debit'].sum():,.2f}")
        st.metric("Total Credits", f"{data['Credit'].sum():,.2f}")

    with tab2:
        st.subheader("📊 Trial Balance")
        st.dataframe(analytics.trial_balance())

    with tab3:
        st.subheader("💰 Income Statement")
        st.dataframe(analytics.income_statement())

    with tab4:
        st.subheader("📃 Balance Sheet")
        st.dataframe(analytics.balance_sheet())

else:
    st.info("ℹ️ No data available. Please upload Excel/CSV or run OCR on raw documents.")


