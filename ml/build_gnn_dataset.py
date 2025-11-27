import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import torch
from torch_geometric.data import Data
import joblib

# Load nodes and edges
drugs = pd.read_csv("../data_processed/kg_drugs.csv")
interactions = pd.read_csv("../data_processed/kg_interactions.csv")

# Map each drug_id to a numeric index
drug_ids = drugs["drug_id"].unique()
drug_id_to_idx = {d: i for i, d in enumerate(drug_ids)}
num_nodes = len(drug_ids)

print("Number of nodes:", num_nodes)

# ====== NODE FEATURES ======
# drug_class -> categorical feature
class_encoder = LabelEncoder()
classes = drugs["drug_class"].fillna("UNKNOWN").astype(str)
class_enc = class_encoder.fit_transform(classes)  # [num_nodes]

# type -> categorical feature
type_encoder = LabelEncoder()
types = drugs["type"].fillna("UNKNOWN").astype(str)
type_enc = type_encoder.fit_transform(types)      # [num_nodes]

# Build positive edges (interactions)
pos_edges = []
for _, row in interactions.iterrows():
    d1 = row["drug1_id"]
    d2 = row["drug2_id"]
    if d1 in drug_id_to_idx and d2 in drug_id_to_idx:
        i = drug_id_to_idx[d1]
        j = drug_id_to_idx[d2]
        pos_edges.append((i, j))

pos_edges = list(set(pos_edges))  # unique
print("Positive edges:", len(pos_edges))

# Degree feature (how connected each drug is)
degrees = np.zeros(num_nodes, dtype=np.float32)
for i, j in pos_edges:
    degrees[i] += 1
    degrees[j] += 1

# Normalize degree (0–1)
if degrees.max() > 0:
    degrees = degrees / degrees.max()

# Stack features: [drug_class_enc, type_enc, degree]
# We convert categorical encodings to float so GCN can process
features = np.stack([class_enc, type_enc, degrees], axis=1).astype(np.float32)
x = torch.tensor(features, dtype=torch.float)  # shape [num_nodes, 3]

# Convert pos_edges to tensor
edge_index_pos = torch.tensor(pos_edges, dtype=torch.long).t().contiguous()

# ====== NEGATIVE EDGES ======
pos_set = set(pos_edges)
num_neg = len(pos_edges)
neg_edges = set()

rng = np.random.default_rng(seed=42)
while len(neg_edges) < num_neg:
    i = int(rng.integers(0, num_nodes))
    j = int(rng.integers(0, num_nodes))
    if i == j:
        continue
    e = (i, j)
    if e in pos_set or e in neg_edges:
        continue
    neg_edges.add(e)

neg_edges = list(neg_edges)
print("Negative edges:", len(neg_edges))

edge_index_neg = torch.tensor(neg_edges, dtype=torch.long).t().contiguous()

# Labels: 1 for positive, 0 for negative
y_pos = torch.ones(edge_index_pos.size(1), dtype=torch.long)
y_neg = torch.zeros(edge_index_neg.size(1), dtype=torch.long)

# Combine for training
edge_index_all = torch.cat([edge_index_pos, edge_index_neg], dim=1)  # [2, 2M]
y_all = torch.cat([y_pos, y_neg], dim=0)                             # [2M]

# Graph Data object (structure uses ONLY positive edges)
data = Data(x=x, edge_index=edge_index_pos)

# Save tensors & mapping
torch.save({
    "data": data,
    "edge_index_all": edge_index_all,
    "y_all": y_all,
}, "../data_processed/gnn_data.pt")

joblib.dump(drug_id_to_idx, "../data_processed/drug_id_to_idx.joblib")
joblib.dump(class_encoder, "../data_processed/gnn_class_encoder.joblib")
joblib.dump(type_encoder, "../data_processed/gnn_type_encoder.joblib")

print("Saved improved GNN dataset to ../data_processed/gnn_data.pt")
