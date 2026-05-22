from typing import Callable, ParamSpec, TypeVar

from config.themes import MESSAGES

from ..logger import logger

P = ParamSpec("P")
R = TypeVar("R")


def log_call(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwds: P.kwargs) -> R:
        logger.info(MESSAGES.action_start.format(function_name=fn.__name__))
        return fn(*args, **kwds)

    return wrapper
