from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from typing import Union


def merge_clips(clips: list) -> VideoFileClip:
    return concatenate_videoclips(clips)


def trim_clip(
    clip: VideoFileClip,
    start_time: tuple,
    end_time: tuple
) -> VideoFileClip:
    return clip.subclip(start_time, end_time)


def set_clip_speed(clip: VideoFileClip, speed: int) -> VideoFileClip:
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
