lhl:
	uv run uvicorn bench.lhl:app --interface asgi3 --http httptools --no-access-log --log-level "warning"