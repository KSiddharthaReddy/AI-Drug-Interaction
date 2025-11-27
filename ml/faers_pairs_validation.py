import pandas as pd
from risk_scoring import predict_pair_severity

# Load FAERS pair data + DrugBank metadata
faers_pairs = pd.read_csv("../data_processed/faers_pairs.csv")
drugs = pd.read_csv("../data_processed/drugs.csv")

# Normalize names for matching
drugs["name_upper"] = drugs["name"].str.upper().str.strip()

name_to_id = dict(zip(drugs["name_upper"], drugs["drug_id"]))

def map_name_to_id(name):
    return name_to_id.get(str(name).upper().strip())

def is_high_risk(severity_label: str) -> bool:
    s = str(severity_label).lower()
    return ("severe" in s) or ("major" in s) or ("contraindicat" in s) or ("moderate" in s)

def main():
    # Restrict to strong FAERS pairs (you can adjust this min_reports upwards)
    MIN_REPORTS = 20  # try 20, 50, 100 etc. Higher = stronger signal

    strong_pairs = faers_pairs[faers_pairs["pair_reports"] >= MIN_REPORTS].copy()
    print(f"Total FAERS pairs with >= {MIN_REPORTS} reports: {len(strong_pairs)}")

    total_evaluated = 0
    correctly_flagged = 0

    details = []

    for _, row in strong_pairs.iterrows():
        n1 = row["drug_name_1"]
        n2 = row["drug_name_2"]
        count = row["pair_reports"]

        id1 = map_name_to_id(n1)
        id2 = map_name_to_id(n2)

        if not id1 or not id2:
            continue  # skip if we can't map to DrugBank

        severity_label, _ = predict_pair_severity(id1, id2)
        high_risk = is_high_risk(severity_label)

        total_evaluated += 1
        if high_risk:
            correctly_flagged += 1

        details.append({
            "drug_name_1": n1,
            "drug_name_2": n2,
            "pair_reports": count,
            "severity_pred": severity_label,
            "model_flags_high": high_risk
        })

    if total_evaluated == 0:
        print("No pairs evaluated. Check name matching or MIN_REPORTS.")
        return

    precision = correctly_flagged / total_evaluated * 100

    print("==== FAERS Pair-Level Validation ====")
    print(f"MIN_REPORTS threshold: {MIN_REPORTS}")
    print(f"Total evaluated FAERS pairs: {total_evaluated}")
    print(f"Pairs flagged high-risk by model: {correctly_flagged}")
    print(f"Agreement (precision on high-FAERS pairs): {precision:.2f}%")

    pd.DataFrame(details).to_csv("../data_processed/faers_pairs_validation_results.csv", index=False)
    print("Saved detailed results to ../data_processed/faers_pairs_validation_results.csv")

if __name__ == "__main__":
    main()
