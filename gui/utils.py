from enum import Enum
from functools import wraps


class MessageType(Enum):
    SUCCESS = 1
    ERROR = 2


class OperationType(Enum):
    INCREASE = 1
    DECREASE = 2


class OperationSystem(Enum):
    WINDOWS = 1
    UNIX = 2


def process_paths(system: OperationSystem):
    """
    This is a decorator that takes a list of
    paths or a path and sets the correct slashes
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if system == OperationSystem.WINDOWS:
                if isinstance(result, str):
                    result = result.replace("/", "\\")
                elif isinstance(result, list):
                    for i in range(len(result)):
                        result[i] = result[i].replace("/", "\\")
                else:
                    raise TypeError
            return result

        return wrapper

    return decorator
