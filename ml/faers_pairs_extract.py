import os
import pandas as pd
import itertools
from collections import Counter

BASE_PATH = "../data_faers"
QUARTERS = ["Q2", "Q3"]  # folders you created

def load_faers_drug(q):
    path = os.path.join(BASE_PATH, q, "DRUG.txt")
    return pd.read_csv(path, sep="$", low_memory=False)

def main():
    pair_counter = Counter()

    for q in QUARTERS:
        print(f"Processing pairs from FAERS {q}...")
        df = load_faers_drug(q)

        # Normalize column names
        cols_lower = {c.lower(): c for c in df.columns}
        primary_col = cols_lower.get("primaryid")
        drug_col = cols_lower.get("drugname")

        if primary_col is None or drug_col is None:
            raise Exception(f"PRIMARYID or DRUGNAME column not found. Columns: {df.columns}")

        # Group by PRIMARYID (one adverse event report)
        grouped = df.groupby(primary_col)

        for _, group in grouped:
            # Get unique drug names in this report
            drugs = (
                group[drug_col]
                .dropna()
                .astype(str)
                .str.strip()
                .str.upper()
                .unique()
            )

            # Generate all unordered pairs
            if len(drugs) < 2:
                continue

            for d1, d2 in itertools.combinations(sorted(drugs), 2):
                pair_counter[(d1, d2)] += 1

    # Convert to DataFrame
    rows = []
    for (d1, d2), count in pair_counter.items():
        rows.append({"drug_name_1": d1, "drug_name_2": d2, "pair_reports": count})

    df_pairs = pd.DataFrame(rows)
    df_pairs.sort_values("pair_reports", ascending=False, inplace=True)
    df_pairs.to_csv("../data_processed/faers_pairs.csv", index=False)

    print("Saved FAERS pairs to ../data_processed/faers_pairs.csv")
    print(df_pairs.head(10))

if __name__ == "__main__":
    main()
