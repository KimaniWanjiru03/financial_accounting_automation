
import pandas as pd

class AccountingAnalytics:
    """Core analytics for accounting data.

    Expected columns (case-sensitive):
    Date, Account, Description, Debit, Credit, Category, Transaction_Type, Customer_Vendor, Payment_Method, Reference

    """
    def __init__(self, df: pd.DataFrame):
        df = df.copy()
        # Normalize/parse
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        # Coerce numeric
        for col in ["Debit", "Credit"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        self.df = df

    # ---------- Helpers ----------
    def filter(self, start_date=None, end_date=None, accounts=None, customers=None, txn_types=None, payment_methods=None):
        d = self.df.copy()
        if start_date is not None:
            d = d[d["Date"] >= pd.to_datetime(start_date)]
        if end_date is not None:
            d = d[d["Date"] <= pd.to_datetime(end_date)]
        if accounts:
            d = d[d["Account"].isin(accounts)]
        if customers:
            d = d[d["Customer_Vendor"].isin(customers)]
        if txn_types:
            d = d[d["Transaction_Type"].isin(txn_types)]
        if payment_methods:
            d = d[d["Payment_Method"].isin(payment_methods)]
        return AccountingAnalytics(d)

    # ---------- 1. Trial Balance ----------
    def trial_balance(self):
        if self.df.empty: 
            return pd.DataFrame(columns=["Account", "Debit", "Credit", "Balance"])
        tb = self.df.groupby("Account")[["Debit", "Credit"]].sum().reset_index()
        tb["Balance"] = tb["Debit"] - tb["Credit"]
        tb = tb.sort_values("Account").reset_index(drop=True)
        return tb

    # ---------- 2. Income Statement ----------
    def income_statement(self):
        revenue = self.df[self.df["Category"] == "Revenue"]["Credit"].sum()
        expenses = self.df[self.df["Category"] == "Expense"]["Debit"].sum()
        net_profit = revenue - expenses
        return pd.DataFrame({
            "Category": ["Revenue", "Expenses", "Net Profit"],
            "Amount": [revenue, expenses, net_profit]
        })

    # ---------- 3. Balance Sheet ----------
    def balance_sheet(self):
        assets = self.df[self.df["Category"] == "Asset"]
        liabilities = self.df[self.df["Category"] == "Liability"]

        total_assets = assets["Debit"].sum() - assets["Credit"].sum()
        total_liabilities = liabilities["Credit"].sum() - liabilities["Debit"].sum()
        equity = total_assets - total_liabilities

        return pd.DataFrame({
            "Category": ["Assets", "Liabilities", "Equity"],
            "Amount": [total_assets, total_liabilities, equity]
        })

    # ---------- 4. Cash Flow (simplified, cash-based) ----------
    def cash_flow(self):
        # Treat Payment_Method == 'Cash' as affecting cash
        cash_txn = self.df[self.df["Payment_Method"] == "Cash"]
        inflows = cash_txn["Debit"].sum()   # cash increases on debits
        outflows = cash_txn["Credit"].sum() # cash decreases on credits
        net_cash = inflows - outflows
        return pd.DataFrame({
            "Category": ["Cash Inflows", "Cash Outflows", "Net Cash Flow"],
            "Amount": [inflows, outflows, net_cash]
        })

    # ---------- 5. Aging Report ----------
    def aging_report(self, account_name="Accounts Receivable"):
        d = self.df[self.df["Account"] == account_name].copy()
        if d.empty:
            return pd.DataFrame(columns=["Aging_Bucket", "Amount"])
        today = pd.Timestamp.today().normalize()
        d["Days_Outstanding"] = (today - d["Date"]).dt.days
        bins = [0, 30, 60, 90, 120, 10_000]
        labels = ["0-30", "31-60", "61-90", "91-120", "120+"]
        d["Aging_Bucket"] = pd.cut(d["Days_Outstanding"], bins=bins, labels=labels, right=True, include_lowest=True)
        # For AR typically the outstanding 'amount' would be the open balance; here we approximate with Debit
        out = d.groupby("Aging_Bucket")["Debit"].sum().reset_index()
        return out

    # ---------- 6. Transaction Drill-down ----------
    def drill_down(self, account=None, customer=None, txn_type=None, date_from=None, date_to=None):
        return self.filter(start_date=date_from, end_date=date_to,
                           accounts=[account] if account else None,
                           customers=[customer] if customer else None,
                           txn_types=[txn_type] if txn_type else None).df

    # ---------- 7. Error Checks ----------
    def error_checks(self):
        result = {}
        # Trial balance check
        deb_sum = float(self.df["Debit"].sum())
        cred_sum = float(self.df["Credit"].sum())
        result["trial_balance_status"] = "✅ Balanced" if abs(deb_sum - cred_sum) < 1e-6 else "❌ Not Balanced"
        result["total_debits"] = deb_sum
        result["total_credits"] = cred_sum
        # Per-row balance flag
        tmp = self.df.copy()
        tmp["Balanced_Row"] = (tmp["Debit"].round(2) == tmp["Credit"].round(2))
        result["unbalanced_entries"] = tmp[~tmp["Balanced_Row"]].drop(columns=["Balanced_Row"])
        # Simple anomalies
        anomalies = self.df[(self.df["Debit"] < 0) | (self.df["Credit"] < 0) | (self.df["Category"].isna())]
        result["anomalies"] = anomalies
        return result
