from .. import event_type, eventbus
from ..event import State


class CurrentState:
    """Keep tack of state values."""

    def __init__(self):
        super().__init__()
        self._state = {}

        @eventbus.on(event_type.STATE)
        def state(eid, value, timestamp, **event):
            self._state[eid] = (value, timestamp)

        @eventbus.on(event_type.GET_STATE)
        async def get(src, **event):
            """Send current values."""
            dst = src
            # make copy of keys to protect against co-modification
            for eid in list(self._state.keys()):
                value, ts = self._state[eid]
                state = State(eid, dst=dst)
                await state.update(value, timestamp=ts)

    @property
    def state(self) -> dict:
        """Return current state values.
        Returns:
            dict: Current state values. Do not modify!
        """
        return self._state
