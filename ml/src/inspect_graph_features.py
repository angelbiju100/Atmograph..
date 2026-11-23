import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    ROOT
    / "ml"
    / "data"
    / "raw"
    / "anon-network-main"
    / "mim2025_network_challenge"
)

nodes = pd.read_csv(DATA_DIR / "nodes_anon.csv")

print("=" * 75)
print("ATMOGRAPH - GRAPH NODE FEATURE INSPECTION")
print("=" * 75)

print("\nDataset shape:")
print(nodes.shape)

print("\nColumns:")
print(nodes.columns.tolist())

print("\nData types:")
print(nodes.dtypes)

print("\nMissing values:")
print(nodes.isnull().sum())

print("\nUnique locations:")
print(nodes["location"].nunique())
print(nodes["location"].value_counts(dropna=False).head(20))

print("\nUnique products:")
print(nodes["products"].nunique())
print(nodes["products"].value_counts(dropna=False).head(20))

print("\nSample records:")
print(nodes.head(15).to_string(index=False))

print("\nGraph feature inspection completed.")