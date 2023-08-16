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


def convert_date_to_seconds(date: Union[Iterable, str]) -> int:
    if isinstance(date, str):
        try:
            sep_date = date.split(':')
            sep_date[-1] = sep_date[-1].split('.')[0]
            date = list(map(int, sep_date))
        except ValueError as e:
            raise TypeError(f'{date} is not in format HH:MM:SS.ms*') from e
    if isinstance(date, Iterable):
        time_in_seconds = 0
        date = list(date)
        power = len(date) - 1
        for number in date:
            if not isinstance(number, int):
                raise TypeError(
                    f'Collection over time contains more than just integer numbers')
            time_in_seconds += number * (60 ** power)
            power -= 1
        date = time_in_seconds
    else:
        raise ValueError(f'{date} can not converted to seconds')
    return date


def convert_ratio_to_int(ratio: str):
    return floordiv(*map(int, ratio.split('/')))
