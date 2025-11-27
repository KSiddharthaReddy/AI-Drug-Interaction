import os
import pandas as pd
from collections import Counter

BASE_PATH = "../data_faers"
QUARTERS = ["Q2", "Q3"]

def load_faers_drug(q):
    return pd.read_csv(os.path.join(BASE_PATH, q, "DRUG.txt"), sep="$", low_memory=False)

def load_faers_reac(q):
    return pd.read_csv(os.path.join(BASE_PATH, q, "REAC.txt"), sep="$", low_memory=False)

def get_drug_name_column(df):
    """
    Try to find the drug name column in a case-insensitive way.
    Works for 'drugname', 'DRUGNAME', 'MEDICINALPRODUCT', etc.
    """
    # Map lowercase column names to original
    cols_lower = {c.lower(): c for c in df.columns}

    possible_keys = ["drugname", "medicinalproduct", "drugname_generic", "prod_ai"]
    for key in possible_keys:
        if key in cols_lower:
            return cols_lower[key]

    # If nothing matched, raise an error showing available columns
    raise Exception(f"No known drug name column found. Available columns: {df.columns}")


def main():
    report_counter = Counter()

    for q in QUARTERS:
        print(f"Processing FAERS {q}...")

        df_drug = load_faers_drug(q)
        drug_col = get_drug_name_column(df_drug)

        for _, row in df_drug.iterrows():
            drug = str(row[drug_col]).strip().upper()
            if not drug:
                continue
            report_counter[drug] += 1

    df_final = pd.DataFrame([
        {"drug_name": drug, "faers_reports": count}
        for drug, count in report_counter.items()
    ])

    df_final.sort_values("faers_reports", ascending=False, inplace=True)
    df_final.to_csv("../data_processed/faers_drug_stats.csv", index=False)

    print("Created: ../data_processed/faers_drug_stats.csv")
    print("Top 10 drugs in FAERS by report count:")
    print(df_final.head(10))

if __name__ == "__main__":
    main()
