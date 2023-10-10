from enum import Enum
from typing import Union
from functools import wraps
from PyQt6.QtCore import QSysInfo, QTime
from PyQt6.QtWidgets import QFileDialog
from VideoEditor.video_editor import TimeInterval


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
def get_open_file_names(obj, available_filters="(*.mp4)"):
    user_file_path, _ = QFileDialog.getOpenFileNames(
        obj, filter=available_filters
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


def process_fragment_time(fragment_time: tuple[QTime, QTime]) -> TimeInterval:
    start, end = fragment_time
    return TimeInterval(start, end)


def process_Qtime(time: QTime) -> int:
    return time.hour() + time.minute() + time.second()


def process_args_for_merge(
    user_data: list, current_path: str, save_path: str
) -> list:
    if isinstance(user_data[0], QTime):  # merge into
        args_for_merge = [
            current_path, user_data[1], process_Qtime(user_data[0])
        ]
    else:  # merge with
        args_for_merge = [current_path]
        args_for_merge.extend(user_data)
        args_for_merge = [args_for_merge]
    args_for_merge.append(save_path)

    return args_for_merge


def process_args_for_set_speed(
    user_args: Union[float, list]
) -> tuple[float, TimeInterval]:
    if isinstance(user_args, float):
        speed = user_args
        interval = None
    else:
        speed = user_args[2]
        interval = process_fragment_time(user_args[0:-1])

    return speed, interval
