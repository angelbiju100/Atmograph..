
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"

REPORTS.mkdir(exist_ok=True)

# Load datasets
syndelay = pd.read_csv(
    RAW / "syndelay-main" / "data" / "syndelay_v1.csv"
)

anon_path = RAW / "anon-network-main" / "mim2025_network_challenge"

nodes = pd.read_csv(anon_path / "nodes_anon.csv")
edges = pd.read_csv(anon_path / "edges_anon.csv")

report = []

report.append("ATMOGRAPH - DATASET INSPECTION REPORT")
report.append("=" * 50)

for name, df in [
    ("SynDelay", syndelay),
    ("AnonNet Nodes", nodes),
    ("AnonNet Edges", edges),
]:
    report.append(f"\n{name}")
    report.append("-" * 40)
    report.append(f"Rows: {df.shape[0]}")
    report.append(f"Columns: {df.shape[1]}")
    report.append(f"Column names: {df.columns.tolist()}")
    report.append("\nMissing values:")
    report.append(df.isnull().sum().to_string())

report.append("\n\nSynDelay Label Distribution")
report.append("-" * 40)
report.append(syndelay["label"].value_counts().sort_index().to_string())

report.append("\n\nAnonNet Network Statistics")
report.append("-" * 40)
report.append(f"Unique nodes: {nodes['id'].nunique()}")
report.append(f"Unique edge sources: {edges['source'].nunique()}")
report.append(f"Unique edge targets: {edges['target'].nunique()}")
report.append(f"Total edges: {len(edges)}")

output = "\n".join(report)

output_path = REPORTS / "dataset_inspection.txt"
output_path.write_text(output, encoding="utf-8")

print(output)
print(f"\nReport saved to: {output_path}")
