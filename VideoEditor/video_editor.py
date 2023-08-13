from utils import \
    check_paths_correctness, convert_date_to_seconds, convert_ratio_to_int
from typing import Union
import ffmpeg
import sys


def merge_and_save_videos(
        videos_paths: list[str],
        path_to_save: str,
        width: int = None,
        height: int = None,
        sar: str = None,
        fps: int = None,
        is_overwrite: bool = False
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
    :return: None
    """
    if len(videos_paths) < 2:
        raise ValueError(
            f'You can merge only two or more videos, but you got {len(videos_paths)}'
        )

    first_video_information = get_information_about_video(videos_paths[0],
                                                          'video')
    width = first_video_information['width'] if width is None else width
    height = first_video_information['height'] if height is None else height
    fps = convert_ratio_to_int(
        first_video_information['avg_frame_rate']) if fps is None else fps
    sar = first_video_information[
        'sample_aspect_ratio'] if sar is None else sar
    save_video(
        merge_videos(open_videos(videos_paths), width, height, fps, sar),
        path_to_save, is_overwrite
    )


def merge_videos(
        videos: list[ffmpeg.Stream],
        width: int,
        height: int,
        fps: int,
        sar: str
) -> ffmpeg.nodes.Node:
    concat_params = []
    for video in videos:
        filtered_video = (
            ffmpeg.filter(video.video, 'scale', h=height, w=width)
            .filter('setsar', sar=sar)
            .filter('fps', fps=fps))
        concat_params.extend((filtered_video, video.audio))
    return ffmpeg.concat(*concat_params, a=1).node


def trim_and_save_video(
        video_path: str,
        start_time: Union[tuple, str],
        end_time: Union[tuple, str],
        path_to_save: str,
        is_overwrite: bool = False
) -> None:
    """
    Trim video and save result
    :param video_path: the absolute path to the video which you want to merge
    :param path_to_save: the absolute path to the result video
    :param start_time: left border to trim
    :param end_time: right border to trim
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :return: None
    """
    video_information = get_information_about_video(video_path, 'video')
    stream = ffmpeg.input(video_path)
    start_time = convert_date_to_seconds(start_time)
    end_time = convert_date_to_seconds(end_time)
    if start_time > end_time or start_time < 0 or end_time > float(
            video_information['duration']):
        raise RuntimeError('You specified the wrong cropping borders')
    save_video(trim_video(stream, start_time, end_time), path_to_save,
               is_overwrite)


def trim_video(
        input_video: ffmpeg.Stream,
        start_time: int,
        end_time: int,
) -> ffmpeg.Stream:
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
        is_overwrite: bool = False
) -> None:
    """
    Set speed of video and save result
    :param video_path: the absolute path to the video which you want to merge
    :param path_to_save: the absolute path to the result video
    :param speed: speed of result video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :return: None
    """
    speed = float(speed) if isinstance(speed, str) else speed
    speed = round(speed, 1)
    if speed < 1e-5:
        raise ZeroDivisionError('Speed of video can not be zero')
    stream = ffmpeg.input(video_path)
    save_video(set_video_speed(stream, speed), path_to_save, is_overwrite)


def set_video_speed(input_video: ffmpeg.Stream, speed: float) -> ffmpeg.Stream:
    video = input_video.video.filter('setpts', f'{1 / speed:0.01}*PTS')
    audio = (input_video.audio
             .filter('asetpts', f'{round(1 / speed, 1)}*PTS')
             .filter("atempo", speed))
    return ffmpeg.concat(video, audio, v=1, a=1).node


def save_video(
        video: Union[ffmpeg.Stream, ffmpeg.nodes.Node],
        output_path: str,
        is_overwrite: bool = False
) -> None:
    if not output_path.endswith('.mp4'):
        output_path += '.mp4'
    check_paths_correctness(output_path)
    if isinstance(video, ffmpeg.Stream):
        out = ffmpeg.output(video.video, video.audio, output_path,
                            format='mp4')
    elif isinstance(video, ffmpeg.nodes.Node):
        out = ffmpeg.output(video[0], video[1], output_path, format='mp4')
    else:
        raise ValueError('')
    out.run(overwrite_output=is_overwrite)


def open_videos(input_paths: Union[list, str]) -> \
        Union[list[ffmpeg.Stream], ffmpeg.Stream]:
    check_paths_correctness(input_paths)
    if isinstance(input_paths, str):
        return ffmpeg.input(input_paths)
    elif isinstance(input_paths, list):
        return [ffmpeg.input(input_path) for input_path in input_paths]
    raise TypeError


def copy_video(input_path: str, output_path: str,
               is_overwrite: bool = True) -> None:
    video = open_videos(input_path)
    save_video(video, output_path, is_overwrite)


def get_information_about_video(file: Union[str, ffmpeg.nodes.Node],
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
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        raise e
