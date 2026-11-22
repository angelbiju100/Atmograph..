from pathlib import Path

import networkx as nx
import pandas as pd

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = (
    ROOT / "ml" / "data" / "raw"
    / "anon-network-main"
    / "mim2025_network_challenge"
)

REPORT_FILE = ROOT / "ml" / "reports" / "network_node_analysis.csv"


# --------------------------------------------------
# API CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="AtmoGraph API",
    description="Supply-chain network analysis and disruption simulation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# LOAD NETWORK DATA
# --------------------------------------------------

nodes = None
edges = None
G = None


def load_network():
    global nodes, edges, G

    if G is not None:
        return

    nodes_file = DATA_DIR / "nodes_anon.csv"
    edges_file = DATA_DIR / "edges_anon.csv"

    if not nodes_file.exists() or not edges_file.exists():
        raise RuntimeError(
            "AnonNet dataset files not found. "
            "Check the ml/data/raw directory."
        )

    nodes = pd.read_csv(nodes_file)
    edges = pd.read_csv(edges_file)

    G = nx.DiGraph()

    # Include all dataset nodes, including any isolates
    G.add_nodes_from(nodes["id"].dropna().astype(str))

    G.add_edges_from(
        edges[["source", "target"]]
        .astype(str)
        .itertuples(index=False, name=None)
    )

    # Reuse the existing centrality report when available
    if REPORT_FILE.exists():
        analysis = pd.read_csv(REPORT_FILE)
        nodes = nodes.merge(
            analysis[
                [
                    "id",
                    "in_degree",
                    "out_degree",
                    "total_degree",
                    "betweenness",
                    "pagerank"
                ]
            ],
            on="id",
            how="left",
            suffixes=("", "_report")
        )

        for column in [
            "in_degree",
            "out_degree",
            "total_degree",
            "betweenness",
            "pagerank"
        ]:
            report_column = f"{column}_report"

            if report_column in nodes.columns:
                if column in nodes.columns:
                    nodes[column] = nodes[column].fillna(
                        nodes[report_column]
                    )
                else:
                    nodes[column] = nodes[report_column]

                nodes.drop(columns=[report_column], inplace=True)

    else:
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())

        nodes["in_degree"] = nodes["id"].map(in_degree)
        nodes["out_degree"] = nodes["id"].map(out_degree)
        nodes["total_degree"] = (
            nodes["in_degree"] + nodes["out_degree"]
        )

        nodes["betweenness"] = pd.Series(
            nx.betweenness_centrality(G)
        )
        nodes["pagerank"] = nodes["id"].map(
            nx.pagerank(G)
        )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AtmoGraph API"
    }


# --------------------------------------------------
# NETWORK SUMMARY
# --------------------------------------------------

@app.get("/api/network/summary")
def network_summary():
    load_network()

    components = list(nx.weakly_connected_components(G))

    largest_component = max(
        (len(component) for component in components),
        default=0
    )

    node_count = G.number_of_nodes()

    return {
        "total_nodes": node_count,
        "total_edges": G.number_of_edges(),
        "average_in_degree": round(
            sum(dict(G.in_degree()).values()) / node_count, 2
        ) if node_count else 0,
        "average_out_degree": round(
            sum(dict(G.out_degree()).values()) / node_count, 2
        ) if node_count else 0,
        "weakly_connected_components": len(components),
        "largest_component_size": largest_component,
        "self_loops": nx.number_of_selfloops(G)
    }


# --------------------------------------------------
# TOP CRITICAL NODES
# --------------------------------------------------

@app.get("/api/network/top-nodes")
def top_nodes(
    sort_by: str = Query(
        "betweenness",
        pattern="^(total_degree|betweenness|pagerank)$"
    ),
    limit: int = Query(10, ge=1, le=100)
):
    load_network()

    result = nodes.sort_values(
        sort_by,
        ascending=False
    ).head(limit)

    result = result.astype(object).where(
        pd.notna(result), None
    )

    return {
        "sort_by": sort_by,
        "count": len(result),
        "nodes": result.to_dict(orient="records")
    }


# --------------------------------------------------
# INDIVIDUAL NODE DETAILS
# --------------------------------------------------

@app.get("/api/network/nodes/{node_id}")
def node_details(node_id: str):
    load_network()

    result = nodes[nodes["id"].astype(str) == node_id]

    if result.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Node {node_id} not found"
        )

    record = result.iloc[0].to_dict()

    return {
        key: (
            value if pd.notna(value) else None
        )
        for key, value in record.items()
    }

@app.get("/api/network/nodes/{node_id}/neighbors")
def node_neighbors(node_id: str):
    load_network()

    if node_id not in G:
        raise HTTPException(
            status_code=404,
            detail=f"Node {node_id} not found"
        )

    incoming_ids = list(G.predecessors(node_id))
    outgoing_ids = list(G.successors(node_id))

    def get_node_info(neighbor_id):
        result = nodes[
            nodes["id"].astype(str) == str(neighbor_id)
        ]

        if result.empty:
            return {
                "id": neighbor_id,
                "location": None,
                "products": None
            }

        record = result.iloc[0]

        return {
            "id": neighbor_id,
            "location": (
                record["location"]
                if pd.notna(record["location"])
                else None
            ),
            "products": (
                record["products"]
                if pd.notna(record["products"])
                else None
            )
        }

    incoming = [
        get_node_info(neighbor_id)
        for neighbor_id in incoming_ids
    ]

    outgoing = [
        get_node_info(neighbor_id)
        for neighbor_id in outgoing_ids
    ]

    return {
        "node_id": node_id,
        "incoming_count": len(incoming),
        "outgoing_count": len(outgoing),
        "incoming_neighbors": incoming,
        "outgoing_neighbors": outgoing
    }



# --------------------------------------------------
# NODE DISRUPTION SIMULATION
# --------------------------------------------------

@app.post("/api/network/simulate/{node_id}")
def simulate_disruption(node_id: str):
    load_network()

    if node_id not in G:
        raise HTTPException(
            status_code=404,
            detail=f"Node {node_id} not found"
        )

    baseline_components = nx.number_weakly_connected_components(G)

    baseline_largest = max(
        (
            len(component)
            for component in nx.weakly_connected_components(G)
        ),
        default=0
    )

    simulated_graph = G.copy()
    simulated_graph.remove_node(node_id)

    components = list(
        nx.weakly_connected_components(simulated_graph)
    )

    largest_component = max(
        (len(component) for component in components),
        default=0
    )

    remaining_nodes = simulated_graph.number_of_nodes()

    return {
        "node_removed": node_id,
        "original_nodes": G.number_of_nodes(),
        "original_edges": G.number_of_edges(),
        "remaining_nodes": remaining_nodes,
        "remaining_edges": simulated_graph.number_of_edges(),
        "original_components": baseline_components,
        "resulting_components": len(components),
        "original_largest_component": baseline_largest,
        "largest_component_after_removal": largest_component,
        "nodes_outside_largest_component": (
            remaining_nodes - largest_component
        ),
        "interpretation": (
            "Structural node-removal simulation. "
            "This does not represent an observed real-world disruption."
        )
    }


# --------------------------------------------------
# STARTUP
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    load_network()
    print("AtmoGraph network data loaded successfully.")
    print("Nodes:", G.number_of_nodes())
    print("Edges:", G.number_of_edges())
