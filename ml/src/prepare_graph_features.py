
import numpy as np
import pandas as pd

from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    ROOT / "ml" / "data" / "raw"
    / "anon-network-main" / "mim2025_network_challenge"
)

OUTPUT_DIR = ROOT / "ml" / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

nodes = pd.read_csv(DATA_DIR / "nodes_anon.csv")
edges = pd.read_csv(DATA_DIR / "edges_anon.csv")

# Preserve the original node order
nodes["location"] = nodes["location"].fillna("Unknown")
nodes["products"] = nodes["products"].fillna("")

# 1. One-hot encode location
location_features = pd.get_dummies(
    nodes["location"],
    prefix="location",
    dtype=np.float32
)

# 2. Convert product descriptions into TF-IDF features
def split_products(text):
    return [
        item.strip().lower()
        for item in text.split(",")
        if item.strip()
    ]

vectorizer = TfidfVectorizer(
    tokenizer=split_products,
    token_pattern=None,
    lowercase=False,
    max_features=512,
    dtype=np.float32
)

product_matrix = vectorizer.fit_transform(nodes["products"])

product_features = pd.DataFrame(
    product_matrix.toarray(),
    columns=[
        f"product_{name}"
        for name in vectorizer.get_feature_names_out()
    ],
    dtype=np.float32
)

# 3. Calculate network degree features
in_degree = edges["target"].value_counts()
out_degree = edges["source"].value_counts()

degree_features = pd.DataFrame({
    "log_in_degree": np.log1p(
        nodes["id"].map(in_degree).fillna(0)
    ),
    "log_out_degree": np.log1p(
        nodes["id"].map(out_degree).fillna(0)
    )
}, dtype=np.float32)

# 4. Combine all features
features = pd.concat(
    [
        location_features.reset_index(drop=True),
        product_features.reset_index(drop=True),
        degree_features.reset_index(drop=True)
    ],
    axis=1
)

feature_matrix = features.to_numpy(dtype=np.float32)

# 5. Save outputs
np.save(
    OUTPUT_DIR / "node_features.npy",
    feature_matrix
)

nodes[["id"]].to_csv(
    OUTPUT_DIR / "node_feature_ids.csv",
    index=False
)

pd.Series(features.columns).to_csv(
    OUTPUT_DIR / "node_feature_names.csv",
    index=False,
    header=["feature_name"]
)

print("=" * 70)
print("ATMOGRAPH - NODE FEATURE PREPARATION")
print("=" * 70)

print("Number of nodes:", len(nodes))
print("Feature matrix shape:", feature_matrix.shape)
print("Location features:", location_features.shape[1])
print("Product features:", product_features.shape[1])
print("Degree features:", degree_features.shape[1])
print("Missing values:", np.isnan(feature_matrix).sum())
print("Infinite values:", np.isinf(feature_matrix).sum())

print("\nSaved files:")
print(OUTPUT_DIR / "node_features.npy")
print(OUTPUT_DIR / "node_feature_ids.csv")
print(OUTPUT_DIR / "node_feature_names.csv")

print("\nFeature preparation completed.")
