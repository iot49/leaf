from .. import event_type, eventbus
from ..event import State


class CurrentState:
    """Keep tack of state values."""

    def __init__(self):
        super().__init__()
        self._state = {}

        @eventbus.on(event_type.STATE)
        def state(eid, value, timestamp, **event):
            print("CurrentState got update", eid, value, timestamp)
            self._state[eid] = (value, timestamp)

        @eventbus.on(event_type.GET_STATE)
        async def get(src, **event):
            """Send current values."""
            dst = src
            print(f"CurrentState get_state -> {dst}", self._state)
            # make copy of keys to protect against co-modification
            for eid in list(self._state.keys()):
                value, ts = self._state[eid]
                state = State(eid, dst=dst)
                print("CurrentState put_state", eid, value, ts)
                await state.update(value, timestamp=ts)

    @property
    def state(self) -> dict:
        """Return current state values.
        Returns:
            dict: Current state values. Do not modify!
        """
        return self._state
