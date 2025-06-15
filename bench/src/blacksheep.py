from blacksheep import (
    Application,
    FromJSON,
    FromQuery,
    JSONContent,
    Response,
    TextContent,
    get,
)

from .shared import Engine, User, get_engine

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
    user = User(id=user.id, name=user.name, email=user.email)
    return Response(status=200, content=JSONContent(user.asdict()))


@get("/ping")
async def pong():
    return Response(status=200, content=TextContent("pong"))
