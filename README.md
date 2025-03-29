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

### Test Method

1. send a post request with path param, query param, request body to server.
2. server receives these data, parse it as `User` object
3. server make a new `User` object out of the receiving user
4. serialize and return `User` in json.

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

v0.1.12

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
    Latency     1.78ms  393.38us  27.78ms   95.12%
    Req/Sec     9.01k     1.09k   28.05k    96.00%
  358958 requests in 10.08s, 47.93MB read
Requests/sec:  35596.90
Transfer/sec:      4.75MB
```

## Starlette

### source code

```python
import json

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
    user = User(**json.loads(body_bytes))
    return Response(
        json.dumps(User(id=user.id, name=user.name, email=user.email).asdict())
    )


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
    Latency     2.03ms    2.35ms  82.87ms   99.51%
    Req/Sec     8.43k   775.29    15.72k    84.75%
  335468 requests in 10.07s, 46.39MB read
Requests/sec:  33326.02
Transfer/sec:      4.61MB
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
    Latency     2.18ms    1.76ms  70.41ms   98.72%
    Req/Sec     7.67k   429.31    10.47k    86.75%
  305344 requests in 10.03s, 50.09MB read
Requests/sec:  30429.13
Transfer/sec:      4.99MB
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
    Latency     3.31ms    4.59ms 127.83ms   99.15%
    Req/Sec     5.39k   448.61     8.70k    98.00%
  214628 requests in 10.06s, 36.23MB read
Requests/sec:  21329.76
Transfer/sec:      3.60MB
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

fastapi will be faster if we wrap get_engine inside an async function, resulting

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     5.66ms    2.55ms  90.26ms   97.70%
    Req/Sec     2.89k   100.78     3.32k    69.77%
  114082 requests in 10.03s, 18.71MB read
Requests/sec:  11374.63
Transfer/sec:      1.87MB
```

## Robyn

robyn is not an ASGI-compatible web framework.

### source code

```python
import json
from robyn import Request, Robyn, jsonify

from .data import Engine, User, get_engine

app = Robyn(__file__)


@app.post("/profile/:pid")
async def profile_handler(request: Request):
    pid = request.path_params["pid"]
    q = int(request.queries.get("q", "0"))
    engine: Engine = get_engine(pid=pid, q=q)
    assert engine.url == pid and engine.nums == q
    user = User(**json.loads(request.body))
    return jsonify(user.asdict())
```


### Result

```bash
wrk -t4 -c64 'http://localhost:8000/profile/p?q=5' -s scripts/post.lua
Running 10s test @ http://localhost:8000/profile/p?q=5
  4 threads and 64 connections
  Thread Stats   Avg      Stdev     Max   +/- Stdev
    Latency     4.35ms    1.16ms  66.49ms   91.64%
    Req/Sec     3.71k   432.29    10.25k    87.00%
  147681 requests in 10.06s, 20.99MB read
Requests/sec:  14683.41
Transfer/sec:      2.09MB
```