import itertools
import joblib
import pandas as pd

# LOAD MODEL & ENCODERS (you already have this above)
model = joblib.load("../data_processed/rf_interaction_model.joblib")
class_encoder = joblib.load("../data_processed/class_encoder.joblib")
severity_encoder = joblib.load("../data_processed/severity_encoder.joblib")

drugs_df = pd.read_csv("../data_processed/drugs.csv")

def get_drug_class(drug_id: str) -> str:
    row = drugs_df[drugs_df["drug_id"] == drug_id]
    if row.empty:
        return "UNKNOWN"
    return str(row.iloc[0]["drug_class"])

def encode_classes(class1: str, class2: str):
    if class1 not in class_encoder.classes_:
        class1 = class_encoder.classes_[0]
    if class2 not in class_encoder.classes_:
        class2 = class_encoder.classes_[0]
    c1_enc = class_encoder.transform([class1])[0]
    c2_enc = class_encoder.transform([class2])[0]
    return c1_enc, c2_enc

def predict_pair_severity(drug1_id: str, drug2_id: str):
    class1 = get_drug_class(drug1_id)
    class2 = get_drug_class(drug2_id)

    c1_enc, c2_enc = encode_classes(class1, class2)

    X = pd.DataFrame([[c1_enc, c2_enc]], columns=["class1_enc", "class2_enc"])
    y_pred = model.predict(X)[0]
    y_prob = model.predict_proba(X)[0]

    severity_label = severity_encoder.inverse_transform([y_pred])[0]
    return severity_label, y_prob

def compute_regimen_risk(drug_ids, age: int | None = None, sex: str | None = None):
    """
    Compute a simple risk score (0-100) for a list of drug_ids.
    Optionally personalize score based on age and sex.
    """
    pairs = list(itertools.combinations(drug_ids, 2))
    if not pairs:
        return {
            "risk_score": 0,
            "total_pairs": 0,
            "severe_pairs": 0,
            "moderate_pairs": 0,
            "unknown_pairs": 0,
            "details": []
        }

    severe_count = 0
    moderate_count = 0
    unknown_count = 0
    details = []

    for d1, d2 in pairs:
        severity_label, _ = predict_pair_severity(d1, d2)
        sev_lower = str(severity_label).lower()
        details.append({
            "drug1_id": d1,
            "drug2_id": d2,
            "severity": str(severity_label)
        })

        if "severe" in sev_lower:
            severe_count += 1
        elif "moderate" in sev_lower:
            moderate_count += 1
        else:
            unknown_count += 1

    total_pairs = len(pairs)

    # Base risk score from interactions
    max_points = total_pairs * 3.0
    actual_points = severe_count * 3 + moderate_count * 2 + unknown_count * 1
    risk_score = (actual_points / max_points) * 100 if max_points > 0 else 0

    # Simple personalization tuning
    if age is not None:
        try:
            age_int = int(age)
            if age_int >= 65:
                risk_score *= 1.2  # elderly: +20%
            elif age_int <= 18:
                risk_score *= 1.1  # child/teen: +10%
        except ValueError:
            pass

    if sex is not None:
        sex_str = str(sex).upper()
        if sex_str == "F":
            risk_score *= 1.05  # slightly higher risk for some drug classes

    # Cap at 100
    risk_score = min(risk_score, 100.0)

    return {
        "risk_score": round(risk_score, 2),
        "total_pairs": total_pairs,
        "severe_pairs": severe_count,
        "moderate_pairs": moderate_count,
        "unknown_pairs": unknown_count,
        "details": details
    }

if __name__ == "__main__":
    # quick test if you want
    example_drugs = []  # fill with some IDs to test
    if example_drugs:
        print(compute_regimen_risk(example_drugs, age=70, sex="F"))
