from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from .data import Engine, get_engine


async def dump_wrapper(pid: str, q: int):
    return get_engine(pid, q)


class PdUser(BaseModel):
    id: int
    name: str
    email: str


profile_route = APIRouter()
ping_route = APIRouter()


@profile_route.post("/profile/{pid}")
async def profile(
    pid: str, q: int, user: PdUser, engine: Annotated[Engine, Depends(dump_wrapper)]
) -> PdUser:
    assert engine.url == pid and engine.nums == q
    return PdUser(id=user.id, name=user.name, email=user.email)


@ping_route.get("/ping")
async def ping():
    return PlainTextResponse("pong")


app = FastAPI()
app.include_router(profile_route)
app.include_router(ping_route)
