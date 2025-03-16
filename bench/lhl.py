from lihil import Lihil, Route
from lihil.interface.marks import Body

from .data import Engine, User, get_engine

profile_route = Route("profile/{pid}")
profile_route.factory(get_engine)


@profile_route.post
async def profile(pid: str, q: int, user: Body[User], engine: Engine) -> User:
    return User(id=user.id, name=user.name, email=user.email)


app = Lihil()
app.include_routes(profile_route)

#if __name__ == "__main__":
#    uvicorn.run(app, access_log=None, log_level="warning")
#