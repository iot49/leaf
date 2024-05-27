# type: ignore
import asyncio

from app import main
from app.led import BLUE, set_color

# override frozen main (for development)

# standard startup is GREEN
set_color(BLUE)

asyncio.new_event_loop()

TEST_WS = "ws://192.168.8.138:8001/gateway/ws"
TEST_WS = "ws://10.39.40.104:8001/gateway/ws"

asyncio.run(main(ws_url=TEST_WS))  # type: ignore

print("exiting to REPL")
