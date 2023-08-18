from collections.abc import Iterable
from operator import floordiv
from typing import Union
import ffmpeg
import sys
import os


def check_paths_correctness(paths: Union[str, list[str]]) -> None:
    if isinstance(paths, str):
        paths = [paths]
    for e in paths:
        if not os.path.isdir(e.rsplit(os.sep, 1)[0]):
            raise IOError(f'{e} is not valid directory') from e
        if e.rsplit('.', 1)[-1] not in {'mp4', 'jpg'}:
            raise ValueError(f"{e} hasn't mp4 or jpg format")


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


def scale_frame_in_bounds(
        main_video_path: str,
        overlay_path: str,
        x_shift: int = 0,
        y_shift: int = 0
) -> tuple[int, int]:
    main_video_inf = get_information_about_stream(main_video_path, 'video')
    overlay_video_path = get_information_about_stream(overlay_path, 'video')
    main_width, main_height = int(main_video_inf['width']), int(
        main_video_inf['height'])
    overlay_width, overlay_height = int(overlay_video_path['width']), int(
        overlay_video_path['height'])
    if not 0 <= x_shift <= main_width or not 0 <= y_shift <= main_height:
        raise ValueError('Shifts go beyond the frame of the main video')

    overlay_width, overlay_height = try_scale(x_shift, overlay_width,
                                              main_width, overlay_height,
                                              main_height)

    overlay_height, overlay_width = try_scale(y_shift, overlay_height,
                                              main_height, overlay_width,
                                              main_width)
    return overlay_height, overlay_width


def try_scale(
        shift: int,
        base_value: int,
        base_border: int,
        scale_value: int,
        scale_boarder: int
) -> Union[bool, tuple[int, int]]:
    if shift + base_value > base_border:
        scale = (base_border - shift) / base_value
        base_value = base_border - shift
        if scale_value * scale <= scale_boarder:
            scale_value = -1
    return base_value, scale_value


def get_video_duration(file: Union[str, ffmpeg.nodes.Node]) -> float:
    if isinstance(file, ffmpeg.nodes.Node):
        file = file.kwargs['filename']
    try:
        probe = ffmpeg.probe(file)
    except TypeError as e:
        raise TypeError(f'You can not get duration of {type(file)}') from e
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e
    return float(probe['format']['duration'])


def get_information_about_stream(file: Union[str, ffmpeg.nodes.Node],
                                 stream_name: str) -> dict:
    if isinstance(file, ffmpeg.nodes.Node):
        file = file.kwargs['filename']
    try:
        probe = ffmpeg.probe(file)
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e
    video_stream = next(
        (stream for stream in probe['streams'] if
         stream['codec_type'] == stream_name), None
    )
    if video_stream is None:
        raise FileNotFoundError(f'No {stream_name} stream found in\n {file}')
    return video_stream