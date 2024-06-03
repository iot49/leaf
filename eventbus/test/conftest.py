import pytest

from eventbus import eventbus


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


pytest.fixture(scope="session", autouse=True)


def clear_event_handlers():
    eventbus.clear()
