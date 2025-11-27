import pandas as pd

# 1) LOAD DATA
faers = pd.read_csv("../data_processed/faers_drug_stats.csv")
drugs = pd.read_csv("../data_processed/drugs.csv")
kg = pd.read_csv("../data_processed/kg_interactions.csv")  # change name if your file is different

# 2) BUILD INTERACTION DEGREE PER DRUG
degree_counts = {}

for _, row in kg.iterrows():
    d1 = row["drug1_id"]
    d2 = row["drug2_id"]

    degree_counts[d1] = degree_counts.get(d1, 0) + 1
    degree_counts[d2] = degree_counts.get(d2, 0) + 1

degree_df = pd.DataFrame([
    {"drug_id": drug_id, "interaction_degree": deg}
    for drug_id, deg in degree_counts.items()
])

# 3) NORMALIZE NAMES FOR MATCHING
faers["drug_name_upper"] = faers["drug_name"].str.upper().str.strip()
drugs["name_upper"] = drugs["name"].str.upper().str.strip()

# 4) MERGE FAERS ↔ DRUGBANK NAMES
merged = pd.merge(
    faers,
    drugs[["drug_id", "name_upper"]],
    left_on="drug_name_upper",
    right_on="name_upper",
    how="inner"
)

# 5) MERGE INTERACTION DEGREE
merged = pd.merge(
    merged,
    degree_df,
    on="drug_id",
    how="inner"
)

print(f"Matched {len(merged)} drugs between FAERS and DrugBank/graph.")

if merged.empty:
    print("No matches found. Check name formats.")
    exit()

# 6) CREATE LABELS: LOW / MEDIUM / HIGH FOR FAERS & DEGREE

def make_label(value, q1, q2):
    if value <= q1:
        return "low"
    elif value <= q2:
        return "medium"
    else:
        return "high"

# Compute quantiles
fa_q1 = merged["faers_reports"].quantile(0.33)
fa_q2 = merged["faers_reports"].quantile(0.66)

deg_q1 = merged["interaction_degree"].quantile(0.33)
deg_q2 = merged["interaction_degree"].quantile(0.66)

merged["faers_label"] = merged["faers_reports"].apply(lambda v: make_label(v, fa_q1, fa_q2))
merged["graph_label"] = merged["interaction_degree"].apply(lambda v: make_label(v, deg_q1, deg_q2))

# 7) COMPUTE AGREEMENT
total = len(merged)
matches = (merged["faers_label"] == merged["graph_label"]).sum()
agreement = (matches / total) * 100

print("==== FAERS vs Knowledge Graph Validation ====")
print(f"Total matched drugs: {total}")
print(f"Label matches: {matches}")
print(f"External agreement: {agreement:.2f}%")

# 8) SAVE DETAILED RESULTS
merged.to_csv("../data_processed/faers_graph_validation_results.csv", index=False)
print("Saved detailed results to ../data_processed/faers_graph_validation_results.csv")
