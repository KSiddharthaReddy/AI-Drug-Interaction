import pandas as pd
from risk_scoring import compute_regimen_risk, get_drug_class

# Load drugs metadata
drugs_df = pd.read_csv("../data_processed/drugs.csv")


def get_candidate_alternatives(target_drug_id: str, max_candidates: int = 20):
    """
    Return up to max_candidates drugs with the same class as target.
    If none are found, fall back to any other drugs (so that the
    recommendation engine always returns something for demo purposes).
    """
    target_class = get_drug_class(target_drug_id)
    print("Target drug:", target_drug_id, "| class:", target_class)

    same_class = []
    if target_class != "UNKNOWN":
        same_class = drugs_df[
            (drugs_df["drug_class"] == target_class) &
            (drugs_df["drug_id"] != target_drug_id)
        ]["drug_id"].dropna().unique().tolist()

    if same_class:
        print("Found", len(same_class), "same-class candidates.")
        return same_class[:max_candidates]

    # Fallback: pick any other drugs so we can still show recommendations
    print("No same-class candidates found; using fallback candidates.")
    fallback = drugs_df[drugs_df["drug_id"] != target_drug_id]["drug_id"].dropna().unique().tolist()
    return fallback[:max_candidates]


def recommend_alternatives(current_regimen, target_drug_id, top_k=3):
    """
    current_regimen: list of current drug_ids.
    target_drug_id: the drug we want to replace.
    """
    if target_drug_id not in current_regimen:
        print("Target drug not in regimen.")
        return []

    base_regimen = [d for d in current_regimen if d != target_drug_id]
    candidates = get_candidate_alternatives(target_drug_id)

    print("Number of candidate alternatives found:", len(candidates))

    results = []
    for alt in candidates:
        new_regimen = base_regimen + [alt]
        risk_info = compute_regimen_risk(new_regimen)
        results.append({
            "alternative_drug_id": alt,
            "risk_score": risk_info["risk_score"],
            "severe_pairs": risk_info["severe_pairs"],
            "moderate_pairs": risk_info["moderate_pairs"],
            "unknown_pairs": risk_info["unknown_pairs"]
        })

    # Sort alternatives by lowest risk score
    results_sorted = sorted(results, key=lambda x: x["risk_score"])
    return results_sorted[:top_k]


if __name__ == "__main__":
    # Example usage - replace with real ids from drugs.csv
    current_regimen = ['DB00301', 'DB00316', 'DB00313']
    target_drug = 'DB00313'  # one of the above ids

    if not current_regimen or not target_drug:
        print("Edit recommendation_engine.py and add real drug_ids for testing.")
    else:
        recs = recommend_alternatives(current_regimen, target_drug)
        print("\nRecommendations:")
        if not recs:
            print("No recommendations found.")
        else:
            for r in recs:
                print(r)
