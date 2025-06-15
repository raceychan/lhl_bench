import json
import matplotlib.pyplot as plt
from pathlib import Path


def load_results() -> dict[str, dict[str, float]]:
    """Load benchmark results from JSON file."""
    results_path = Path("benchmark_results.json")
    if results_path.exists():
        with open(results_path, 'r') as f:
            return json.load(f)
    return {}


# Load results from JSON file
results = load_results()
COMPLEX_RESULT = results.get("complex", {})
PING_PONG_RESULT = results.get("ping_pong", {})

# Sort frameworks by RPS descending


def make_graph(result: dict[str, float], save_dir: str, graph_name: str):
    # Create the bar chart
    sorted_frameworks, sorted_rps = zip(
        *dict(sorted(result.items(), key=lambda item: item[1], reverse=True)).items()
    )

    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        sorted_frameworks,
        sorted_rps,
    )

    # Add labels and title
    plt.xlabel("Framework (Sorted by RPS)")
    plt.ylabel("Requests per Second (RPS)")
    plt.title("RPS Comparison Across Python Web Frameworks (High to Low)")
    plt.ylim(0, max(sorted_rps) + 5000)  # Dynamic Y-axis

    # Annotate bars with RPS values
    for bar, value in zip(bars, sorted_rps):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 500,
            f"{value:.0f}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(save_dir + f"/{graph_name}.png")
    plt.close()


if __name__ == "__main__":
    # Reload results to ensure we have the latest data
    results = load_results()
    complex_result = results.get("complex", {})
    ping_pong_result = results.get("ping_pong", {})
    
    if complex_result:
        make_graph(complex_result, "./assets", "bench_complex")
    if ping_pong_result:
        make_graph(ping_pong_result, "./assets", "bench_ping")
