from VideoEditor.video_editor import \
    merge_videos_and_save, trim_and_save_video, set_video_speed_and_save
from gui.application import run_gui
import argparse
import sys


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Video editor parser")
        self.parser.add_argument(
            "-v", dest="videos", type=str, help="Paths to the video(-s)",
            nargs="+"
        )
        self.parser.add_argument(
            "-o", dest="path_to_save", type=str,
            help="Path to save the result video"
        )
        self._create_subcommand_parsers()

    def _create_subcommand_parsers(self):
        subparsers = self.parser.add_subparsers(required=True,
                                                help="Available commands for video processing")
        merge_parser = subparsers.add_parser("merge", help="Merge videos")
        self._add_arguments_for_merge_parser(merge_parser)
        trim_parser = subparsers.add_parser("trim", help="Trim video")
        self._add_arguments_for_trim_parser(trim_parser)
        clip_speed_parser = subparsers.add_parser("speed",
                                                  help="Set video speed"
                                                  )
        self._add_arguments_for_clip_speed_parser(clip_speed_parser)
        gui_parser = subparsers.add_parser("gui", help="Show GUI")
        self._add_arguments_for_gui_parser(gui_parser)

    def parse_args(self, args=None, namespace=None):
        parsed = self.parser.parse_args(args, namespace)
        if ('gui' not in sys.argv[1:] and
                (parsed.path_to_save is None or parsed.videos is None)):
            raise ValueError('The following arguments are required: -v, -o')
        return parsed

    @staticmethod
    def _add_arguments_for_merge_parser(parser: argparse.ArgumentParser):
        parser.set_defaults(
            func=lambda x: merge_videos_and_save(x.videos, x.path_to_save))

    @staticmethod
    def _add_arguments_for_trim_parser(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-s", dest="start_time", type=str, required=True,
            help="Start time to trim video in format: HH:MM:SS"
        )
        parser.add_argument(
            "-e", dest="end_time", type=str, required=True,
            help="End time to trim video in format: HH:MM:SS"
        )
        parser.set_defaults(
            func=lambda x: trim_and_save_video(x.videos[0], x.start_time,
                                               x.end_time, x.path_to_save))

    @staticmethod
    def _add_arguments_for_clip_speed_parser(parser: argparse.ArgumentParser):
        parser.add_argument("-s", dest="speed", type=float,
                            required=True, help="Speed of video")
        parser.set_defaults(
            func=lambda x: set_video_speed_and_save(x.videos[0], x.speed,
                                                    x.path_to_save))

    @staticmethod
    def _add_arguments_for_gui_parser(parser: argparse.ArgumentParser):
        parser.set_defaults(func=lambda x: run_gui())
