from ocr import OCRExtractor
from db_io import insert_entries, fetch_entries
from accounting_analytics import AccountingAnalytics
import os
import openai
from openai import OpenAIError, RateLimitError
from openai import OpenAI

import io
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


api_key = os.getenv("OPENAI_API_KEY")


if __name__ == "__main__":
    pdf_file = "invoice_dummy.pdf"

    # Step 1 + 2: OCR + LLM
    ocr = OCRExtractor(api_key=api_key)
    entries = ocr.extract_all_entries(pdf_file)

    # Step 3: Save to DB
    insert_entries(entries)

    # Step 4: Analytics
    df = fetch_entries()
    analytics = AccountingAnalytics(df)

    print("\nTrial Balance")
    print(analytics.trial_balance())

    print("\nIncome Statement")
    print(analytics.income_statement())

    print("\nBalance Sheet")
    print(analytics.balance_sheet())
