import json
from typing import Any

from .. import event_type, eventbus
from ..event import put_config


class Config:
    """Configuration."""

    def __init__(self, config_file: str):
        super().__init__()
        config = {}
        try:
            with open(config_file) as f:
                config = json.load(f)
        except OSError:
            pass
        self._config_file = config_file
        self._config = config

        @eventbus.on(event_type.GET_CONFIG)
        async def get(src, **event):
            await eventbus.emit(put_config(data=self._config, dst=src))

        @eventbus.on(event_type.PUT_CONFIG)
        def put(data, **event):
            self._config = data
            try:
                import micropython  # type: ignore  # noqa: F401

                with open(self._config_file, "w") as f:
                    json.dump(self._config, f)
            except ImportError:
                # for earth, update_config writes config.json
                pass

    def get(self, path=None, default=None) -> Any:
        """Get configuration value.

        Examples:
            config.get("version")
            config.get("wifi")
        """
        if not path:
            return self._config
        path = path.split("/")
        res = self._config
        try:
            for p in path:
                res = res[p]
        except (KeyError, AttributeError):
            return default
        return res
