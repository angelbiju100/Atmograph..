
import copy
import json
import random
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from pathlib import Path
from torch import nn
from torch_geometric.nn import SAGEConv
from sklearn.metrics import roc_auc_score, average_precision_score

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "ml" / "data" / "processed"
MODEL_DIR = ROOT / "ml" / "models"
REPORT_DIR = ROOT / "ml" / "reports"

SEED = 42
EPOCHS = 100
PATIENCE = 15

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

# ------------------------------------------------------------
# LOAD DATA - EXCLUDE THE TWO DEGREE FEATURES
# ------------------------------------------------------------

features = np.load(DATA_DIR / "node_features.npy")
features = features[:, :-2]

train_edges = np.load(DATA_DIR / "train_edges.npy")
val_edges = np.load(DATA_DIR / "val_edges.npy")
test_edges = np.load(DATA_DIR / "test_edges.npy")

val_negative_edges = np.load(
    DATA_DIR / "val_negative_edges.npy"
)

test_negative_edges = np.load(
    DATA_DIR / "test_negative_edges.npy"
)

num_nodes = features.shape[0]

x = torch.tensor(features, dtype=torch.float32)

edge_index = torch.tensor(
    train_edges.T,
    dtype=torch.long
)

train_pos = torch.tensor(train_edges, dtype=torch.long)
val_pos = torch.tensor(val_edges, dtype=torch.long)
val_neg = torch.tensor(val_negative_edges, dtype=torch.long)
test_pos = torch.tensor(test_edges, dtype=torch.long)
test_neg = torch.tensor(test_negative_edges, dtype=torch.long)

# ------------------------------------------------------------
# GRAPHSAGE ENCODER
# ------------------------------------------------------------

class GraphSAGE(nn.Module):

    def __init__(self, input_channels, hidden_channels, embedding_channels):
        super().__init__()

        self.conv1 = SAGEConv(
            input_channels, hidden_channels, aggr="mean"
        )

        self.conv2 = SAGEConv(
            hidden_channels, embedding_channels, aggr="mean"
        )

    def forward(self, x, edge_index):

        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.3, training=self.training)

        return self.conv2(x, edge_index)


# ------------------------------------------------------------
# DIRECTED LINK DECODER
# ------------------------------------------------------------

class DirectedLinkDecoder(nn.Module):

    def __init__(self, embedding_channels):
        super().__init__()

        self.source_projection = nn.Linear(
            embedding_channels, embedding_channels, bias=False
        )

        self.target_projection = nn.Linear(
            embedding_channels, embedding_channels, bias=False
        )

    def forward(self, embeddings, edges):

        source = self.source_projection(
            embeddings[edges[:, 0]]
        )

        target = self.target_projection(
            embeddings[edges[:, 1]]
        )

        return (source * target).sum(dim=1)


encoder = GraphSAGE(
    x.shape[1], 128, 64
)

decoder = DirectedLinkDecoder(64)

optimizer = torch.optim.Adam(
    list(encoder.parameters()) + list(decoder.parameters()),
    lr=0.001,
    weight_decay=0.0001
)

# ------------------------------------------------------------
# GENERATE TRAINING NEGATIVE EDGES
# ------------------------------------------------------------

all_positive_edges = set(
    map(tuple, np.vstack([
        train_edges, val_edges, test_edges
    ]).tolist())
)

rng = np.random.default_rng(SEED)

def generate_negative_edges(count):

    negatives = set()
    attempts = 0
    max_attempts = count * 100

    while len(negatives) < count and attempts < max_attempts:

        remaining = count - len(negatives)
        batch_size = min(remaining * 2, 100000)

        sources = rng.integers(0, num_nodes, size=batch_size)
        targets = rng.integers(0, num_nodes, size=batch_size)

        for u, v in zip(sources, targets):

            attempts += 1

            if u == v:
                continue

            edge = (int(u), int(v))

            if edge in all_positive_edges:
                continue

            negatives.add(edge)

            if len(negatives) == count:
                break

    if len(negatives) != count:
        raise RuntimeError("Could not generate negative edges.")

    return torch.tensor(sorted(negatives), dtype=torch.long)


train_neg = generate_negative_edges(len(train_pos))


# ------------------------------------------------------------
# EVALUATION
# ------------------------------------------------------------

def evaluate(pos_edges, neg_edges):

    encoder.eval()
    decoder.eval()

    with torch.no_grad():

        embeddings = encoder(x, edge_index)

        pos_scores = decoder(embeddings, pos_edges)
        neg_scores = decoder(embeddings, neg_edges)

        scores = torch.cat([
            pos_scores, neg_scores
        ]).numpy()

        labels = np.concatenate([
            np.ones(len(pos_scores)),
            np.zeros(len(neg_scores))
        ])

        probabilities = 1 / (
            1 + np.exp(-np.clip(scores, -50, 50))
        )

        return (
            roc_auc_score(labels, probabilities),
            average_precision_score(labels, probabilities)
        )


# ------------------------------------------------------------
# TRAINING
# ------------------------------------------------------------

best_val_auc = -1
best_epoch = 0
best_state = None
patience_counter = 0

history = []

print("=" * 70)
print("ATMOGRAPH - GRAPHSAGE WITHOUT DEGREE FEATURES")
print("=" * 70)

print("Nodes:", num_nodes)
print("Input features:", x.shape[1])
print("Training edges:", len(train_pos))
print("Training negative edges:", len(train_neg))

for epoch in range(1, EPOCHS + 1):

    encoder.train()
    decoder.train()

    optimizer.zero_grad()

    embeddings = encoder(x, edge_index)

    positive_scores = decoder(embeddings, train_pos)
    negative_scores = decoder(embeddings, train_neg)

    scores = torch.cat([
        positive_scores, negative_scores
    ])

    labels = torch.cat([
        torch.ones(len(positive_scores)),
        torch.zeros(len(negative_scores))
    ])

    loss = F.binary_cross_entropy_with_logits(scores, labels)

    loss.backward()
    optimizer.step()

    val_auc, val_ap = evaluate(val_pos, val_neg)

    history.append({
        "epoch": epoch,
        "training_loss": loss.item(),
        "validation_roc_auc": val_auc,
        "validation_average_precision": val_ap
    })

    if val_auc > best_val_auc:

        best_val_auc = val_auc
        best_epoch = epoch

        best_state = {
            "encoder": copy.deepcopy(encoder.state_dict()),
            "decoder": copy.deepcopy(decoder.state_dict())
        }

        patience_counter = 0

    else:
        patience_counter += 1

    if epoch == 1 or epoch % 10 == 0:

        print(
            f"Epoch {epoch:03d} | "
            f"Loss: {loss.item():.4f} | "
            f"Val ROC-AUC: {val_auc:.4f} | "
            f"Val AP: {val_ap:.4f}"
        )

    if patience_counter >= PATIENCE:

        print(f"\nEarly stopping at epoch {epoch}.")
        break


# ------------------------------------------------------------
# RESTORE BEST MODEL AND TEST
# ------------------------------------------------------------

encoder.load_state_dict(best_state["encoder"])
decoder.load_state_dict(best_state["decoder"])

test_auc, test_ap = evaluate(test_pos, test_neg)

print("\n" + "=" * 70)
print("GRAPHSAGE WITHOUT DEGREE - FINAL RESULTS")
print("=" * 70)

print("Best epoch:", best_epoch)
print("Validation ROC-AUC:", round(best_val_auc, 4))
print("Test ROC-AUC:", round(test_auc, 4))
print("Test Average Precision:", round(test_ap, 4))

# ------------------------------------------------------------
# SAVE SEPARATELY
# ------------------------------------------------------------

torch.save({
    "encoder_state_dict": encoder.state_dict(),
    "decoder_state_dict": decoder.state_dict(),
    "input_channels": x.shape[1],
    "hidden_channels": 128,
    "embedding_channels": 64,
    "best_epoch": best_epoch
}, MODEL_DIR / "graphsage_without_degree.pt")

results = {
    "experiment": "GraphSAGE without degree features",
    "input_features": int(x.shape[1]),
    "best_epoch": int(best_epoch),
    "validation_roc_auc": float(best_val_auc),
    "test_roc_auc": float(test_auc),
    "test_average_precision": float(test_ap),
    "seed": SEED
}

with open(
    REPORT_DIR / "graphsage_without_degree_results.json", "w"
) as file:
    json.dump(results, file, indent=4)

pd.DataFrame(history).to_csv(
    REPORT_DIR / "graphsage_without_degree_history.csv",
    index=False
)

print("\nModel and reports saved successfully.")
print("GraphSAGE ablation experiment completed.")
