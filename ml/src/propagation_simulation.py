
from pathlib import Path
import random

import networkx as nx
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = (
    ROOT / "ml" / "data" / "raw"
    / "anon-network-main"
    / "mim2025_network_challenge"
)

NODES_FILE = DATA_DIR / "nodes_anon.csv"
EDGES_FILE = DATA_DIR / "edges_anon.csv"


def load_network():
    nodes = pd.read_csv(NODES_FILE)
    edges = pd.read_csv(EDGES_FILE)

    graph = nx.DiGraph()

    graph.add_nodes_from(nodes["id"].dropna().astype(str))

    graph.add_edges_from(
        edges[["source", "target"]]
        .astype(str)
        .itertuples(index=False, name=None)
    )

    return graph



def simulate_cascade(
    graph,
    seed_node,
    transmission_probability=0.10,
    max_steps=10,
    random_seed=42
):
    if seed_node not in graph:
        raise ValueError(f"Node {seed_node} does not exist.")

    if not 0 <= transmission_probability <= 1:
        raise ValueError(
            "Transmission probability must be between 0 and 1."
        )

    rng = random.Random(random_seed)

    affected = {seed_node}
    frontier = {seed_node}

    results = [{
        "step": 0,
        "newly_affected": 1,
        "total_affected": 1
    }]

    for step in range(1, max_steps + 1):
        newly_affected = set()

        for node in sorted(frontier):
            for neighbor in sorted(graph.successors(node)):

                if neighbor in affected:
                    continue

                if rng.random() < transmission_probability:
                    newly_affected.add(neighbor)

        affected.update(newly_affected)
        frontier = newly_affected

        results.append({
            "step": step,
            "newly_affected": len(newly_affected),
            "total_affected": len(affected)
        })

        if not frontier:
            break

    naturally_terminated = len(frontier) == 0

    return results, affected, naturally_terminated




def main():
    graph = load_network()

    seed_node = "n5063"
    probabilities = [0.05, 0.10, 0.20, 0.30]
    max_steps = 50
    num_simulations = 100

    print("\nATMOGRAPH - MONTE CARLO PROPAGATION ANALYSIS")
    print("=" * 65)

    print("Network nodes:", graph.number_of_nodes())
    print("Network edges:", graph.number_of_edges())
    print("Initial node:", seed_node)
    print("Simulations per probability:", num_simulations)
    print("Maximum propagation steps:", max_steps)

    all_results = []

    for probability in probabilities:

        affected_counts = []
        steps_completed = []
        natural_terminations = 0

        for run in range(num_simulations):

            results, affected, naturally_terminated = simulate_cascade(
                graph,
                seed_node,
                transmission_probability=probability,
                max_steps=max_steps,
                random_seed=42 + run
            )

            affected_counts.append(len(affected))
            steps_completed.append(results[-1]["step"])

            if naturally_terminated:
                natural_terminations += 1

            all_results.append({
                "transmission_probability": probability,
                "simulation": run + 1,
                "total_affected": len(affected),
                "percentage_affected": (
                    len(affected) / graph.number_of_nodes()
                ) * 100,
                "steps_completed": results[-1]["step"],
                "naturally_terminated": naturally_terminated
            })

        print("\nTransmission probability:", probability)
        print("Mean affected:", round(
            sum(affected_counts) / num_simulations, 2
        ))
        print("Minimum affected:", min(affected_counts))
        print("Maximum affected:", max(affected_counts))
        print("Naturally terminated:", natural_terminations)
        print("Reached step limit:", num_simulations - natural_terminations)

    runs_df = pd.DataFrame(all_results)

    summary_df = (
        runs_df.groupby("transmission_probability")
        .agg(
            mean_affected=("total_affected", "mean"),
            std_affected=("total_affected", "std"),
            min_affected=("total_affected", "min"),
            max_affected=("total_affected", "max"),
            mean_percentage_affected=("percentage_affected", "mean"),
            mean_steps=("steps_completed", "mean"),
            naturally_terminated=("naturally_terminated", "sum")
        )
        .reset_index()
        .round(4)
    )

    print("\n\nMONTE CARLO SUMMARY")
    print("=" * 65)
    print(summary_df.to_string(index=False))

    report_dir = ROOT / "ml" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    runs_df.to_csv(
        report_dir / "propagation_monte_carlo_runs.csv",
        index=False
    )

    summary_df.to_csv(
        report_dir / "propagation_monte_carlo_summary.csv",
        index=False
    )

    print("\nIndividual runs and summary reports saved successfully.")


if __name__ == "__main__":
    main()
