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
    assert engine.url == pid and engine.nums == q
    return PdUser(id=user.id, name=user.name, email=user.email)


app = FastAPI()
app.include_router(profile_route)
