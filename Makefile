lhl:
	uv run uvicorn bench.lhl:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

ls:
	uv run uvicorn bench.ls:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

fa:
	uv run uvicorn bench.fa:app --interface asgi3 --http httptools --no-access-log --log-level "warning"