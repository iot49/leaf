# type: ignore
import asyncio

from app import main, secrets
from app.led import BLUE, set_color

# override frozen main (for development)

# standard startup is GREEN
set_color(BLUE)

asyncio.new_event_loop()


tree_id = secrets.get("tree").get("tree_id")
if tree_id == "dev":
    WS = "ws://10.0.0.76:8001/gateway/ws"
else:
    WS = "wss://leaf49.org/gateway/ws"

asyncio.run(main(WS))

print("exiting to REPL")
