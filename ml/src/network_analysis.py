
from pathlib import Path
import pandas as pd
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]

DATA = (
    ROOT / "data" / "raw" /
    "anon-network-main" /
    "mim2025_network_challenge"
)

nodes = pd.read_csv(DATA / "nodes_anon.csv")
edges = pd.read_csv(DATA / "edges_anon.csv")

# Construct directed supply-chain graph
G = nx.from_pandas_edgelist(
    edges,
    source="source",
    target="target",
    create_using=nx.DiGraph()
)

# Calculate connectivity
in_degree = dict(G.in_degree())
out_degree = dict(G.out_degree())

nodes["in_degree"] = nodes["id"].map(in_degree)
nodes["out_degree"] = nodes["id"].map(out_degree)

# Rank highly connected nodes
nodes["total_degree"] = (
    nodes["in_degree"] + nodes["out_degree"]
)
# Calculate additional network centrality measures
print("\nCalculating network centrality...")

betweenness = nx.betweenness_centrality(
    G,
    normalized=True
)

pagerank = nx.pagerank(G)

nodes["betweenness"] = nodes["id"].map(betweenness)
nodes["pagerank"] = nodes["id"].map(pagerank)

# Rank nodes by different centrality measures
print("\nTOP 10 NODES BY BETWEENNESS")
print(
    nodes.sort_values("betweenness", ascending=False)[
        ["id", "location", "betweenness", "total_degree"]
    ].head(10).to_string(index=False)
)

print("\nTOP 10 NODES BY PAGERANK")
print(
    nodes.sort_values("pagerank", ascending=False)[
        ["id", "location", "pagerank", "total_degree"]
    ].head(10).to_string(index=False)
)
print("\nNETWORK SUMMARY")
print("=" * 45)
print("Total nodes:", G.number_of_nodes())
print("Total edges:", G.number_of_edges())
print("Average in-degree:", round(
    sum(in_degree.values()) / len(in_degree), 2
))
print("Average out-degree:", round(
    sum(out_degree.values()) / len(out_degree), 2
))

print("\nTOP 10 NODES BY TOTAL DEGREE")
print(
    nodes.sort_values(
        "total_degree", ascending=False
    )[
        ["id", "location", "products",
         "in_degree", "out_degree", "total_degree"]
    ].head(10).to_string(index=False)
)

# Simulate removal of critical network nodes
print("\nNODE DISRUPTION SIMULATION")
print("=" * 50)

def simulate_node_disruption(graph, node_id):
    simulated_graph = graph.copy()

    # Remove the selected entity
    simulated_graph.remove_node(node_id)

    # Measure remaining network connectivity
    components = list(
        nx.weakly_connected_components(simulated_graph)
    )

    largest_component = max(
        (len(component) for component in components),
        default=0
    )

    return {
        "node_removed": node_id,
        "remaining_nodes": simulated_graph.number_of_nodes(),
        "remaining_edges": simulated_graph.number_of_edges(),
        "weakly_connected_components": len(components),
        "largest_component_size": largest_component,
        "nodes_outside_largest_component":
            simulated_graph.number_of_nodes() - largest_component
    }


baseline_components = list(nx.weakly_connected_components(G))
baseline_largest = max(len(c) for c in baseline_components)

print("Original largest component:", baseline_largest)

critical_nodes = ["n4859", "n5063", "n6211"]

for node_id in critical_nodes:
    result = simulate_node_disruption(G, node_id)

    print(f"\nRemoving {node_id}:")
    for key, value in result.items():
        print(f"{key}: {value}")

# Save analysis
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

nodes.to_csv(
    REPORT_DIR / "network_node_analysis.csv",
    index=False
)

print("\nSaved: reports/network_node_analysis.csv")

