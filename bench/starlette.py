from litestar import Litestar, Router, get, post
from litestar.di import Provide
from litestar.params import Body, Parameter

from typing import Literal
from .data import Engine, User, get_engine


@post("/{pid:str}")
async def profile_handler(
    pid: str = Parameter(),
    q: int = Parameter(query="q"),
    data: User = Body(),
    engine: Engine = Provide(get_engine),
) -> User:
    assert engine.url == pid and engine.nums == q
    return User(id=data.id, name=data.name, email=data.email)


@get("/ping")
async def ping() -> Literal["pong"]:
    return "pong"


profile_router = Router(
    path="/profile",
    route_handlers=[profile_handler],
    dependencies={"engine": Provide(get_engine)},
)

app = Litestar(
    route_handlers=[profile_router, ping],
)
