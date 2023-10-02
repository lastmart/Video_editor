from VideoEditor.video_editor import \
    (merge_videos_and_save, trim_and_save_video, set_video_speed_and_save,
     overlay_video_on_another_and_save, insert_video_and_save,
     cut_part_and_save_video, crop_and_save, TimeInterval)
from VideoEditor.utils import Usage, convert_time_to_seconds
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
        merge_parser = subparsers.add_parser(
            "merge",
            help="Combine videos or insert the first and second videos "
                 "(for this you need to specify the time for insertion)"
        )
        self._add_arguments_for_merge_parser(merge_parser)
        trim_parser = subparsers.add_parser("trim", help="Trim video")
        self._add_arguments_for_trim_parser(trim_parser)
        clip_speed_parser = subparsers.add_parser("speed", help="Set the speed of the video or part of it")
        self._add_arguments_for_set_speed_parser(clip_speed_parser)
        gui_parser = subparsers.add_parser("gui", help="Show GUI")
        self._add_arguments_for_gui_parser(gui_parser)
        overlay_parser = subparsers.add_parser("overlay", help='Overlay one video or image in another video')
        self._add_arguments_for_overlay_parser(overlay_parser)
        crop_parser = subparsers.add_parser('crop', help="Crop video")
        self._add_arguments_for_crop_parser(crop_parser)

    def parse_args(self, args=None, namespace=None):
        parsed = self.parser.parse_args(args, namespace)
        if ('gui' not in sys.argv[1:] and
                (parsed.path_to_save is None or parsed.videos is None)):
            raise ValueError('The following arguments are required: -v, -o')
        return parsed

    @staticmethod
    def _add_arguments_for_merge_parser(parser: argparse.ArgumentParser):
        def select_insert_or_merge(arg):
            if arg.start_time is None:
                merge_videos_and_save(
                    arg.videos,
                    arg.path_to_save,
                    mode=Usage.CONSOLE
                )
            else:
                insert_video_and_save(
                    arg.videos[0],
                    arg.videos[1],
                    convert_time_to_seconds(arg.start_time),
                    arg.path_to_save,
                    mode=Usage.CONSOLE
                )

        parser.add_argument(
            "-s", dest="start_time", type=str, default=None,
            help="Start time to insert first video to second in format: HH:MM:SS (default: video duration)"
        )
        parser.set_defaults(func=select_insert_or_merge)

    @staticmethod
    def _add_arguments_for_trim_parser(parser: argparse.ArgumentParser):
        def select_trim_or_cut(arg):
            func = trim_and_save_video if arg.is_core else cut_part_and_save_video
            func(
                arg.videos[0],
                TimeInterval(convert_time_to_seconds(arg.start_time), convert_time_to_seconds(arg.end_time)),
                arg.path_to_save,
                mode=Usage.CONSOLE
            )

        parser.add_argument(
            "-s", dest="start_time", type=str, required=True,
            help="Start time to trim video in format: HH:MM:SS"
        )
        parser.add_argument(
            "-e", dest="end_time", type=str, required=True,
            help="End time to trim video in format: HH:MM:SS"
        )
        parser.add_argument('--t', dest='is_core', action='store_true',
                            help='Only the middle remains in the specified range')
        parser.add_argument('--c', dest='is_core', action='store_false',
                            help='Everything except the middle remains in the specified range')
        parser.set_defaults(func=select_trim_or_cut, is_core=True)

    @staticmethod
    def _add_arguments_for_set_speed_parser(parser: argparse.ArgumentParser):
        def define_set_interval(arg):
            time_interval = None
            if arg.start_time is not None and arg.end_time is not None:
                time_interval = TimeInterval(
                    convert_time_to_seconds(arg.start_time),
                    convert_time_to_seconds(arg.end_time)
                )

            set_video_speed_and_save(
                arg.videos[0],
                arg.speed,
                arg.path_to_save,
                time_interval=time_interval,
                mode=Usage.CONSOLE)

        parser.add_argument("-speed", dest="speed", type=float,
                            required=True, help="Speed of video")
        parser.add_argument(
            "-s", dest="start_time", type=str,
            default=None, help="Start time to set speed of video in format: HH:MM:SS"
        )
        parser.add_argument(
            "-e", dest="end_time", type=str,
            default=None, help="End time to set speed video in format: HH:MM:SS"
        )
        parser.set_defaults(func=define_set_interval)

    @staticmethod
    def _add_arguments_for_gui_parser(parser: argparse.ArgumentParser):
        parser.set_defaults(func=lambda x: run_gui())

    @staticmethod
    def _add_arguments_for_overlay_parser(parser: argparse.ArgumentParser):
        parser.add_argument('-i', dest="overlay_path", type=str,
                            required=True, help="Path to the video or image you want to overlay on another video")
        parser.add_argument('-shifts', dest="shifts", type=int, nargs=2,
                            required=True, help="x-axis and y-axis offsets of the inserted video or image")
        parser.set_defaults(func=lambda x: overlay_video_on_another_and_save(
            x.videos[0],
            x.overlay_path,
            x.path_to_save,
            x.shifts[0] if x.shifts is not None else None,
            x.shifts[1] if x.shifts is not None else None,
            mode=Usage.CONSOLE
        ))

    @staticmethod
    def _add_arguments_for_crop_parser(parser: argparse.ArgumentParser):
        parser.add_argument('-shifts', dest="shifts", type=int, nargs=2,
                            required=True, help="x-axis and y-axis offsets to the cropped video")
        parser.add_argument("-width", dest="width", type=int, default=None,
                            required=True, help="Width of cropped video")
        parser.add_argument("-height", dest="height", type=int, default=None,
                            required=True, help="Height of cropped video")
        parser.set_defaults(func=lambda x: crop_and_save(
            x.videos[0],
            x.path_to_save,
            x_shift=x.shifts[0] if x.shifts is not None else None,
            y_shift=x.shifts[1] if x.shifts is not None else None,
            width=x.width,
            height=x.height,
            mode=Usage.CONSOLE
        ))
