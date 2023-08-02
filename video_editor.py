from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from typing import Union


def merge_clips(clips: list) -> VideoFileClip:
    for clip in clips:
        if clip is None:
            raise FileNotFoundError

    return concatenate_videoclips(clips)


def trim_clip(
    clip: VideoFileClip,
    start_time: tuple,
    end_time: tuple
) -> VideoFileClip:
    if clip is None:
        raise FileNotFoundError

    start = float(start_time[0] * 60 + start_time[1])
    end = float(end_time[0] * 60 + end_time[1])

    if start > clip.duration or end > clip.duration or start > end:
        raise IOError

    return clip.subclip(start_time, end_time)


def set_clip_speed(clip: VideoFileClip, speed: int) -> VideoFileClip:
    if clip is None:
        raise FileNotFoundError

    return clip.fx(vfx.speedx, speed)


def save_clip(clip: VideoFileClip, output_path: str) -> None:
    if clip is None:
        raise FileNotFoundError

    clip.write_videofile(output_path)


def open_clips(input_paths: Union[list, str]) -> list:
    if isinstance(input_paths, str):
        return VideoFileClip(input_paths)

    elif isinstance(input_paths, list):
        return [VideoFileClip(input_path) for input_path in input_paths]

    raise TypeError
