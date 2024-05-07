from test import *  # noqa: F403
from types import ModuleType


def run_all_tests():
    for name, module in globals().items():
        if name.startswith("test_") and isinstance(module, ModuleType):
            print("Testing module", name, "...")
            for k, v in module.__dict__.items():
                if k.startswith("test_") and callable(v):
                    print(f"   {k} ...")
                    v()


run_all_tests()
