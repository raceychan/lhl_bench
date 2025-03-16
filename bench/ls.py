from litestar import Litestar, Router, post
from litestar.di import Provide
from litestar.params import Body, Parameter

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


profile_router = Router(
    path="/profile",
    route_handlers=[profile_handler],
    dependencies={"engine": Provide(get_engine)},
)

app = Litestar(
    route_handlers=[profile_router],
)
