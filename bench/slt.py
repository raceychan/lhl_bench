from msgspec.json import decode, encode
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .data import Engine, User, get_engine


async def profile_handler(request: Request):
    pid = request.path_params["pid"]
    q = int(request.query_params.get("q", "0"))
    engine: Engine = get_engine(pid=pid, q=q)
    assert engine.url == pid and engine.nums == q
    body_bytes = await request.body()
    user = User(**decode(body_bytes))
    return Response(encode(User(id=user.id, name=user.name, email=user.email)))


routes = [
    Route("/profile/{pid}", profile_handler, methods=["POST"]),
]

app = Starlette(routes=routes)
