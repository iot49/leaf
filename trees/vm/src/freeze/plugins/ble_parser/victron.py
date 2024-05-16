async def parser(dev, manufacturer, data):
    if manufacturer != 0x02E1:
        return
    print("Victron", dev.name())
