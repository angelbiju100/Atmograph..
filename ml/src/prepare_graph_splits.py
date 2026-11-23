
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    ROOT / "ml" / "data" / "raw"
    / "anon-network-main" / "mim2025_network_challenge"
)

OUTPUT_DIR = ROOT / "ml" / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = 42
rng = np.random.default_rng(RANDOM_SEED)

# 1. Load nodes and edges
nodes = pd.read_csv(DATA_DIR / "nodes_anon.csv")
edges = pd.read_csv(DATA_DIR / "edges_anon.csv")

node_ids = nodes["id"].tolist()
node_to_index = {
    node_id: index
    for index, node_id in enumerate(node_ids)
}

num_nodes = len(node_ids)

# 2. Convert directed edges into integer indices
edges = edges.drop_duplicates(subset=["source", "target"])

source = edges["source"].map(node_to_index).to_numpy()
target = edges["target"].map(node_to_index).to_numpy()

edge_array = np.column_stack([source, target]).astype(np.int64)

# Remove self-loops for this link-prediction experiment
edge_array = edge_array[
    edge_array[:, 0] != edge_array[:, 1]
]

# 3. Shuffle and split positive edges
rng.shuffle(edge_array)

num_edges = len(edge_array)

train_end = int(num_edges * 0.80)
val_end = int(num_edges * 0.90)

train_edges = edge_array[:train_end]
val_edges = edge_array[train_end:val_end]
test_edges = edge_array[val_end:]

# 4. Build a set of all existing directed edges
all_positive_edges = set(
    map(tuple, edge_array.tolist())
)

# 5. Generate negative directed edges
def generate_negative_edges(count, rng):
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

            if attempts >= max_attempts:
                break

    if len(negatives) != count:
        raise RuntimeError(
            "Could not generate the required negative edges."
        )

    return np.array(sorted(negatives), dtype=np.int64)


val_negative_edges = generate_negative_edges(
    len(val_edges), rng
)

test_negative_edges = generate_negative_edges(
    len(test_edges), rng
)

# 6. Save graph splits
np.save(OUTPUT_DIR / "train_edges.npy", train_edges)
np.save(OUTPUT_DIR / "val_edges.npy", val_edges)
np.save(OUTPUT_DIR / "test_edges.npy", test_edges)

np.save(
    OUTPUT_DIR / "val_negative_edges.npy",
    val_negative_edges
)

np.save(
    OUTPUT_DIR / "test_negative_edges.npy",
    test_negative_edges
)

# 7. Save training graph edges for GraphSAGE message passing
np.save(
    OUTPUT_DIR / "message_passing_edges.npy",
    train_edges
)

# 8. Print verification
print("=" * 70)
print("ATMOGRAPH - GRAPH DATASET SPLITTING")
print("=" * 70)

print("Total nodes:", num_nodes)
print("Unique directed edges after self-loop removal:", num_edges)

print("\nPositive edge splits:")
print("Training:", len(train_edges))
print("Validation:", len(val_edges))
print("Testing:", len(test_edges))

print("\nNegative edge splits:")
print("Validation:", len(val_negative_edges))
print("Testing:", len(test_negative_edges))

print("\nLeakage checks:")
print(
    "Train/validation overlap:",
    len(set(map(tuple, train_edges)) &
        set(map(tuple, val_edges)))
)

print(
    "Train/test overlap:",
    len(set(map(tuple, train_edges)) &
        set(map(tuple, test_edges)))
)

print(
    "Validation negative edges overlapping positives:",
    len(set(map(tuple, val_negative_edges)) &
        all_positive_edges)
)

print(
    "Test negative edges overlapping positives:",
    len(set(map(tuple, test_negative_edges)) &
        all_positive_edges)
)

print("\nSaved files in:", OUTPUT_DIR)
print("\nGraph splitting completed.")
