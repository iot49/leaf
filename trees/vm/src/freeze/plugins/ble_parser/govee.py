from struct import unpack

from eventbus import post
from eventbus.event import state


async def parser(dev, manufacturer, data):
    if dev.name() is None or manufacturer != 0xEC88:
        return
    _, temp, humi, batt = unpack("<BhHB", data)
    await post(state("dev.temperature", temp / 100))
    await post(state("dev.humidity", humi / 100))
    await post(state("dev.battery_level", batt))
    await post(state("dev.rssi", dev.rssi))
    print(f"Govee T={temp/100}C H={humi/100}% batt={batt}% {dev.rssi}dBm {dev.name()}")
