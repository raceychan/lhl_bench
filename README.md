## TLDR

![res](/assets/benchmark.png)

## Context

### Hardware

- CPU:
 AMD Ryzen 9 7950X 16-Core Processor 4.50 GHz

- RAM 
64.0 GB (63.1 GB usable)

- internet ethernet controller i225v

### OS
Ubuntu 20.04.6 LTS
packages

- python == 3.12
- uvloop==0.21.0
- httptools==0.6.4
- uvicorn==0.34.0


- lihil==0.1.3
- fastapi==0.115.8
- litestar>=2.15.1

### Test command

wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua

4 threas, 64 connections

### Test script

```bash
       │ File: scripts/post.lua
───────┼──────────────────────────────────────────────────────
   1   │ -- example HTTP POST script which demonstrates settin
       │ g the
   2   │ -- HTTP method, body, and adding a header
   3   │ 
   4   │ wrk.method = "POST"
   5 ~ │ wrk.body   = '{"id": 1, "name": "user", "email": "use
       │ r@email.com"}'
   6 ~ │ wrk.headers["Content-Type"] = "application/json"
```

### data.py

```python
from msgspec import Struct


class User(Struct):
    id: int
    name: str
    email: str


class Engine:
    def __init__(self, url: str, nums: int):
        self.url = url
        self.nums = nums


def get_engine(pid: str, q: int) -> Engine:
    return Engine(url=pid, nums=q)
```


## Lihil

### source code

```python
from lihil import Lihil, Route
from lihil.interface.marks import Body

from .data import Engine, User, get_engine

profile_route = Route("profile/{pid}")
profile_route.factory(get_engine)


@profile_route.post
async def profile(pid: str, q: int, user: Body[User], engine: Engine) -> User:
    assert engine.url == pid and engine.nums == q
    return User(id=user.id, name=user.name, email=user.email)


app = Lihil()
app.include_routes(profile_route)
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.53ms    9.23ms 174.74ms   99.17%
    Req/Sec     8.92k     0.89k    9.60k    94.70%
  351456 requests in 10.00s, 46.92MB read
Requests/sec:  35135.64
Transfer/sec:      4.69MB
```


## Litestar

### source code

```python
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
    assert engine.url == pid and engine.nums == q
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
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.44ms   13.80ms 229.39ms   98.37%
    Req/Sec     5.59k   755.03    16.83k    97.98%
  220904 requests in 10.08s, 37.29MB read
Requests/sec:  21905.83
Transfer/sec:      3.70MB
```


## FastAPI


### source code

```python
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from pydantic import BaseModel

from .data import Engine, get_engine


class PdUser(BaseModel):
    id: int
    name: str
    email: str


profile_route = APIRouter()


@profile_route.post("/profile/{pid}")
async def profile(
    pid: str, q: int, user: PdUser, engine: Annotated[Engine, Depends(get_engine)]
) -> PdUser:
    return PdUser(id=user.id, name=user.name, email=user.email)


app = FastAPI()
app.include_router(profile_route)
```


### Result

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency    11.42ms    4.19ms 132.01ms   95.22%
    Req/Sec     1.43k   111.81     1.58k    87.47%
  56778 requests in 10.01s, 9.31MB read
Requests/sec:   5672.98
Transfer/sec:      0.93MB
```


## Starlette

### source code

```python
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
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.60ms    9.31ms 172.91ms   98.92%
    Req/Sec     9.00k     0.97k   11.92k    96.48%
  356674 requests in 10.03s, 47.62MB read
Requests/sec:  35560.72
Transfer/sec:      4.75MB
```


## Blacksheep

### source code

```python
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
```

### Result

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     2.30ms    3.02ms  83.39ms   99.55%
    Req/Sec     7.51k   458.55     8.03k    85.93%
  297405 requests in 10.00s, 48.78MB read
Requests/sec:  29732.23
Transfer/sec:      4.88M
```