import json

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse
from starlette.routing import Route

from .data import Engine, User, get_engine


async def profile_handler(request: Request):
    pid = request.path_params["pid"]
    q = int(request.query_params.get("q", "0"))
    engine: Engine = get_engine(pid=pid, q=q)
    assert engine.url == pid and engine.nums == q
    body_bytes = await request.body()
    user = User(**json.loads(body_bytes))
    new_user = User(id=user.id, name=user.name, email=user.email).asdict()
    return JSONResponse(new_user)


async def ping(r: Request):
    return PlainTextResponse("pong")


routes = [
    Route("/ping", ping, methods=["GET"]),
    Route("/profile/{pid}", profile_handler, methods=["POST"]),
]

app = Starlette(routes=routes)
