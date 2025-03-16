from blacksheep import Application, FromJSON, FromQuery, JSONContent, Response
from blacksheep.server.routing import Router
from msgspec.structs import asdict

from .data import Engine, User, get_engine

app = Application()


@app.router.post("/profile/{pid}")
async def profile_handler(
    pid: str,
    data: FromJSON[User],
    q: FromQuery[int] = FromQuery(""),
) -> Response:
    # Get engine
    engine: Engine = get_engine(pid=pid, q=q)
    assert engine.url == pid and engine.nums == q

    user = data.value

    result = User(id=user.id, name=user.name, email=user.email)
    return Response(status=200, content=JSONContent(asdict(result)))
