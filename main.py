import streamlit as st
import pandas as pd
from datetime import datetime

from accounting_analytics import AccountingAnalytics
from db_utils import init_database, insert_dataframe_to_db, get_all_data
from file_processor import process_uploaded_file

# Page configuration
st.set_page_config(
    page_title="Accounting Analytics Dashboard", 
    layout="wide",
    page_icon="📊"
)

# Initialize database
init_database()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<p class="main-header">📊 Accounting Analytics Dashboard</p>', unsafe_allow_html=True)
st.caption("Upload your accounting data, visualize financial statements, and analyze transactions")

# Sidebar for data upload and filters
with st.sidebar:
    st.header("📁 Data Management")
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Upload Accounting Data", 
        type=["xlsx", "csv"],
        help="Upload Excel or CSV file with accounting transactions"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing your file..."):
            processed_df = process_uploaded_file(uploaded_file)
            
            if processed_df is not None:
                success = insert_dataframe_to_db(processed_df)
                if success:
                    st.success("Data successfully uploaded to database!")
                else:
                    st.error("Failed to upload data to database.")
    
    st.divider()
    
    # Filters section
    st.header("🔍 Filters")
    
    # Load data from database
    df = get_all_data()
    
    if not df.empty:
        min_date = pd.to_datetime(df["Date"]).min()
        max_date = pd.to_datetime(df["Date"]).max()
        
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        accounts = sorted([a for a in df["Account"].dropna().unique() if a])
        customers = sorted([c for c in df["Customer_Vendor"].dropna().unique() if c])
        txn_types = sorted([t for t in df["Transaction_Type"].dropna().unique() if t])
        pay_methods = sorted([p for p in df["Payment_Method"].dropna().unique() if p])
        
        sel_accounts = st.multiselect("Accounts", accounts, default=[])
        sel_customers = st.multiselect("Customers/Vendors", customers, default=[])
        sel_txn_types = st.multiselect("Transaction Types", txn_types, default=[])
        sel_pay_methods = st.multiselect("Payment Methods", pay_methods, default=[])
    else:
        st.info("Upload data to enable filters")
        date_range = None
        sel_accounts = sel_customers = sel_txn_types = sel_pay_methods = None
        df = pd.DataFrame()

# Main content area
if df.empty:
    # Show welcome message and instructions if no data
    st.info("👆 Upload an Excel or CSV file to get started")
    
    with st.expander("📋 Expected File Format"):
        st.markdown("""
        Your file should include these columns (case-sensitive):
        
        - **Date**: Transaction date
        - **Account**: Account name (e.g., "Cash", "Accounts Receivable")
        - **Description**: Transaction description
        - **Debit**: Debit amount
        - **Credit**: Credit amount
        - **Category**: Account category (e.g., "Asset", "Liability", "Revenue", "Expense")
        - **Transaction_Type**: Type of transaction
        - **Customer_Vendor**: Customer or vendor name
        - **Payment_Method**: Payment method used
        - **Reference**: Transaction reference number
        """)
        
    st.divider()
    st.subheader("Sample Data Format")
    sample_data = {
        "Date": ["2023-01-15", "2023-01-16", "2023-01-17"],
        "Account": ["Cash", "Accounts Receivable", "Office Supplies"],
        "Description": ["Client Payment", "Sale to ABC Corp", "Purchase pens and paper"],
        "Debit": [1000.00, 500.00, 45.50],
        "Credit": [0.00, 0.00, 0.00],
        "Category": ["Asset", "Asset", "Expense"],
        "Transaction_Type": ["Payment", "Sale", "Purchase"],
        "Customer_Vendor": ["John Smith", "ABC Corp", "Office Depot"],
        "Payment_Method": ["Bank Transfer", "Credit", "Cash"],
        "Reference": ["INV-001", "INV-002", "PUR-001"]
    }
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
    
else:
    # Apply filters using the analytics class
    analytics = AccountingAnalytics(df)
    analytics = analytics.filter(
        start_date=date_range[0] if date_range else None,
        end_date=date_range[1] if date_range else None,
        accounts=sel_accounts or None,
        customers=sel_customers or None,
        txn_types=sel_txn_types or None,
        payment_methods=sel_pay_methods or None
    )

    filtered = analytics.df

    # KPI Metrics
    st.markdown("## 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Debits", f"${filtered['Debit'].sum():,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Total Credits", f"${filtered['Credit'].sum():,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    is_df = analytics.income_statement()
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Revenue", f"${float(is_df.loc[is_df['Category']=='Revenue','Amount']):,.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        net_profit = float(is_df.loc[is_df['Category']=='Net Profit','Amount'])
        profit_color = "green" if net_profit >= 0 else "red"
        st.metric("Net Profit", f"${net_profit:,.2f}", delta_color="off")
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Tabs for different reports
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Trial Balance", "💰 Income Statement", "🏦 Balance Sheet", 
        "💵 Cash Flow", "⏰ Aging", "🔍 Transactions", "✅ Error Checks"
    ])

    with tab1:
        st.markdown("### Trial Balance")
        tb_df = analytics.trial_balance()
        st.dataframe(tb_df, use_container_width=True)
        
        # Add download button
        st.download_button(
            "Download Trial Balance as CSV",
            data=tb_df.to_csv(index=False),
            file_name="trial_balance.csv",
            mime="text/csv"
        )

    with tab2:
        st.markdown("### Income Statement")
        st.dataframe(is_df, use_container_width=True)
        
        # Simple visualization
        if not is_df.empty:
            viz_data = is_df[is_df['Category'].isin(['Revenue', 'Expenses'])]
            st.bar_chart(viz_data.set_index('Category')['Amount'])

    with tab3:
        st.markdown("### Balance Sheet")
        bs_df = analytics.balance_sheet()
        st.dataframe(bs_df, use_container_width=True)
        
        # Balance sheet check
        assets = float(bs_df.loc[bs_df['Category']=='Assets','Amount'])
        liabilities = float(bs_df.loc[bs_df['Category']=='Liabilities','Amount'])
        equity = float(bs_df.loc[bs_df['Category']=='Equity','Amount'])
        
        if abs(assets - (liabilities + equity)) < 0.01:
            st.success("✅ Balance Sheet is balanced")
        else:
            st.error("❌ Balance Sheet is not balanced")

    with tab4:
        st.markdown("### Cash Flow Statement")
        cf_df = analytics.cash_flow()
        st.dataframe(cf_df, use_container_width=True)

    with tab5:
        st.markdown("### Aging Report")
        aging_account = st.selectbox("Select Account", ["Accounts Receivable", "Accounts Payable"])
        aging_df = analytics.aging_report(aging_account)
        
        if not aging_df.empty:
            st.dataframe(aging_df, use_container_width=True)
            st.bar_chart(aging_df.set_index('Aging_Bucket')['Debit'])
        else:
            st.info(f"No data available for {aging_account}")

    with tab6:
        st.markdown("### Transaction Details")
        st.dataframe(filtered, use_container_width=True)
        
        # Add search functionality
        search_term = st.text_input("Search transactions...")
        if search_term:
            search_results = filtered[filtered.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
            st.dataframe(search_results, use_container_width=True)
        
        st.download_button(
            "Download Filtered Transactions as CSV",
            data=filtered.to_csv(index=False),
            file_name="filtered_transactions.csv",
            mime="text/csv"
        )

    with tab7:
        st.markdown("### Error Checks")
        ec = analytics.error_checks()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Trial Balance Status")
            if "✅" in ec["trial_balance_status"]:
                st.success(ec["trial_balance_status"])
            else:
                st.error(ec["trial_balance_status"])
                
            st.write(f"**Total Debits:** ${ec['total_debits']:,.2f}")
            st.write(f"**Total Credits:** ${ec['total_credits']:,.2f}")
            
        with col2:
            if not ec["unbalanced_entries"].empty:
                st.warning(f"⚠️ {len(ec['unbalanced_entries'])} unbalanced entries found")
            else:
                st.success("✅ All entries are balanced")
                
            if not ec["anomalies"].empty:
                st.warning(f"⚠️ {len(ec['anomalies'])} anomalies found")
            else:
                st.success("✅ No anomalies detected")
        
        st.markdown("#### Unbalanced Entries")
        st.dataframe(ec["unbalanced_entries"], use_container_width=True)
        
        st.markdown("#### Anomalies")
        st.dataframe(ec["anomalies"], use_container_width=True)

# Footer
st.divider()
st.caption("Accounting Analytics Dashboard | Built with Streamlit")