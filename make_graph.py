import matplotlib.pyplot as plt

COMPLEX_RESULT: dict[str, float] = {
    "Lihil": 35135.64,
    "Starlette": 30950.06,
    "Blacksheep": 29732.23,
    "Litestar": 21905.83,
    "Robyn": 14683.57,
    "FastAPI": 5672.98,
}

PING_PONG_RESULT: dict[str, float] = {
    "Lihil": 56359.57,
    "Starlette": 45039.65,
    "Blacksheep": 51031.89,
    "Litestar": 34523.74,
    "Robyn": 20874.14,
    "FastAPI": 31539.92,
}

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
    make_graph(COMPLEX_RESULT, "./assets", "bench_complex")
    make_graph(PING_PONG_RESULT, "./assets", "bench_ping")
