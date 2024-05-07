import asyncio
import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket

from eventbus import post, serve
from eventbus.bus import Counter, CurrentState, Log, configure_logging
from eventbus.bus.printer import Printer
from eventbus.event import get_state, state_action

N = 1000


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(main())
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get():
    return "Hello World"


_CLIENT_ADDR = 1


@app.websocket("/ws")
async def client_ws(websocket: WebSocket):
    global _CLIENT_ADDR
    await websocket.accept()
    _CLIENT_ADDR += 1
    peer = f"@{_CLIENT_ADDR}"

    param = {
        "peer": peer,
        "host": str(websocket.headers.get("host")),
        "gateway": False,
    }

    def addr_filter(dst: str) -> bool:
        return dst in ("#clients", peer)

    async def authenticate(token: str) -> bool:
        # dummy that accepts any token
        param["user"] = f"TODO: email for {token}"
        return True

    # won't return until the connection is closed
    await serve(websocket, addr_filter, authenticate, param)  # type: ignore


async def reset_task():
    for i in range(N):
        await post(state_action(counter1.state, "reset", param=i))
        await asyncio.sleep(10)


configure_logging()
Log()
CurrentState()
Printer()
counter1 = Counter("counter1.up", interval=3, N=N)
counter2 = Counter("counter2.up", interval=5, N=N)

print("Action", json.dumps(state_action(counter1.state, "reset", param=777)))
print("GetState", json.dumps(get_state))


async def main():
    await asyncio.gather(counter1.counter_task(), counter2.counter_task(), reset_task())


if __name__ == "__main__":
    uvicorn.run(app, port=8055, host="0.0.0.0")  # , log_level="trace")
