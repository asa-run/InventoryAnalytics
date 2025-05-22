
import pandas as pd

def load_invoice_data(csv_path="data/Synthetic_Invoice_Data-ChatGPT.csv"):
    df = pd.read_csv(csv_path)
    # Ensure date column is parsed correctly
    df["PO Order Date"] = pd.to_datetime(df["PO Order Date"])
    # Add derived year column
    df["YEAR"] = df["PO Order Date"].dt.year
    # Add pre-computed unit cost if not already there
    if "UNIT_COST" not in df.columns and "AMOUNT INVOICED" in df.columns and "QUANTITY" in df.columns:
        df["UNIT_COST"] = df["AMOUNT INVOICED"] / df["QUANTITY"]

    return df