import matplotlib.pyplot as plt

RESULT: dict[str, float] = {
    "Lihil": 35135.64,
    "Starlette": 30950.06,
    "Blacksheep": 29732.23,
    "Litestar": 21905.83,
    "Robyn": 14683.57,
    "FastAPI": 5672.98,
}

# Sort frameworks by RPS descending


def make_graph(result: dict[str, float], path: str):
    # Create the bar chart
    sorted_frameworks, sorted_rps = zip(*result.items())
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
    plt.savefig(path)
    plt.close()


if __name__ == "__main__":
    make_graph(RESULT, "./assets/benchmark.png")
