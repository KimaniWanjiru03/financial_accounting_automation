import pdfplumber
import json
from openai import OpenAI

class OCRExtractor:
    def __init__(self, api_key, model="gpt-4o-mini", temperature=0.2):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature

    # 1. Extract text from PDF
    def extract_text_from_pdf(self, pdf_path):
        texts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    texts.append((page_num, page_text))
        return texts   # list of (page_num, text)

    # 2. Build prompt
    def prompt_source_document(self, text):
        return f"""
        You are an expert accounting assistant.  
        You are given the text extracted from a financial source document
        (such as invoice, receipt, credit note, debit note, purchase order, 
        bank statement, deposit slip, check, or cash register receipt).  

        Your task:
        1. Identify the type of source document.  
        2. Extract transaction details into structured journal entries.  
        3. Apply **basic double-entry accounting rules** to assign Debit and Credit correctly.  
            ⚠️ Debit must always equal Credit for each JE_ID.  
        4. For each transaction, generate a unique Journal Entry ID (e.g., JE-001, JE-002).  
        Both the Debit and Credit lines for the same transaction must share the same JE_ID.  
    

        ### Double-entry rules (simplified):
        - Sales Invoice: Debit Accounts Receivable (Asset), Credit Revenue  
        - Sales Receipt (Cash Sale): Debit Cash (Asset), Credit Revenue  
        - Purchase Invoice (from supplier): Debit Expense or Inventory, Credit Accounts Payable (Liability)  
        - Payment to Supplier: Debit Accounts Payable, Credit Cash  
        - Credit Note (to customer): Debit Revenue (reduce), Credit Accounts Receivable  
        - Debit Note (to supplier): Debit Accounts Payable (reduce), Credit Expense or Inventory  
        - Bank Deposit Slip: Debit Cash, Credit Accounts Receivable or Revenue (depending on context)  
        - Bank Statement Charge (e.g., bank fee): Debit Expense, Credit Cash  
        - Check Issued: Debit Accounts Payable or Expense, Credit Cash 

        Schema (Excel columns):  
        - JE_ID: (Journal Entry ID, e.g., JE-001) 
        - Date: (format as YYYY-MM-DD)  
        - Account: (if specified okay, otherwise chosen from 
            Accounts Payable, Accounts Receivable, Cash, Inventory, etc)  
        - Description: (short summary of the transaction)  
        - Debit: (numeric only, leave blank if not applicable)  
        - Credit: (numeric only, leave blank if not applicable)  
        - Category: (must be chosen from: Asset, Liability, Revenue, Expense, Equity)  
        - Transaction_Type: (Invoice, Receipt, Credit Note, Debit Note, Purchase Order, 
        Bank Statement, Deposit, Check, Cash Receipt)  
        - Customer_Vendor: (name of customer/vendor/party, if available)  
        - Payment_Method: (Cash, Bank Transfer, Credit Card, Check, etc., if available)  
        - Reference: (Invoice number, receipt number, check number, transaction ID, etc.)  

        5. If the document contains multiple transactions (e.g., a bank statement), 
        generate a separate JE_ID for each transaction.

        ⚠️ Return only valid JSON (array of objects), no explanation or markdown formatting.
        Document text:
        {text}
        """

    # 3. Call LLM for a single page
    def extract_journal_entries_from_page(self, page_text):
        prompt = self.prompt_source_document(page_text)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        raw_output = response.choices[0].message.content.strip()

        try:
            entries = json.loads(raw_output)
        except json.JSONDecodeError:
            print("⚠️ JSON decode failed, raw output was:")
            print(raw_output)
            return []

        if isinstance(entries, dict):
            entries = [entries]

        return entries

    # 4. Multi-page extractor
    def extract_all_entries(self, pdf_path):
        all_entries = []
        texts = self.extract_text_from_pdf(pdf_path)
        for page_num, text in texts:
            print(f"📄 Processing page {page_num}...")
            page_entries = self.extract_journal_entries_from_page(text)
            all_entries.extend(page_entries)
        return all_entries
