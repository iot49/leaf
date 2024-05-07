"""Trivial subset of pydantic to get EventBus working on MicroPython."""


class BaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def model_dump(self, **kwargs) -> dict:
        # omit None, defaults, and unset values
        return {k: v for k, v in self.__dict__.items() if v is not None}
