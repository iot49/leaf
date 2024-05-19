import asyncio
import logging

from bsp import LED  # type: ignore
from machine import Pin  # type: ignore
from neopixel import NeoPixel  # type: ignore

"""
On-board LED

Example:
    from features import led
    led.pattern = led.RGB_FAST
    # ...
    led.pattern = led.BLUE_BLINK_SLOW
"""

logger = logging.getLogger(__name__)


class _LED:
    # few colors ...
    OFF = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    # few patterns
    # format: list/tuple of (color, duration_ms)
    LED_OFF = ((OFF, 1000),)

    RED_BLINK_SLOW = ((RED, 150), (OFF, 1500))
    RED_BLINK_FAST = ((RED, 150), (OFF, 150))

    GREEN_BLINK_SLOW = ((GREEN, 150), (OFF, 1500))
    GREEN_BLINK_FAST = ((GREEN, 150), (OFF, 150))

    BLUE_BLINK_SLOW = ((BLUE, 150), (OFF, 1500))
    BLUE_BLINK_FAST = ((BLUE, 150), (OFF, 150))

    RGB_SLOW = ((RED, 1000), (GREEN, 1000), (BLUE, 1000))
    RGB_FAST = ((RED, 150), (GREEN, 150), (BLUE, 150))

    def __init__(self):
        self._np = NeoPixel(Pin(LED), 1)
        self._pattern: tuple = self.RED_BLINK_SLOW

    @property
    def pattern(self):
        return self._pattern

    @pattern.setter
    def pattern(self, value: tuple):
        if not isinstance(value[0], (list, tuple)):
            value = ((value, 1000),)
        self._pattern = value
        asyncio.create_task(self.run())

    async def run(self):
        n = -1
        try:
            while True:
                n = (n + 1) % len(self._pattern)
                color, ms = self._pattern[n]
                self._np[0] = color
                self._np.write()
                await asyncio.sleep_ms(ms)  # type: ignore
        except Exception as e:
            logger.exception(f"{e} n={n} pattern={self._pattern}[{n}] = {self._pattern[n]}")


# create led singleton
led = _LED()

# start blink task
# asyncio.create_task(led.run())
