from typing import Union
from pathlib import Path
import ffmpeg


def merge_and_save_videos(videos_paths: list[str], path_to_save: str,
                          width: int = None, height: int = None) -> None:
    if len(videos_paths) < 2:
        raise ValueError(
            f'You can merge only two or more videos, but you got {len(videos_paths)}')
    if width is None or height is None:
        stream_parameters = ffmpeg.probe(videos_paths[0])['streams']
        width = stream_parameters[0].get('width',
                                         stream_parameters[1].get('width'))
        height = stream_parameters[0].get('height',
                                          stream_parameters[1].get('height'))
    save_video(merge_videos(open_videos(videos_paths), width, height),
               path_to_save)


def merge_videos(videos: list[ffmpeg.Stream], width: int,
                 height: int) -> ffmpeg.nodes.Node:
    concat_params = []
    for video in videos:
        scaled_video = (ffmpeg
                        .filter(video.video, 'scale', h=height, w=width)
                        .filter('setsar', sar="1/1"))
        concat_params.extend((scaled_video, video.audio))
    return ffmpeg.concat(*concat_params, a=1).node


def trim_and_save_video(video_path: str,
                        start_time: Union[tuple, str],
                        end_time: Union[tuple, str],
                        path_to_save: str) -> None:
    stream = ffmpeg.input(video_path)
    start_time = _convert_data_to_seconds(start_time)
    end_time = _convert_data_to_seconds(end_time)
    save_video(trim_video(stream, start_time, end_time), path_to_save)


def trim_video(input_video: ffmpeg.Stream,
               start_time: int,
               end_time: int) -> ffmpeg.Stream:
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
        time = list(map(int, time.split(':')))
    if isinstance(time, Union[tuple, list]):
        time_in_seconds = 0
        for i in range(len(time)):
            time_in_seconds += time[i] * (60 ** (len(time) - i - 1))
        time = time_in_seconds
    else:
        raise ValueError
    return time


def set_video_speed_and_save(video_path: str,
                             speed: Union[int, float, str],
                             path_to_save: str) -> None:
    speed = int(speed) if isinstance(speed, str) else speed
    speed = round(speed, 1)
    stream = ffmpeg.input(video_path)
    save_video(set_video_speed(stream, speed), path_to_save)


def set_video_speed(input_video: ffmpeg.Stream, speed: int) -> ffmpeg.Stream:
    video = input_video.video.filter('setpts', f'{round(1 / speed, 1)}*PTS')
    audio = (input_video.audio
             .filter('asetpts', f'{round(1 / speed, 1)}*PTS')
             .filter("atempo", speed))
    return ffmpeg.concat(video, audio, v=1, a=1).node


def save_video(video: Union[ffmpeg.Stream, ffmpeg.nodes.Node],
               output_path: str) -> None:
    if not is_paths_correct(output_path):
        raise ValueError
    if isinstance(video, ffmpeg.Stream):
        out = ffmpeg.output(video.video, video.audio, output_path,
                            format='mp4')
    elif isinstance(video, ffmpeg.nodes.Node):
        out = ffmpeg.output(video[0], video[1], output_path, format='mp4')
    else:
        raise ValueError('')
    out.run()


def open_videos(input_paths: Union[list, str]) -> Union[
    list[ffmpeg.Stream], ffmpeg.Stream]:
    if not is_paths_correct(input_paths):
        raise ValueError
    if isinstance(input_paths, str):
        return ffmpeg.input(input_paths)
    elif isinstance(input_paths, list):
        return [ffmpeg.input(input_path) for input_path in input_paths]
    raise TypeError


def is_paths_correct(paths: Union[str, list[str]]) -> bool:
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        try:
            Path(path).resolve()
        except (FileNotFoundError, RuntimeError):
            return False
    return True


# if __name__ == '__main__':
    # in1: ffmpeg.Stream = ffmpeg.input(
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/ASCII_ART/document_5231008315256878506.mp4")
    # video = ffmpeg.filter(in1.video, 'scale', h=720, w=1280)  #.filter('setsar', sar="1/1")
    # out = ffmpeg.output(video, in1.audio, r"/mnt/c/Users/egore/OneDrive/Документы/sampleCorrectSizeWithout.mp4")
    # out.run()
    # in2 = ffmpeg.input(
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4")
    # merge_and_save_videos([
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/fugu_eat_carrot.mp4",
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4",
    # ],
    #     r"/mnt/c/Users/egore/OneDrive/Документы/12update.mp4"
    # )
    # print('\n' * 5)


    # merge_and_save_videos([
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/fugu_eat_carrot.mp4",
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4",
    # ],
    #     r"/mnt/c/Users/egore/OneDrive/Документы/2.mp4",
    #     width=1280, height=720
    # )

    # video = in1.video.filter('setpts', '0.5*PTS')
    # audio = in1.audio.filter('asetpts', '0.5*PTS').filter("atempo", 2)
    # save_video(ffmpeg.concat(video, audio, v=1, a=1).node,
    #            r"/mnt/c/Users/egore/OneDrive/Документы/good.mp4")

    # a = ffmpeg.probe(r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4")
    # print(a['streams'][0]['width'])
    # print(a['streams'][0]['height'])
    # v1 = ffmpeg.filter(in1.video, 'scale', h=720, w=1280).filter('setsar',
    #                                                              sar="1/1")
    # save_video(ffmpeg.concat(v1, in1.audio, in2.video, in2.audio, a=1).node,
    #            r"/mnt/c/Users/egore/OneDrive/Документы/excellent1.mp4")


    # merge_and_save_videos([
    #     r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/ASCII_ART/document_5231008315256878506.mp4",
    #     r"/mnt/c/Users/egore/OneDrive/Документы/1.mp4"],
    #     r"/mnt/c/Users/egore/OneDrive/Документы/well.mp4")



    # trim_and_save_video(r"/mnt/c/Users/egore/OneDrive/Документы/sampleCorrectSizeWithout.mp4", '01:00', '02:00', r"/mnt/c/Users/egore/OneDrive/Документы/well.mp4")

    # set_video_speed_and_save(r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4", 0.5, r"/mnt/c/Users/egore/OneDrive/Документы/3.mp4")