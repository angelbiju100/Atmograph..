
import numpy as np
import pandas as pd
import torch

from pathlib import Path
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score
)

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "ml" / "data" / "processed"
MODEL_DIR = ROOT / "ml" / "models"
REPORT_DIR = ROOT / "ml" / "reports"

DEVICE = torch.device("cpu")

# ============================================================
# LOAD TEST DATA
# ============================================================

train_edges = np.load(DATA_DIR / "train_edges.npy")
test_edges = np.load(DATA_DIR / "test_edges.npy")

test_negative_edges = np.load(
    DATA_DIR / "test_negative_edges.npy"
)

num_nodes = len(
    pd.read_csv(DATA_DIR / "node_feature_ids.csv")
)

positive_edges = test_edges
negative_edges = test_negative_edges

all_test_edges = np.vstack([
    positive_edges,
    negative_edges
])

labels = np.concatenate([
    np.ones(len(positive_edges)),
    np.zeros(len(negative_edges))
])

# ============================================================
# TRAINING GRAPH DEGREE STATISTICS
# ============================================================

in_degree = np.zeros(num_nodes)
out_degree = np.zeros(num_nodes)

np.add.at(in_degree, train_edges[:, 1], 1)
np.add.at(out_degree, train_edges[:, 0], 1)

# ============================================================
# BASELINE 1: RANDOM PREDICTION
# ============================================================

rng = np.random.default_rng(42)

random_scores = rng.random(len(all_test_edges))

# ============================================================
# BASELINE 2: DEGREE-BASED PREDICTION
# ============================================================

degree_scores = []

for source, target in all_test_edges:

    score = np.log1p(
        out_degree[source]
    ) + np.log1p(
        in_degree[target]
    )

    degree_scores.append(score)

degree_scores = np.array(degree_scores)

# ============================================================
# BASELINE 3: DIRECTED COMMON NEIGHBOURS
# ============================================================

out_neighbors = [
    set() for _ in range(num_nodes)
]

in_neighbors = [
    set() for _ in range(num_nodes)
]

for source, target in train_edges:

    out_neighbors[source].add(target)
    in_neighbors[target].add(source)

common_neighbor_scores = []

for source, target in all_test_edges:

    common = (
        out_neighbors[source]
        & in_neighbors[target]
    )

    common_neighbor_scores.append(
        len(common)
    )

common_neighbor_scores = np.array(
    common_neighbor_scores
)

# ============================================================
# GRAPH SAGE MODEL
# ============================================================

from torch import nn
import torch.nn.functional as F
from torch_geometric.nn import SAGEConv


class GraphSAGE(nn.Module):

    def __init__(
        self,
        input_channels,
        hidden_channels,
        embedding_channels
    ):
        super().__init__()

        self.conv1 = SAGEConv(
            input_channels,
            hidden_channels,
            aggr="mean"
        )

        self.conv2 = SAGEConv(
            hidden_channels,
            embedding_channels,
            aggr="mean"
        )

    def forward(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.3, training=self.training)

        return self.conv2(x, edge_index)


class DirectedLinkDecoder(nn.Module):

    def __init__(self, embedding_channels):
        super().__init__()

        self.source_projection = nn.Linear(
            embedding_channels,
            embedding_channels,
            bias=False
        )

        self.target_projection = nn.Linear(
            embedding_channels,
            embedding_channels,
            bias=False
        )

    def forward(self, embeddings, edges):

        source_embeddings = self.source_projection(
            embeddings[edges[:, 0]]
        )

        target_embeddings = self.target_projection(
            embeddings[edges[:, 1]]
        )

        return (
            source_embeddings * target_embeddings
        ).sum(dim=1)


# ============================================================
# LOAD GRAPH SAGE INPUTS
# ============================================================

features = np.load(DATA_DIR / "node_features.npy")

# Recompute degree features from training edges
features[:, -2] = np.log1p(in_degree)
features[:, -1] = np.log1p(out_degree)

x = torch.tensor(
    features,
    dtype=torch.float32
)

edge_index = torch.tensor(
    train_edges.T,
    dtype=torch.long
)

edges_tensor = torch.tensor(
    all_test_edges,
    dtype=torch.long
)

checkpoint = torch.load(
    MODEL_DIR / "graphsage_link_prediction.pt",
    map_location=DEVICE,
    weights_only=True
)

encoder = GraphSAGE(
    checkpoint["input_channels"],
    checkpoint["hidden_channels"],
    checkpoint["embedding_channels"]
)

decoder = DirectedLinkDecoder(
    checkpoint["embedding_channels"]
)

encoder.load_state_dict(
    checkpoint["encoder_state_dict"]
)

decoder.load_state_dict(
    checkpoint["decoder_state_dict"]
)

encoder.eval()
decoder.eval()

with torch.no_grad():

    embeddings = encoder(x, edge_index)

    graphsage_scores = decoder(
        embeddings,
        edges_tensor
    ).numpy()

# ============================================================
# EVALUATE ALL METHODS
# ============================================================

methods = {
    "Random": random_scores,
    "Degree-based": degree_scores,
    "Directed common neighbours": common_neighbor_scores,
    "GraphSAGE": graphsage_scores
}

results = []

for method, scores in methods.items():

    roc_auc = roc_auc_score(
        labels,
        scores
    )

    average_precision = average_precision_score(
        labels,
        scores
    )

    results.append({
        "model": method,
        "roc_auc": roc_auc,
        "average_precision": average_precision
    })

comparison = pd.DataFrame(results)

comparison = comparison.sort_values(
    "roc_auc",
    ascending=False
).reset_index(drop=True)

# ============================================================
# SAVE AND DISPLAY
# ============================================================

OUTPUT_FILE = (
    REPORT_DIR / "link_prediction_baseline_comparison.csv"
)

comparison.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 75)
print("ATMOGRAPH - LINK PREDICTION BASELINE COMPARISON")
print("=" * 75)

print("\nTest samples:")
print("Positive edges:", len(positive_edges))
print("Negative edges:", len(negative_edges))

print("\nModel comparison:")
print(
    comparison.to_string(
        index=False,
        float_format=lambda value: f"{value:.4f}"
    )
)

print("\nSaved report:", OUTPUT_FILE)

print("\nBaseline comparison completed.")
