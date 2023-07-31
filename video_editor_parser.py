from video_editor import *
import re
import argparse


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Video editor parser")
        self.parser.add_argument(
            "-v", dest="clips", type=str, help="Paths to the video(-s)",
            nargs="+", required=True
        )
        self.parser.add_argument(
            "-o", dest="path_to_save", type=str, required=True,
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

    def parse_args(self, args=None, namespace=None):
        return self.parser.parse_args(args, namespace)

    @staticmethod
    def _add_arguments_for_merge_parser(parser):
        parser.set_defaults(
            func=lambda x: save_clip(merge_clips(open_clips(x.clips)),
                                     x.path_to_save))

    @staticmethod
    def _add_arguments_for_trim_parser(parser):
        parser.add_argument(
            "-s", dest="start_time", type=str,
            help="Start time to trim video in format: HH:MM:SS"
        )
        parser.add_argument(
            "-e", dest="end_time", type=str,
            help="End time to trim video in format: HH:MM:SS"
        )
        parser.set_defaults(
            func=lambda x: save_clip(
                trim_clip(open_clips(x.clips)[0], x.start_time, x.end_time),
                x.path_to_save))

    @staticmethod
    def _add_arguments_for_clip_speed_parser(parser):
        parser.add_argument("-s", dest="speed", type=int,
                            help="Speed of video")
        parser.set_defaults(
            func=lambda x: save_clip(
                set_clip_speed(open_clips(x.clips)[0], x.speed),
                x.path_to_save))
