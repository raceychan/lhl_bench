import json
from sanic import Sanic, Request, response

from .data import Engine, User, get_engine

app = Sanic("sanic_bench")


@app.post("/profile/<pid>")
async def profile_handler(request: Request, pid: str):
    q = int(request.args.get("q", "0"))
    engine: Engine = get_engine(pid=pid, q=q)
    assert engine.url == pid and engine.nums == q
    
    user_data = json.loads(request.body)
    user = User(**user_data)
    new_user = User(id=user.id, name=user.name, email=user.email)
    
    return response.json(new_user.asdict())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)