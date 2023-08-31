from .utils import \
    (check_paths_correctness, convert_date_to_seconds, convert_ratio_to_int,
     scale_frame_in_bounds, get_video_duration, get_information_about_stream,
     Usage)
from .progress_bar import \
    show_progress_in_console, show_progress_in_gui
from typing import Union
import ffmpeg
import sys


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
            f'You can merge only two or more videos, but you got {len(videos_paths)}'
        )

    first_video_information = get_information_about_stream(
        videos_paths[0],
        'video')
    width = first_video_information['width'] if width is None else width
    height = first_video_information['height'] if height is None else height
    fps = convert_ratio_to_int(
        first_video_information['avg_frame_rate']) if fps is None else fps
    sar = first_video_information.get('sample_aspect_ratio',
                                      '1/1') if sar is None else sar
    merged_video = merge_videos(open_videos(videos_paths), width, height, fps,
                                sar)
    result_video_duration = sum(
        map(lambda v: get_video_duration(v), videos_paths))
    save_video(merged_video, path_to_save, is_overwrite=is_overwrite,
               duration=result_video_duration, mode=mode)


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
    video_information = get_information_about_stream(video_path, 'video')
    stream = ffmpeg.input(video_path)
    start_time = convert_date_to_seconds(start_time)
    end_time = convert_date_to_seconds(end_time)
    if start_time > end_time or start_time < 0 or end_time > float(
            video_information['duration']):
        raise RuntimeError('You specified the wrong cropping borders')
    result_video_duration = start_time - end_time
    save_video(trim_video(stream, start_time, end_time), path_to_save,
               is_overwrite, result_video_duration)


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
        is_overwrite: bool = False,
) -> None:
    """
    Set speed of video and save result
    :param video_path: the absolute path to the video which you want to merge
    :param path_to_save: the absolute path to the result video
    :param speed: speed of result video
    :param is_overwrite: overwrites the video even if there is already a video in the save path
    :return: None
    """
    speed = round(float(speed), 1) if isinstance(speed, str) else speed
    if speed < 0.5:
        raise ValueError(f'{speed} is very small')
    changed_speed_video = set_video_speed(open_videos(video_path), speed)
    print(get_video_duration(video_path))
    print((1 / speed))
    print(get_video_duration(video_path) * (1 / speed))
    result_video_duration = round(get_video_duration(video_path) * (1 / speed),
                                  2)
    save_video(changed_speed_video, path_to_save, is_overwrite,
               result_video_duration)


def set_video_speed(input_video: ffmpeg.Stream, speed: float) -> ffmpeg.Stream:
    video = input_video.video.filter('setpts', f'{1 / speed:0.01}*PTS')
    audio = (input_video.audio
             .filter('asetpts', f'{round(1 / speed, 1)}*PTS')
             .filter("atempo", speed))
    return ffmpeg.concat(video, audio, v=1, a=1).node


def overlay_video_on_another_and_save(
        main_video_path: str,
        overlay_path: str,
        path_to_save: str,
        x_shift: int = 0,
        y_shift: int = 0,
        is_overwrite: bool = False
) -> None:
    overlay_height, overlay_width = scale_frame_in_bounds(main_video_path,
                                                          overlay_path,
                                                          x_shift, y_shift)
    main_video = open_videos(main_video_path)
    overlay_video = open_videos(overlay_path) \
        .filter('scale', overlay_width, overlay_height)
    overlay_result = (
        main_video
        .overlay(overlay_video, x=x_shift, y=y_shift)
        .concat(main_video.audio, a=1).node
    )
    save_video(overlay_result, path_to_save, is_overwrite=is_overwrite)


def copy_video(input_path: str, output_path: str, is_overwrite: bool = True) -> None:
    video = open_videos(input_path)
    duration = get_video_duration(input_path)
    save_video(video, output_path, duration=duration, is_overwrite=is_overwrite)


def generate_thumbnail(
        in_filename: str,
        out_filename: str,
        time: int,
        width: int
) -> None:
    """
    Allows to get a frame from a video
    :param in_filename: the absolute path to the video where you want the frame
    :param out_filename: the absolute path to the image where you want to save the result (the format is also indicated
    in the path)
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
             .run(overwrite_output=is_overwrite, capture_stdout=True,
                  capture_stderr=True)
             )
    else:
        out.run(overwrite_output=is_overwrite)


def open_videos(input_paths: Union[list[str], str]) -> \
        Union[list[ffmpeg.Stream], ffmpeg.Stream]:
    check_paths_correctness(input_paths)
    if isinstance(input_paths, str):
        return ffmpeg.input(input_paths)
    elif isinstance(input_paths, list):
        return [ffmpeg.input(input_path) for input_path in input_paths]
    raise TypeError
