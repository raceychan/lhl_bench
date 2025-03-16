lhl:
	uv run uvicorn bench.lhl:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

ls:
	uv run uvicorn bench.ls:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

fa:
	uv run uvicorn bench.fa:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

slt:
	uv run uvicorn bench.slt:app --interface asgi3 --http httptools --no-access-log --log-level "warning"

bs:
	uv run uvicorn bench.bs:app --interface asgi3 --http httptools --no-access-log --log-level "warning"