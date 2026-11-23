
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT / "ml" / "reports" /
    "propagation_monte_carlo_runs.csv"
)

OUTPUT_FILE = (
    ROOT / "ml" / "reports" /
    "propagation_statistical_analysis.csv"
)

BOOTSTRAP_RESAMPLES = 5000
RANDOM_SEED = 42

def bootstrap_intervals(values, rng):

    values = np.asarray(values)
    n = len(values)

    bootstrap_means = np.empty(BOOTSTRAP_RESAMPLES)
    bootstrap_medians = np.empty(BOOTSTRAP_RESAMPLES)

    for i in range(BOOTSTRAP_RESAMPLES):

        sample = rng.choice(values, size=n, replace=True)

        bootstrap_means[i] = np.mean(sample)
        bootstrap_medians[i] = np.median(sample)

    mean_ci = np.percentile(
        bootstrap_means, [2.5, 97.5]
    )

    median_ci = np.percentile(
        bootstrap_medians, [2.5, 97.5]
    )

    return mean_ci, median_ci

def main():

    df = pd.read_csv(INPUT_FILE)

    rng = np.random.default_rng(RANDOM_SEED)

    records = []

    for probability, group in df.groupby(
        "transmission_probability"
    ):

        affected = group["total_affected"].to_numpy()

        mean = np.mean(affected)
        median = np.median(affected)
        standard_deviation = np.std(affected, ddof=1)

        standard_error = (
            standard_deviation / np.sqrt(len(affected))
        )

        normal_ci_lower = mean - 1.96 * standard_error
        normal_ci_upper = mean + 1.96 * standard_error

        mean_ci, median_ci = bootstrap_intervals(
            affected, rng
        )

        records.append({
            "transmission_probability": probability,
            "simulation_count": len(group),
            "mean_affected": mean,
            "median_affected": median,
            "std_affected": standard_deviation,
            "min_affected": np.min(affected),
            "percentile_25": np.percentile(affected, 25),
            "percentile_75": np.percentile(affected, 75),
            "percentile_95": np.percentile(affected, 95),
            "max_affected": np.max(affected),

            "normal_ci_95_lower": normal_ci_lower,
            "normal_ci_95_upper": normal_ci_upper,

            "bootstrap_mean_ci_lower": mean_ci[0],
            "bootstrap_mean_ci_upper": mean_ci[1],

            "bootstrap_median_ci_lower": median_ci[0],
            "bootstrap_median_ci_upper": median_ci[1],

            "mean_percentage_affected": (
                group["percentage_affected"].mean()
            )
        })

    summary = pd.DataFrame(records).round(4)

    print("\nATMOGRAPH - BOOTSTRAP STATISTICAL ANALYSIS")
    print("=" * 90)

    print(summary.to_string(index=False))

    summary.to_csv(OUTPUT_FILE, index=False)

    print("\nBootstrap analysis completed successfully.")
    print("Bootstrap resamples per probability:", BOOTSTRAP_RESAMPLES)
    print("Random seed:", RANDOM_SEED)
    print("Report saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    main()