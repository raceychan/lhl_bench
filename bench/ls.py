from litestar import Litestar, Router, post
from litestar.di import Provide
from litestar.params import Body, Parameter

from .data import Engine, User, get_engine


# Dependency provider for the route
async def provide_engine() -> Engine:
    return get_engine()


# Handler function
@post("/{pid:str}")
async def profile_handler(
    pid: str = Parameter(),  # From path
    q: int = Parameter(query="q"),  # From query string ?q=123
    data: User = Body(),  # Changed from 'user' to 'data'
    engine: Engine = Provide(provide_engine),  # Injected dependency
) -> User:
    return User(id=data.id, name=data.name, email=data.email)


# Router
profile_router = Router(
    path="/profile",
    route_handlers=[profile_handler],
    dependencies={"engine": Provide(provide_engine)},
)

# App instance
app = Litestar(
    route_handlers=[profile_router],
)
