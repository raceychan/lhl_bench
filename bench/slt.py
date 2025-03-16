from msgspec.json import decode, encode
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .data import User


# The route handler
async def profile_handler(request: Request):
    # Extract path parameter
    pid = request.path_params["pid"]
    q = int(request.query_params.get("q", "0"))
    body_bytes = await request.body()
    user = User(**decode(body_bytes))
    return Response(encode(User(id=user.id, name=user.name, email=user.email)))


# Create routes
routes = [
    Route("/profile/{pid}", profile_handler, methods=["POST"]),
]

# Create the app
app = Starlette(routes=routes)
