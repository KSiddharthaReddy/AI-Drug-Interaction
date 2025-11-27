import pandas as pd
from risk_scoring import predict_pair_severity

# Load training data (contains FDA severity labels)
df = pd.read_csv("../data_processed/training_data.csv")

# Only keep necessary columns and drop missing values
df = df.dropna(subset=["drug1_id", "drug2_id", "severity"])

total = 0
correct = 0
details = []

for _, row in df.iterrows():
    d1 = row["drug1_id"]
    d2 = row["drug2_id"]
    true_label = str(row["severity"]).lower()
    
    predicted_label, _ = predict_pair_severity(d1, d2)
    predicted_label = str(predicted_label).lower()

    # Count as match if predicted severity category matches true label
    match = (predicted_label in true_label) or (true_label in predicted_label)
    
    total += 1
    if match:
        correct += 1
    
    details.append({
        "drug1": d1,
        "drug2": d2,
        "true_severity": true_label,
        "predicted_severity": predicted_label,
        "match": match
    })

accuracy = correct / total * 100

print("=== FDA-Documented Drug Interaction Validation ===")
print(f"Total evaluated pairs: {total}")
print(f"Correct predictions: {correct}")
print(f"Accuracy: {accuracy:.2f}%")

# Save detailed result table
pd.DataFrame(details).to_csv("../data_processed/fda_validation_details.csv", index=False)
print("Saved detailed results to ../data_processed/fda_validation_details.csv")
