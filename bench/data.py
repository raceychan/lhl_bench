from msgspec import Struct
from pydantic import BaseModel


class User(Struct):
    id: int
    name: str
    email: str





class Engine: ...


def get_engine() -> Engine:
    return Engine()
