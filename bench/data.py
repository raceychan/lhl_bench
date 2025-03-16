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
