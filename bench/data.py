from msgspec import Struct
from msgspec.structs import asdict


class User(Struct):
    id: int
    name: str
    email: str

    def asdict(self):
        return asdict(self)


class Engine:
    def __init__(self, url: str, nums: int):
        self.url = url
        self.nums = nums


def get_engine(pid: str, q: int) -> Engine:
    return Engine(url=pid, nums=q)
