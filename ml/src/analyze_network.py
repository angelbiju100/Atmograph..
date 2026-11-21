
from pathlib import Path
import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

DATA = ROOT / "data" / "raw" / "anon-network-main" / "mim2025_network_challenge"

nodes = pd.read_csv(DATA / "nodes_anon.csv")
edges = pd.read_csv(DATA / "edges_anon.csv")

# Build directed graph initially, preserving source-target direction
G = nx.from_pandas_edgelist(
    edges,
    source="source",
    target="target",
    create_using=nx.DiGraph()
)

node_ids = set(nodes["id"])
edge_ids = set(edges["source"]) | set(edges["target"])

print("NETWORK VALIDATION")
print("=" * 40)

print("Nodes in dataset:", len(node_ids))
print("Nodes in graph:", G.number_of_nodes())
print("Edges in dataset:", len(edges))
print("Edges in graph:", G.number_of_edges())

print("\nEDGE QUALITY")
print("Duplicate edges:", edges.duplicated().sum())
print("Self-loops:", nx.number_of_selfloops(G))
print("Unknown node references:", len(edge_ids - node_ids))
print("Nodes without connections:", len(node_ids - edge_ids))

print("\nNETWORK STRUCTURE")
print("Is directed:", nx.is_directed(G))
print("Weakly connected components:",
      nx.number_weakly_connected_components(G))
print("Largest weak component:",
      max(len(c) for c in nx.weakly_connected_components(G)))

print("\nDEGREE STATISTICS")
print("Average in-degree:",
      sum(dict(G.in_degree()).values()) / G.number_of_nodes())
print("Average out-degree:",
      sum(dict(G.out_degree()).values()) / G.number_of_nodes())
print("Maximum in-degree:",
      max(dict(G.in_degree()).values()))
print("Maximum out-degree:",
      max(dict(G.out_degree()).values()))
