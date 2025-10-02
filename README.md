# Accounting Automation System

## 📊 Overview

A comprehensive accounting automation platform that streamlines financial data processing through AI-powered OCR, automated double-entry accounting, and real-time analytics. This system transforms manual accounting workflows into efficient digital processes suitable for businesses, freelancers, and accounting professionals.

## ✨ Features

- **🤖 AI-Powered OCR**: Extract financial data from invoices, receipts, and documents using OpenAI GPT
- **📊 Automated Accounting**: Intelligent double-entry journal entry generation
- **📈 Real-time Analytics**: Instant financial statements and KPI dashboards
- **🔄 Multi-Format Support**: Process Excel, CSV, PDF, and image files
- **🔍 Error Detection**: Automatic balance validation and anomaly checks
- **💾 SQLite Database**: Robust data storage and management
- **🌐 Web Interface**: User-friendly Streamlit dashboard

## 🏗️ System Architecture

```
Raw Documents (PDF/Images)  →  OCR Processing  →  Structured Data  →  Database
      ↓
Excel/CSV Files  →  File Processing  →  Validation & Cleaning  →  Database
      ↓
              Analytics Engine  →  Financial Reports  →  Web Dashboard
```

## 📁 Project Structure

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit web application dashboard |
| `main.py` | Alternative comprehensive dashboard |
| `db_io.py` | Database operations (insert, fetch, initialization) |
| `db_setup.py` | Database schema setup and initialization |
| `db_utils.py` | Additional database utility functions |
| `file_processor.py` | Excel/CSV file processing and validation |
| `ocr.py` | OCR extraction using OpenAI API |
| `pipeline.py` | Standalone OCR processing pipeline |
| `accounting_analytics.py` | Core accounting logic and analytics |
| `requirements.txt` | Python dependencies |

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (for OCR features)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd accounting-automation
```

2. **Create and activate virtual environment**
```bash
# Create virtual environment
python -m venv accounting_env

# Activate on Mac/Linux
source accounting_env/bin/activate

# Activate on Windows
# accounting_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**
   - Update `API_KEY` in `ocr.py` with your OpenAI API key
   - Or set environment variable: `OPENAI_API_KEY=your_key_here`

5. **Launch the application**
```bash
streamlit run app.py
```

6. **Access the dashboard**
   - Open your browser to: http://localhost:8501
   - For network access: http://192.168.x.x:8501

## 📖 Usage Guide

### Uploading Data

#### Option A: Excel/CSV Files
1. Select "Excel/CSV" in sidebar
2. Upload file with required columns:
   - `Date`, `Account`, `Description`, `Debit`, `Credit`
   - `Category`, `Transaction_Type`, `Customer_Vendor`, `Payment_Method`, `Reference`

#### Option B: Document OCR
1. Select "Raw Document (OCR)" in sidebar
2. Upload PDF, PNG, JPG, or JPEG files
3. System automatically extracts and structures financial data
4. Review and confirm extracted entries

### Analytics & Reports

- **📑 Data Preview**: Raw transaction overview
- **📈 KPIs**: Key financial metrics and totals
- **📊 Trial Balance**: Account balances and verification
- **💰 Income Statement**: Revenue, expenses, and net profit
- **📃 Balance Sheet**: Assets, liabilities, and equity

## 🔧 Troubleshooting

### Common Issues

**Port already in use:**
```bash
streamlit run app.py --server.port 8502
```

**Database errors:**
```bash
# Reset database
rm accounting.db
streamlit run app.py  # Recreates fresh database
```

**Reactivating environment:**
```bash
cd accounting-automation
source accounting_env/bin/activate  # Mac/Linux
streamlit run app.py
```

**Package conflicts:**
```bash
pip install --upgrade -r requirements.txt
```

### Restarting the Application

1. **Stop the server**: Press `Ctrl+C` in terminal
2. **Restart**: `streamlit run app.py`
3. **Alternative dashboard**: `streamlit run main.py`

## 🗃️ Database Schema

The system uses SQLite with the following main table:

```sql
journal_entries (
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
```

## 🔒 Security Notes

- API keys are stored in code files (consider using environment variables for production)
- Database is local SQLite file
- No external data transmission except OpenAI API calls for OCR

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check troubleshooting section above
2. Ensure all dependencies are installed
3. Verify database file exists and is accessible
4. Confirm OpenAI API key is valid and has credits

---

**Happy Accounting!** 🎉
