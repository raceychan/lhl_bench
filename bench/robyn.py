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


@app.get("/ping")
async def ping():
    return "pong"


app.start(port=8000)
