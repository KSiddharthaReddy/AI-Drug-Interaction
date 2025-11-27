import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.utils import train_test_split_edges
from sklearn.metrics import classification_report
import time

# Load data
saved = torch.load("../data_processed/gnn_data.pt", weights_only=False)
data = saved["data"]
edge_index_all = saved["edge_index_all"]  # [2, 2M]
y_all = saved["y_all"]                    # [2M]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
data = data.to(device)
edge_index_all = edge_index_all.to(device)
y_all = y_all.to(device)

num_nodes = data.num_nodes

# Simple GCN model
class GCNLinkPredictor(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.lin = nn.Linear(hidden_channels * 2, 2)  # binary classification

    def encode(self, x, edge_index):
        h = self.conv1(x.float(), edge_index)
        h = F.relu(h)
        h = self.conv2(h, edge_index)
        return h

    def decode(self, z, edge_index_pairs):
        # z: [N, hidden], edge_index_pairs: [2, E]
        z_i = z[edge_index_pairs[0]]  # [E, hidden]
        z_j = z[edge_index_pairs[1]]  # [E, hidden]
        z_cat = torch.cat([z_i, z_j], dim=-1)  # [E, 2*hidden]
        return self.lin(z_cat)  # logits [E, 2]

model = GCNLinkPredictor(in_channels=data.x.size(1), hidden_channels=32).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)
# Class weights: penalize mistakes on positive class more
class_weights = torch.tensor([1.0, 3.0], device=device)  # [w0, w1]


# Split positive+negative edges into train/test
num_edges = edge_index_all.size(1)
perm = torch.randperm(num_edges)
split = int(0.8 * num_edges)
train_idx = perm[:split]
test_idx = perm[split:]

edge_index_train = edge_index_all[:, train_idx]
y_train = y_all[train_idx]

edge_index_test = edge_index_all[:, test_idx]
y_test = y_all[test_idx]

print("Train edges:", edge_index_train.size(1), "Test edges:", edge_index_test.size(1))

def train():
    model.train()
    optimizer.zero_grad()
    z = model.encode(data.x, data.edge_index)  # positive edges define graph structure
    out = model.decode(z, edge_index_train)
    loss = F.cross_entropy(out, y_train, weight=class_weights)
    loss.backward()
    optimizer.step()
    return loss.item()

@torch.no_grad()
def test():
    model.eval()
    z = model.encode(data.x, data.edge_index)
    out = model.decode(z, edge_index_test)
    preds = out.argmax(dim=-1)
    report = classification_report(y_test.cpu(), preds.cpu(), output_dict=False)
    return report

# Training loop
for epoch in range(1, 61):
    loss = train()
    if epoch % 5 == 0 or epoch == 1:
        print(f"Epoch {epoch}, Loss {loss:.4f}")


print("\n=== GNN Evaluation on Test Set ===")
report = test()
print(report)

# Measure inference time for, say, 1000 edges
@torch.no_grad()
def measure_inference_time(num_samples=1000):
    model.eval()
    z = model.encode(data.x, data.edge_index)
    # Sample subset of test edges (or reuse full)
    e = min(num_samples, edge_index_test.size(1))
    subset = edge_index_test[:, :e]
    start = time.time()
    out = model.decode(z, subset)
    end = time.time()
    avg_time_per_edge = (end - start) / e
    print(f"Inference time per edge: {avg_time_per_edge*1000:.4f} ms")

measure_inference_time()

# Save model
torch.save(model.state_dict(), "../data_processed/gnn_ddi_model.pt")
print("Saved GNN model to ../data_processed/gnn_ddi_model.pt")
