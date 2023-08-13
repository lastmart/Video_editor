from collections.abc import Iterable
from operator import floordiv
from typing import Union
import os


def check_paths_correctness(paths: Union[str, list[str]]) -> None:
    if isinstance(paths, str):
        paths = [paths]
    for e in paths:
        if not os.path.isdir(e.rsplit(os.sep, 1)[0]):
            raise IOError(f'{e} is not valid directory') from e
        if e.rsplit('.', 1)[-1] != 'mp4':
            raise ValueError(f"{e} hasn't mp4 format")


def convert_date_to_seconds(time: Union[Iterable, str]) -> int:
    if isinstance(time, str):
        try:
            time = list(map(int, time.split(':')))
        except ValueError as e:
            raise TypeError(f'{time} is not in format HH:MM:SS') from e
    if isinstance(time, Iterable):
        time_in_seconds = 0
        time = list(time)
        power = len(time) - 1
        for number in time:
            if not isinstance(number, int):
                raise TypeError(
                    f'Collection over time contains more than just numbers')
            time_in_seconds += number * (60 ** power)
            power -= 1
        time = time_in_seconds
    else:
        raise ValueError(f'{time} can not converted to seconds')
    return time


def convert_ratio_to_int(ratio: str):
    return floordiv(*map(int, ratio.split('/')))
