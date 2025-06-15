from lihil import Lihil, Route, Text

from .shared import Engine, User, get_engine

profile_route = Route("profile/{pid}")
profile_route.factory(get_engine)


@profile_route.post
async def profile(pid: str, q: int, user: User, engine: Engine) -> User:
    assert engine.url == pid and engine.nums == q
    return User(id=user.id, name=user.name, email=user.email)


ping = Route("/ping", to_thread=False)


@ping.get
def pong() -> Text:
    return "pong"


app = Lihil(profile_route)
