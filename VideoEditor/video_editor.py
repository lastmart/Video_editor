from .utils import \
    (check_paths_correctness, scale_frame_in_bounds, get_video_duration,
     get_video_parameters, Usage)
from .progress_bar import \
    show_progress_in_console, show_progress_in_gui
from collections import namedtuple
from PyQt6.QtCore import QTime
from typing import Union
import ffmpeg
import sys


class TimeInterval:
    _begin = None
    _end = None

    def __init__(self, start_time: Union[QTime, int], end_time: Union[QTime, int]):
        try:
            self._end = QTime(0, 0).secsTo(end_time) if isinstance(end_time, QTime) else end_time
            self._begin = QTime(0, 0).secsTo(start_time) if isinstance(start_time, QTime) else start_time
            self._check_interval_correctness()
        except TypeError:
            raise TypeError("In the values of the boundaries of the TimeInterval not PyQt6.QtCore.QTime or int:\n{}"
                            .format((type(start_time), type(end_time))))

    def get_duration_in_seconds(self) -> int:
        return self.end - self.begin

    @property
    def begin(self) -> int:
        return self._begin

    @begin.setter
    def begin(self, value: int):
        if not isinstance(value, int):
            raise TypeError('Begin of TimeInterval should be int, but received {}'
                            .format(type(value)))
        self._begin = value
        self._check_interval_correctness()

    @property
    def end(self) -> int:
        return self._end

    @end.setter
    def end(self, value: int):
        if not isinstance(value, int):
            raise TypeError('End of TimeInterval should be int, but received {}'
                            .format(type(value)))
        self._end = value
        self._check_interval_correctness()

    def in_range(self, value: Union[int, float]):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise TypeError('Range of TimeInterval should be int, but received {}'
                            .format(type(value)))
        return self.end < value

    def _check_interval_correctness(self) -> None:
        if not (0 <= self._begin <= self._end):
            raise ValueError('You specified the wrong time interval:\n'
                             'begin {begin} \nend {end}'
                             .format(begin=self.begin, end=self.end))


FilterableStream = namedtuple("FilterableStream", ['video', "audio"])


def merge_videos_and_save(
        videos_paths: list[str],
        path_to_save: str,
        width: int = None,
        height: int = None,
        sar: str = None,
        fps: int = None,
        is_overwrite: bool = False,
        mode: Usage = Usage.GUI
) -> None:
    """
    Merge multiple videos and save result. If one of the options for the final
    video is not specified, this option is taken from the first video in the
    list
    :param videos_paths: the absolute path to the videos which you want to merge
    :param path_to_save: the absolute path to the result video
    :param width: resulting video width
    :param height: resulting video height
    :param fps: resulting video fps
    :param sar: resulting video  SAR (Storage Aspect Ratio)
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :return: None
    """
    if len(videos_paths) < 2:
        raise ValueError(
            'You can merge only two or more videos, but you got {}'
            .format(len(videos_paths))
        )

    width, height, fps, sar = get_video_parameters(videos_paths[0],
                                                   width, height, fps, sar)
    streams = open_videos(videos_paths)
    merged_video = merge_videos(streams, width, height, fps, sar)
    result_video_duration = sum(map(lambda v: get_video_duration(v), videos_paths))
    save_video(merged_video, path_to_save, is_overwrite=is_overwrite,
               duration=result_video_duration, mode=mode)


def insert_video_and_save(
        main_video_path: str,
        insert_path: str,
        insert_time_in_seconds: int,
        path_to_save: str,
        is_overwrite: bool = False,
        mode: Usage = Usage.GUI
) -> None:
    """
    Insert one video in another and save result. If one of the options for the final
    video is not specified, this option is taken from the main video
    :param main_video_path: absolute path to the video where you want to insert another video
    :param insert_path: absolute path to the video which you want to insert
    :param insert_time_in_seconds: time from the beginning of the main video after which another
     video will be inserted
    :param path_to_save: the absolute path to the result video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :return: None
    """
    main_video_duration = get_video_duration(main_video_path)
    if main_video_duration < insert_time_in_seconds:
        raise ValueError('Time to insert ({}) beyond video duration({})'
                         .format(insert_time_in_seconds, main_video_duration))
    result_video_parts = [
        open_videos(main_video_path, ss=0, t=insert_time_in_seconds),
        open_videos(insert_path),
        open_videos(main_video_path, ss=insert_time_in_seconds)
    ]

    width, height, fps, sar = get_video_parameters(main_video_path)
    result_video_duration = main_video_duration + get_video_duration(insert_path)
    merged = merge_videos(result_video_parts, width, height, fps, sar)
    save_video(merged, path_to_save, is_overwrite, result_video_duration, mode)


def merge_videos(
        videos: list[ffmpeg.Stream],
        width: int = None,
        height: int = None,
        fps: int = None,
        sar: str = None,
        unsafe_mod: bool = False
) -> ffmpeg.nodes.Node:
    """
    Merge multiple videos and return its object representation
    :param videos: video streams to concat
    :param width: resulting video width
    :param height: resulting video height
    :param fps: resulting video fps
    :param sar: resulting video  SAR (Storage Aspect Ratio)
    :param unsafe_mod:
    :return: ffmpeg.nodes.Node
    """
    concat_params = []
    transition_duration = 0.25
    for video in videos:
        if unsafe_mod:
            filtered_video = video.video
        else:
            filtered_video = (
                ffmpeg.filter(video.video, 'scale', h=height, w=width)
                .filter('setsar', sar=sar)
                .filter('fps', fps=fps)
            )
            if video is not videos[0]:
                filtered_video = ffmpeg.filter(filtered_video, 'fade', t="in",
                                               st=transition_duration, d=transition_duration)
            if video is not videos[-1]:
                duration = get_video_duration(video.node)
                filtered_video = ffmpeg.filter(filtered_video, 'fade', t="out",
                                               st=duration - transition_duration, d=transition_duration)

        concat_params.extend((filtered_video, video.audio))
    return ffmpeg.concat(*concat_params, a=1).node


def trim_and_save_video(
        video_path: str,
        time_interval: TimeInterval,
        path_to_save: str,
        is_overwrite: bool = False,
        mode: Usage = Usage.GUI
) -> None:
    """
    Trim the end and beginning of the video and save result
    :param video_path: the absolute path to the video which you want to merge
    :param path_to_save: the absolute path to the result video
    :param time_interval: all time intervals that should be included in the resulting video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :return: None
    """
    video_duration = get_video_duration(video_path)
    if not time_interval.in_range(video_duration):
        raise ValueError('Time to trim ({}) beyond video duration({})'
                         .format(time_interval.end, video_duration))
    stream = open_videos(video_path)
    result_video_duration = time_interval.get_duration_in_seconds()
    save_video(trim_video(stream, time_interval.begin, time_interval.end), path_to_save,
               is_overwrite, result_video_duration, mode=mode)


def cut_part_and_save_video(
        video_path: str,
        time_interval: TimeInterval,
        path_to_save: str,
        is_overwrite: bool = False,
        mode: Usage = Usage.GUI
) -> None:
    """
    Cut part of the video and save result
    :param video_path: the absolute path to the video which you want to merge
    :param path_to_save: the absolute path to the result video
    :param time_interval: all time intervals that should be removed in given video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :return: None
    """
    video_duration = get_video_duration(video_path)
    if not time_interval.in_range(video_duration):
        raise ValueError('Time to cut beyond video duration')
    result_video_duration = video_duration - time_interval.get_duration_in_seconds()
    video_parts_without_middle = [
        open_videos(video_path, ss=0, t=time_interval.begin),
        open_videos(video_path, ss=time_interval.end)
    ]
    save_video(merge_videos(video_parts_without_middle, unsafe_mod=True),
               path_to_save, is_overwrite, result_video_duration, mode)


def trim_video(
        input_video: ffmpeg.Stream,
        start_time: int,
        end_time: int,
) -> ffmpeg.nodes.Node:
    pts = 'PTS-STARTPTS'
    video = (input_video.video
             .filter('trim', start=start_time, end=end_time)
             .filter('setpts', pts))
    audio = (input_video.audio
             .filter('atrim', start=start_time, end=end_time)
             .filter('asetpts', pts))
    return ffmpeg.concat(video, audio, v=1, a=1).node


def set_video_speed_and_save(
        video_path: str,
        speed: Union[int, float, str],
        path_to_save: str,
        is_overwrite: bool = False,
        time_interval: TimeInterval = None,
        mode: Usage = Usage.GUI
) -> None:
    """
    Set speed of video and save result
    :param video_path: the absolute path to the video which you want to merge
    :param path_to_save: the absolute path to the result video
    :param speed: speed of result video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :param time_interval: time interval of the video to which the playback
     speed change will be applied
    :return: None
    """
    speed = round(float(speed), 1) if isinstance(speed, str) else speed
    if speed < 0.5:
        raise ValueError('{} is very small'.format(speed))
    video_duration = get_video_duration(video_path)
    if time_interval is not None and video_duration < time_interval.end:
        raise ValueError('Interval to set speed ({}) beyond video duration({})'
                         .format(time_interval.end, video_duration))
    if time_interval is None:
        changed_speed_video = set_video_speed(open_videos(video_path), speed)
        result_video_duration = video_duration * (1 / speed)
    else:
        video, audio = set_video_speed(
            open_videos(video_path, ss=time_interval.begin, t=time_interval.get_duration_in_seconds()),
            speed,
            raw_format=True
        )
        video_parts_without_middle = [
            open_videos(video_path, ss=0, t=time_interval.begin),
            FilterableStream(video, audio),
            open_videos(video_path, ss=time_interval.end),
        ]
        changed_speed_video = merge_videos(video_parts_without_middle, unsafe_mod=True)
        result_video_duration = (time_interval.begin +
                                 time_interval.get_duration_in_seconds() * (1 / speed) +
                                 video_duration - time_interval.end)
    save_video(changed_speed_video, path_to_save, is_overwrite,
               result_video_duration, mode=mode)


def set_video_speed(
        input_video: ffmpeg.Stream,
        speed: float,
        raw_format: bool = False) \
        -> Union[ffmpeg.nodes.Node, tuple[ffmpeg.nodes.FilterableStream, ffmpeg.nodes.FilterableStream]]:
    video = input_video.video.filter('setpts', '{}*PTS'.format(round(1 / speed, 1)))
    audio = (input_video.audio
             .filter('asetpts', '{}*PTS'.format(round(1 / speed, 1)))
             .filter("atempo", speed))
    return (video, audio) if raw_format else ffmpeg.concat(video, audio, v=1, a=1).node


def overlay_video_on_another_and_save(
        main_video_path: str,
        overlay_path: str,
        path_to_save: str,
        x_shift: int = 0,
        y_shift: int = 0,
        is_overwrite: bool = False,
        mode: Usage = Usage.GUI
) -> None:
    """
    Overlay one video or image in another video and save result
    :param main_video_path: absolute path to the video where you want to insert another video
    :param overlay_path: absolute path to the video or image which you want to overlay
    :param path_to_save: the absolute path to the result video
    :param x_shift: x-axis offset of the inserted video or image
    :param y_shift: x-axis offset of the inserted video or image
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :return: None
    """
    overlay_height, overlay_width = scale_frame_in_bounds(main_video_path,
                                                          overlay_path,
                                                          x_shift, y_shift)
    main_video = open_videos(main_video_path)
    overlay_video = (open_videos(overlay_path, {'mp4', 'png', 'jpg'})
                     .filter('scale', overlay_width, overlay_height))
    overlay_result = (
        main_video
        .overlay(overlay_video, x=x_shift, y=y_shift)
        .concat(main_video.audio, a=1).node
    )
    result_video_duration = max(get_video_duration(main_video_path),
                                get_video_duration(overlay_path))
    save_video(overlay_result, path_to_save, is_overwrite=is_overwrite,
               duration=result_video_duration, mode=mode)


def crop_and_save(
        video_path: str,
        path_to_save: str,
        x_shift: int,
        y_shift: int,
        width: int,
        height: int,
        is_overwrite: bool = False,
        mode: Usage = Usage.GUI
) -> None:
    """
    Crop video and save result
    :param video_path: absolute path to the video which you want crop
    :param path_to_save: the absolute path to the result video
    :param x_shift: x-axis offset of the inserted video or image
    :param y_shift: x-axis offset of the inserted video or image
    :param width: width of cropped video
    :param height: height of cropped video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :param mode: where to display progress: in the console or in the GUI
    :return: None
    """
    stream = open_videos(video_path)
    result_video_duration = get_video_duration(video_path)
    cropped = (ffmpeg
               .crop(stream, x_shift, y_shift, width, height)
               .concat(stream.audio, a=1))
    save_video(cropped, path_to_save, is_overwrite, result_video_duration, mode)


def copy_video(input_path: str, output_path: str, is_overwrite: bool = True) -> None:
    video = open_videos(input_path)
    video_duration = get_video_duration(input_path)
    save_video(video, output_path, duration=video_duration,
               is_overwrite=is_overwrite, mode=Usage.GUI)


def generate_thumbnail(
        in_filename: str,
        out_filename: str,
        time_moment: int,
        width: int
) -> None:
    """
    Allows to get a frame from a video
    :param in_filename: the absolute path to the video where you want the frame
    :param out_filename: the absolute path to the image where you want to save the result (the format is also indicated
    in the path)
    :param time_moment: time in seconds to frame
    :param width: the resulting frame width (the height is proportional to the parameters of the source video)
    :return: None
    """
    try:
        (
            ffmpeg
            .input(in_filename, ss=time_moment)
            .filter('scale', width, -1)
            .output(out_filename, vframes=1)
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e


def save_video(
        video: Union[ffmpeg.Stream, ffmpeg.nodes.Node],
        output_path: str,
        is_overwrite: bool = False,
        duration: float = None,
        mode: Usage = Usage.CONSOLE,
) -> None:
    if not output_path.endswith('.mp4'):
        output_path += '.mp4'
    check_paths_correctness(output_path)

    if isinstance(video, ffmpeg.Stream):
        out = ffmpeg.output(video, output_path)
    elif isinstance(video, ffmpeg.nodes.Node):
        out = ffmpeg.output(video[0], video[1], output_path)
    else:
        raise ValueError(f'{type(video)} can not save')

    if duration is not None:
        view = show_progress_in_console if mode is Usage.CONSOLE \
            else show_progress_in_gui
        with view(duration) as socket_filename:
            (out
             .global_args('-progress', 'unix://{}'.format(socket_filename))
             .run(overwrite_output=is_overwrite, capture_stdout=mode is Usage.GUI,
                  capture_stderr=mode is Usage.GUI)
             )
    else:
        out.run(overwrite_output=is_overwrite)


def open_videos(input_paths: Union[list[str], str],
                possible_formats: set[str] = None,
                **kwargs) -> \
        Union[list[ffmpeg.Stream], ffmpeg.Stream]:
    check_paths_correctness(input_paths, possible_formats)
    if isinstance(input_paths, str):
        return ffmpeg.input(input_paths, **kwargs)
    elif isinstance(input_paths, list):
        return [ffmpeg.input(input_path, **kwargs) for input_path in input_paths]
    raise TypeError('Can not open video with path {}'.format(input_paths))
