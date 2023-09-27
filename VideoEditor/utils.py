from collections.abc import Iterable
from operator import floordiv
from typing import Union
from enum import Enum
import ffmpeg
import sys
import os

Usage = Enum('Usage', ['GUI', 'CONSOLE'])


def check_paths_correctness(paths: Union[str, list[str]],
                            possible_formats=None) -> None:
    if possible_formats is None:
        possible_formats = {'mp4'}
    if isinstance(paths, str):
        paths = [paths]
    for e in paths:
        if not os.path.isdir(e.rsplit(os.sep, 1)[0]):
            raise IOError('{} is not valid directory'.format(e)) from e
        if e.rsplit('.', 1)[-1] not in possible_formats:
            raise ValueError("{} hasn't {} format"
                             .format(e, ", ".join(possible_formats)))


def convert_time_to_seconds(date: Union[Iterable, str]) -> int:
    if isinstance(date, str):
        try:
            sep_date = date.split(':')
            sep_date[-1] = sep_date[-1].split('.')[0]
            date = list(map(int, sep_date))
        except ValueError as e:
            raise TypeError('{} is not in format HH:MM:SS.ms*'.format(date)) from e
    if isinstance(date, Iterable):
        time_in_seconds = 0
        date = list(date)
        power = len(date) - 1
        for number in date:
            if not isinstance(number, int):
                raise TypeError(
                    'Collection over time contains more than just integer numbers')
            time_in_seconds += number * (60 ** power)
            power -= 1
        date = time_in_seconds
    else:
        raise ValueError('{} can not converted to seconds'.format(date))
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
        video_duration = float(probe['format']['duration'])
    except TypeError as e:
        raise TypeError('You can not get duration of {}'.format(type(file))) from e
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e
    except KeyError:
        video_duration = 0
    return video_duration


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
        raise FileNotFoundError('No {} stream found in\n {}'
                                .format(stream_name, file))
    return video_stream


def get_video_parameters(path_to_video: str,
                         width: int = None,
                         height: int = None,
                         sar: str = None,
                         fps: int = None,
                         ) -> tuple[int, int, int, str]:
    video_information = get_information_about_stream(path_to_video, 'video')
    width = video_information['width'] if width is None else width
    height = video_information['height'] if height is None else height
    fps = convert_ratio_to_int(video_information['avg_frame_rate']) if fps is None else fps
    sar = video_information.get('sample_aspect_ratio', '1/1') if sar is None else sar
    return width, height, fps, sar
