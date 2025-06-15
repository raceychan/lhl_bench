graph:
	uv run python make_graph.py

auto-bench:
	python auto_bench.py

bench-single:
	python auto_bench.py $(FRAMEWORK)