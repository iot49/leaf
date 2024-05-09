import asyncio
import json
import time

import aiohttp
import machine  # type: ignore
import ntptime  # type: ignore

from eventbus import event_type
from eventbus.bus import Counter

from . import DOMAIN, get_state, logger, ping, wifi


async def ping_task(ws, interval):
    while True:
        try:
            await ws.send_json(ping)
        except OSError as e:
            print("Ping failed", e)
            break
        await asyncio.sleep(interval)


async def receiver_task(ws):
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            print(f"receiver_task {msg.type}: {msg.data}")
            if msg.data == "close cmd":
                await ws.close()
                break
            else:
                await ws.send_str(msg.data + "/answer")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            logger.error(f"receiver_task: ws returned error {msg}")
            # TODO: reconnect
            machine.reset()


async def main():
    from . import secrets

    async with wifi:
        logger.info(f"Connected to wifi @ {wifi.ip}")
        ntptime.settime()
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))
        logger.info(f"Time set to {t}")

        # connect to earth

        async with aiohttp.ClientSession() as session:
            url = f"wss://{DOMAIN}/gateway/ws"
            gateway_token = secrets["gateway-token"]
            async with session.ws_connect(url) as ws:
                # get auth
                auth_msg = await ws.receive_json()
                logger.debug(f"Authenticated - {auth_msg}")
                if auth_msg["type"] == event_type.GET_AUTH:
                    await ws.send_json({"type": event_type.PUT_AUTH, "token": gateway_token})
                hello_msg = await ws.receive_json()
                if hello_msg["type"] == event_type.HELLO_CONNECTED:
                    logger.info(f"Connected - {hello_msg}")
                    asyncio.create_task(ping_task(ws, hello_msg["param"]["timeout_interval"]))
                    asyncio.create_task(receiver_task(ws))

                    # update secrets
                    async with session.get(
                        f"https://{DOMAIN}/gateway/secrets",
                        headers={"Authorization": f"Bearer {gateway_token}"},
                    ) as response:
                        secrets = await response.json()
                        with open("/secrets.json", "w") as f:
                            json.dump(secrets, f)

                    # update config
                    await ws.send_json(get_state)
                else:
                    print("Connection failed.", hello_msg)
                    return
                await ws.send_json(get_state)

        # plugins
        Counter("counter.count")
