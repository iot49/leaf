import asyncio

import aiohttp

from eventbus import event_type
from eventbus.bus import Counter, Printer
from eventbus.event import bye, get_state, ping


async def ping_task(ws, interval):
    while True:
        try:
            await ws.send_json(ping)
        except OSError as e:
            print("Ping failed", e)
            break
        await asyncio.sleep(interval)


async def bye_task(ws):
    await asyncio.sleep(10)
    print("Bye - closing connection")
    await ws.send_json(bye)
    await ws.close()


async def main(url):
    Counter("counter.count")
    Printer()
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            # get auth
            auth_msg = await ws.receive_json()
            if auth_msg["type"] == event_type.GET_AUTH:
                await ws.send_json({"type": event_type.PUT_AUTH, "token": "123"})
            hello_msg = await ws.receive_json()
            if hello_msg["type"] == event_type.HELLO_CONNECTED:
                print("Connected", hello_msg)
                asyncio.create_task(ping_task(ws, hello_msg["param"]["timeout_interval"]))
                await ws.send_json(get_state)
                asyncio.create_task(bye_task(ws))
            else:
                print("Connection failed.", hello_msg)
                return
            n = 0
            async for msg in ws:
                print("GOT", msg.data)
                n += 1


if __name__ == "__main__":
    asyncio.run(main("ws://localhost:8055/ws"))
