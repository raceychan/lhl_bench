from msgspec import Struct


class User(Struct):
    id: int
    name: str
    email: str


class Engine: ...


def get_engine() -> Engine:
    return Engine()