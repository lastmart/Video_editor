from typing import Union
from pathlib import Path
import ffmpeg
import sys
from operator import floordiv


def merge_and_save_videos(
    videos_paths: list[str], path_to_save: str,
    width: int = None, height: int = None,
    fps: int = None
) -> None:
    """
    Merge video, and if one of the parameters is not specified: height, width or fps -
    this parameter is taken from the first video in the list
    """
    if len(videos_paths) < 2:
        raise ValueError(
            f'You can merge only two or more videos, but you got {len(videos_paths)}'
        )
    if width is None or height is None:
        first_video_information = get_information_about_video(
            videos_paths[0],
            'video'
        )
        width = first_video_information['width']
        height = first_video_information['height']
        fps = first_video_information["avg_frame_rate"]
        fps = floordiv(*map(int, fps.split('/')))
    save_video(
        merge_videos(open_videos(videos_paths), width, height, fps),
        path_to_save
    )


def merge_videos(
    videos: list[ffmpeg.Stream], width: int,
    height: int, fps: int
) -> ffmpeg.nodes.Node:
    concat_params = []
    for video in videos:
        scaled_video = (ffmpeg
                        .filter(video.video, 'scale', h=height, w=width)
                        .filter('setsar', sar="1/1")
                        .filter('fps', fps=fps))
        concat_params.extend((scaled_video, video.audio))
    return ffmpeg.concat(*concat_params, a=1).node


def trim_and_save_video(
    video_path: str,
    start_time: Union[tuple, str],
    end_time: Union[tuple, str],
    path_to_save: str
) -> None:
    video_information = get_information_about_video(video_path, 'video')
    stream = ffmpeg.input(video_path)
    start_time = _convert_data_to_seconds(start_time)
    end_time = _convert_data_to_seconds(end_time)
    if start_time > end_time or start_time < 0 or end_time > float(video_information['duration']):
        raise RuntimeError('You specified the wrong cropping borders')
    save_video(trim_video(stream, start_time, end_time), path_to_save)


def trim_video(
    input_video: ffmpeg.Stream,
    start_time: int,
    end_time: int
) -> ffmpeg.Stream:
    pts = 'PTS-STARTPTS'
    video = (input_video.video
             .filter('trim', start=start_time, end=end_time)
             .filter('setpts', pts))
    audio = (input_video.audio
             .filter('atrim', start=start_time, end=end_time)
             .filter('asetpts', pts))
    return ffmpeg.concat(video, audio, v=1, a=1).node


def _convert_data_to_seconds(time: Union[tuple, list, str]):
    if isinstance(time, str):
        try:
            time = list(map(int, time.split(':')))
        except ValueError:
            raise
    if isinstance(time, Union[tuple, list]):
        time_in_seconds = 0
        for i in range(len(time)):
            time_in_seconds += time[i] * (60 ** (len(time) - i - 1))
        time = time_in_seconds
    else:
        raise ValueError
    return time


def set_video_speed_and_save(
    video_path: str,
    speed: Union[int, float, str],
    path_to_save: str
) -> None:
    speed = float(speed) if isinstance(speed, str) else speed
    speed = round(speed, 1)
    if speed < 1e-5:
        raise ZeroDivisionError
    stream = ffmpeg.input(video_path)
    save_video(set_video_speed(stream, speed), path_to_save)


def set_video_speed(input_video: ffmpeg.Stream, speed: int) -> ffmpeg.Stream:
    video = input_video.video.filter('setpts', f'{round(1 / speed, 1)}*PTS')
    audio = (input_video.audio
             .filter('asetpts', f'{round(1 / speed, 1)}*PTS')
             .filter("atempo", speed))
    return ffmpeg.concat(video, audio, v=1, a=1).node


def save_video(
    video: Union[ffmpeg.Stream, ffmpeg.nodes.Node],
    output_path: str, overwrite: bool = False
) -> None:
    check_paths_correctness(output_path)
    if isinstance(video, ffmpeg.Stream):
        out = ffmpeg.output(
            video.video, video.audio, output_path,
            format='mp4'
        )
    elif isinstance(video, ffmpeg.nodes.Node):
        out = ffmpeg.output(video[0], video[1], output_path, format='mp4')
    else:
        raise ValueError('')
    if overwrite:
        out.overwrite_output()
    out.run()


def open_videos(input_paths: Union[list, str]) -> Union[
    list[ffmpeg.Stream], ffmpeg.Stream]:
    check_paths_correctness(input_paths)
    if isinstance(input_paths, str):
        return ffmpeg.input(input_paths)
    elif isinstance(input_paths, list):
        return [ffmpeg.input(input_path) for input_path in input_paths]
    raise TypeError


def check_paths_correctness(paths: Union[str, list[str]]) -> None:
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        try:
            Path(path).resolve()
        except (FileNotFoundError, RuntimeError) as e:
            raise IOError(path) from e
        if path.rsplit('.', 1)[-1] != 'mp4':
            raise ValueError(f"{path} hasn't mp4 format")


def copy_video(input_path: str, output_path: str):
    video = open_videos(input_path)
    save_video(video, output_path, True)


def get_information_about_video(file: str, stream_name: str) -> dict:
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
        raise FileNotFoundError(f'No video stream found in\n {file}')
    return video_stream


def generate_thumbnail(
    in_filename: str, out_filename: str, time: int,
    width: int
) -> None:
    """
    Allows to get a frame from a video
    :param in_filename: the absolute path to the video where you want the frame
    :param out_filename: the absolute path to the image where you want to save the result (the format is also indicated in the path)
    :param time: time in seconds to frame
    :param width: the resulting frame width (the height is proportional to the parameters of the source video)
    :return: None
    """
    try:
        (
            ffmpeg
            .input(in_filename, ss=time)
            .filter('scale', width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)
