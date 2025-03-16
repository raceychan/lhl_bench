import matplotlib.pyplot as plt

# Define frameworks and their corresponding RPS values
frameworks = ["Lihil", "Litestar", "FastAPI", "Starlette", "Blacksheep"]
rps = [35135.64, 21905.83, 5672.98, 35560.72, 29732.23]

# Sort frameworks by RPS descending
sorted_data = sorted(zip(frameworks, rps), key=lambda x: x[1], reverse=True)
sorted_frameworks, sorted_rps = zip(*sorted_data)

# Create the bar chart
plt.figure(figsize=(10, 6))
bars = plt.bar(
    sorted_frameworks, sorted_rps, color=["purple", "blue", "orange", "green", "red"]
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
plt.savefig("./assets/benchmark.png")
plt.close()
