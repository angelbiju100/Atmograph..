
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
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
)

# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT / "ml" / "data" / "processed"
MODEL_DIR = ROOT / "ml" / "models"
REPORT_DIR = ROOT / "ml" / "reports"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
HIDDEN_CHANNELS = 128
EMBEDDING_CHANNELS = 64
LEARNING_RATE = 0.001
WEIGHT_DECAY = 0.0001
EPOCHS = 100
PATIENCE = 15

# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

DEVICE = torch.device("cpu")

# ============================================================
# LOAD DATA
# ============================================================

features = np.load(DATA_DIR / "node_features.npy")

train_edges = np.load(DATA_DIR / "train_edges.npy")
val_edges = np.load(DATA_DIR / "val_edges.npy")
test_edges = np.load(DATA_DIR / "test_edges.npy")

val_negative_edges = np.load(
    DATA_DIR / "val_negative_edges.npy"
)

test_negative_edges = np.load(
    DATA_DIR / "test_negative_edges.npy"
)

node_ids = pd.read_csv(
    DATA_DIR / "node_feature_ids.csv"
)["id"].tolist()

# ============================================================
# RECOMPUTE DEGREE FEATURES FROM TRAINING GRAPH ONLY
# ============================================================

num_nodes = features.shape[0]

train_in_degree = np.zeros(num_nodes, dtype=np.float32)
train_out_degree = np.zeros(num_nodes, dtype=np.float32)

np.add.at(train_out_degree, train_edges[:, 0], 1)
np.add.at(train_in_degree, train_edges[:, 1], 1)

# Degree features are the final two columns
features[:, -2] = np.log1p(train_in_degree)
features[:, -1] = np.log1p(train_out_degree)

x = torch.tensor(features, dtype=torch.float32)

# PyG message passing uses source -> target edge indices
edge_index = torch.tensor(
    train_edges.T,
    dtype=torch.long
)

train_pos = torch.tensor(
    train_edges,
    dtype=torch.long
)

val_pos = torch.tensor(val_edges, dtype=torch.long)
val_neg = torch.tensor(val_negative_edges, dtype=torch.long)

test_pos = torch.tensor(test_edges, dtype=torch.long)
test_neg = torch.tensor(test_negative_edges, dtype=torch.long)

# ============================================================
# GRAPHSAGE ENCODER
# ============================================================

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

        x = self.conv2(x, edge_index)

        return x


# ============================================================
# DIRECTED LINK DECODER
# ============================================================

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

        scores = (
            source_embeddings * target_embeddings
        ).sum(dim=1)

        return scores


# ============================================================
# INITIALIZE MODEL
# ============================================================

encoder = GraphSAGE(
    input_channels=x.shape[1],
    hidden_channels=HIDDEN_CHANNELS,
    embedding_channels=EMBEDDING_CHANNELS
).to(DEVICE)

decoder = DirectedLinkDecoder(
    EMBEDDING_CHANNELS
).to(DEVICE)

optimizer = torch.optim.Adam(
    list(encoder.parameters()) +
    list(decoder.parameters()),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY
)

# ============================================================
# TRAINING DATA
# ============================================================

# Sample training negatives from pairs that are not
# present in the original observed graph.

all_positive_edges = set(
    map(tuple, np.vstack([
        train_edges,
        val_edges,
        test_edges
    ]).tolist())
)

rng = np.random.default_rng(SEED)

def generate_training_negatives(count):

    negatives = set()
    attempts = 0
    max_attempts = count * 100

    while len(negatives) < count and attempts < max_attempts:

        remaining = count - len(negatives)
        batch_size = min(remaining * 2, 100000)

        sources = rng.integers(
            0, num_nodes, size=batch_size
        )

        targets = rng.integers(
            0, num_nodes, size=batch_size
        )

        for source, target in zip(sources, targets):

            attempts += 1

            if source == target:
                continue

            edge = (int(source), int(target))

            if edge in all_positive_edges:
                continue

            negatives.add(edge)

            if len(negatives) == count:
                break

    if len(negatives) != count:
        raise RuntimeError(
            "Unable to generate training negatives."
        )

    return torch.tensor(
        sorted(negatives),
        dtype=torch.long
    )


train_neg = generate_training_negatives(
    len(train_pos)
)

# ============================================================
# EVALUATION
# ============================================================

def evaluate(pos_edges, neg_edges):

    encoder.eval()
    decoder.eval()

    with torch.no_grad():

        embeddings = encoder(x, edge_index)

        pos_scores = decoder(
            embeddings, pos_edges
        )

        neg_scores = decoder(
            embeddings, neg_edges
        )

        scores = torch.cat([
            pos_scores,
            neg_scores
        ]).cpu().numpy()

        labels = np.concatenate([
            np.ones(len(pos_scores)),
            np.zeros(len(neg_scores))
        ])

        probabilities = 1 / (
            1 + np.exp(-np.clip(scores, -50, 50))
        )

        auc = roc_auc_score(labels, probabilities)

        average_precision = average_precision_score(
            labels,
            probabilities
        )

    return auc, average_precision


# ============================================================
# TRAINING LOOP
# ============================================================

best_val_auc = -1
best_epoch = 0
best_state = None
epochs_without_improvement = 0

history = []

print("=" * 70)
print("ATMOGRAPH - GRAPHSAGE LINK PREDICTION")
print("=" * 70)

print("Nodes:", num_nodes)
print("Input features:", x.shape[1])
print("Training positive edges:", len(train_pos))
print("Training negative edges:", len(train_neg))
print("Device:", DEVICE)

for epoch in range(1, EPOCHS + 1):

    encoder.train()
    decoder.train()

    optimizer.zero_grad()

    embeddings = encoder(x, edge_index)

    positive_scores = decoder(
        embeddings, train_pos
    )

    negative_scores = decoder(
        embeddings, train_neg
    )

    scores = torch.cat([
        positive_scores,
        negative_scores
    ])

    labels = torch.cat([
        torch.ones(len(positive_scores)),
        torch.zeros(len(negative_scores))
    ])

    loss = F.binary_cross_entropy_with_logits(
        scores,
        labels
    )

    loss.backward()

    optimizer.step()

    val_auc, val_ap = evaluate(
        val_pos,
        val_neg
    )

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
            "encoder": copy.deepcopy(
                encoder.state_dict()
            ),
            "decoder": copy.deepcopy(
                decoder.state_dict()
            )
        }

        epochs_without_improvement = 0

    else:

        epochs_without_improvement += 1

    if epoch == 1 or epoch % 10 == 0:

        print(
            f"Epoch {epoch:03d} | "
            f"Loss: {loss.item():.4f} | "
            f"Val ROC-AUC: {val_auc:.4f} | "
            f"Val AP: {val_ap:.4f}"
        )

    if epochs_without_improvement >= PATIENCE:

        print(
            f"\nEarly stopping at epoch {epoch}."
        )
        break


# ============================================================
# RESTORE BEST MODEL
# ============================================================

encoder.load_state_dict(best_state["encoder"])
decoder.load_state_dict(best_state["decoder"])

# ============================================================
# FINAL TEST EVALUATION
# ============================================================

test_auc, test_ap = evaluate(
    test_pos,
    test_neg
)

print("\n" + "=" * 70)
print("FINAL GRAPHSAGE RESULTS")
print("=" * 70)

print("Best epoch:", best_epoch)
print("Best validation ROC-AUC:", round(best_val_auc, 4))
print("Test ROC-AUC:", round(test_auc, 4))
print("Test Average Precision:", round(test_ap, 4))

# ============================================================
# SAVE MODEL
# ============================================================

model_path = MODEL_DIR / "graphsage_link_prediction.pt"

torch.save({
    "encoder_state_dict": encoder.state_dict(),
    "decoder_state_dict": decoder.state_dict(),
    "input_channels": x.shape[1],
    "hidden_channels": HIDDEN_CHANNELS,
    "embedding_channels": EMBEDDING_CHANNELS,
    "best_epoch": best_epoch
}, model_path)

# Save node embeddings
encoder.eval()

with torch.no_grad():
    embeddings = encoder(x, edge_index).numpy()

np.save(
    MODEL_DIR / "graphsage_node_embeddings.npy",
    embeddings
)

# Save training history
pd.DataFrame(history).to_csv(
    REPORT_DIR / "graphsage_training_history.csv",
    index=False
)

# Save evaluation metrics
results = {
    "task": "directed_link_prediction",
    "dataset": "AnonNet",
    "nodes": int(num_nodes),
    "input_features": int(x.shape[1]),
    "training_edges": int(len(train_pos)),
    "validation_edges": int(len(val_pos)),
    "test_edges": int(len(test_pos)),
    "best_epoch": int(best_epoch),
    "validation_roc_auc": float(best_val_auc),
    "test_roc_auc": float(test_auc),
    "test_average_precision": float(test_ap),
    "seed": SEED
}

with open(
    REPORT_DIR / "graphsage_results.json",
    "w"
) as file:

    json.dump(results, file, indent=4)

print("\nSaved model:", model_path)
print("Saved embeddings:", MODEL_DIR / "graphsage_node_embeddings.npy")
print("Saved training history:", REPORT_DIR / "graphsage_training_history.csv")
print("Saved metrics:", REPORT_DIR / "graphsage_results.json")

print("\nGraphSAGE training completed.")
