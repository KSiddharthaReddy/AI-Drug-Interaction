import pandas as pd

def prepare_drug_nodes():
    df = pd.read_csv("../data_processed/drugs.csv")
    # Keep only columns that exist
    wanted_cols = ["drug_id", "name", "type", "drug_class", "indication"]
    cols = [c for c in wanted_cols if c in df.columns]
    df_nodes = df[cols].copy()
    print("Drug nodes:", len(df_nodes))
    df_nodes.to_csv("../data_processed/kg_drugs.csv", index=False)
    print("Saved ../data_processed/kg_drugs.csv")

def prepare_interaction_edges():
    df = pd.read_csv("../data_processed/known_interactions.csv")
    wanted_cols = ["drug1_id", "drug2_id", "severity", "description", "source"]
    cols = [c for c in wanted_cols if c in df.columns]
    df_edges = df[cols].copy()
    print("Interaction edges:", len(df_edges))
    df_edges.to_csv("../data_processed/kg_interactions.csv", index=False)
    print("Saved ../data_processed/kg_interactions.csv")

def main():
    prepare_drug_nodes()
    prepare_interaction_edges()

if __name__ == "__main__":
    main()
