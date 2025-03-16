
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
    Latency     2.28ms    6.91ms 165.67ms   99.10%
    Req/Sec     9.18k   818.49    10.06k    95.47%
  362755 requests in 10.01s, 48.43MB read
Requests/sec:  36239.05
Transfer/sec:      4.84MB
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
    Latency     3.04ms    4.21ms 101.24ms   99.33%
    Req/Sec     5.81k   346.53     6.40k    92.71%
  230278 requests in 10.01s, 38.87MB read
Requests/sec:  23013.11
Transfer/sec:      3.88MB
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
    Latency    11.06ms   10.18ms 210.40ms   98.60%
    Req/Sec     1.58k   134.55     1.72k    94.16%
  62477 requests in 10.01s, 10.25MB read
Requests/sec:   6242.67
Transfer/sec:      1.02MB
```