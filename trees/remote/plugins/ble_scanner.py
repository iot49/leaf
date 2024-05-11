import aioble  # type: ignore


async def init(duration_ms: int = 500, active=True) -> None:
    from .ble_parser import govee, victron

    parsers = [govee.parser, victron.parser]
    while True:
        async with aioble.scan(duration_ms=duration_ms, active=active) as scanner:
            async for dev in scanner:
                for manufacturer, data in dev.manufacturer():
                    for parser in parsers:
                        await parser(dev, manufacturer, data)
