import aiohttp


async def main(url="ws://example.org/ws"):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == "close cmd":
                        await ws.close()
                        break
                    else:
                        await ws.send_str(msg.data + "/answer")
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
