from enum import Enum
from functools import wraps
from PyQt6.QtCore import QSysInfo
from PyQt6.QtWidgets import QFileDialog


class MessageType(Enum):
    SUCCESS = 1
    ERROR = 2


class OperationType(Enum):
    INCREASE = 1
    DECREASE = 2


class OperationSystem(Enum):
    WINDOWS = 1
    MACOS = 2
    OTHER = 4


os_dict = {
    'windows': OperationSystem.WINDOWS,
    'macos': OperationSystem.MACOS,
}

os_name = QSysInfo.productType()
OS_TYPE = os_dict[os_name] if \
    os_name in os_dict else \
    OperationSystem.OTHER


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


@process_paths(OS_TYPE)
def get_open_file_name(obj):
    user_file_path, _ = QFileDialog.getOpenFileName(obj, filter="(*.mp4)")
    return user_file_path


@process_paths(OS_TYPE)
def get_open_file_names(obj):
    user_file_path, _ = QFileDialog.getOpenFileNames(
        obj, filter="(*.mp4)"
    )
    return user_file_path


@process_paths(OS_TYPE)
def get_save_file_name(obj):
    user_file_path, _ = QFileDialog.getSaveFileName(obj, filter="(*.mp4)")
    return user_file_path


def process_time(time: int) -> tuple:
    hours = int(time / 3600000)
    minutes = int((time / 60000) % 60)
    seconds = int((time / 1000) % 60)

    return hours, minutes, seconds, 0
