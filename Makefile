lihil:
	uv run uvicorn bench.lihil:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

starlette:
	uv run uvicorn bench.starlette:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

fastapi:
	uv run uvicorn bench.fastapi:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

litestar:
	uv run uvicorn bench.litestar:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

blacksheep:
	uv run uvicorn bench.blacksheep:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

robyn:
	uv run python -m bench.robyn

sanic:
	uv run uvicorn bench.sanic:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

graph:
	uv run python make_graph.py

auto-bench:
	python auto_bench.py

bench-single:
	python auto_bench.py $(FRAMEWORK)