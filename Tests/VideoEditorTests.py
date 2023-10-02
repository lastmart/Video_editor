from VideoEditor.video_editor import \
    (Usage, TimeInterval, Point, open_videos, merge_videos_and_save,
     insert_video_and_save, trim_and_save_video, cut_part_and_save_video,
     set_video_speed_and_save, overlay_video_on_another_and_save, crop_and_save)
from VideoEditor.utils import get_video_duration
from typing import Callable
import unittest
import ffmpeg
import shutil
import tempfile
import os


class TestVideoEditor(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        project_directory = os.path.dirname(current_directory)
        self.video_directory = project_directory + os.sep + 'resources' + os.sep
        self.video_paths = list(map(lambda f: self.video_directory + f, os.listdir(self.video_directory)))

    def test_open_not_file(self):
        self.assertRaises(TypeError, open_videos, 1)

    def test_open_nonexistent_file(self):
        self.assertRaises(IOError, open_videos, 'asdf.mp4')
        self.assertRaises(IOError, open_videos, '/some/incorrect/path/asdf.mp4')
        self.assertRaises(IOError, open_videos, '{}asdf.mp4'.format(self.video_directory))

    def test_open_existing_file(self):
        self.assertIsNotNone(open_videos(self.video_paths))

    def test_merge(self):
        self.base_check_duration_test(
            merge_videos_and_save,
            float(sum(map(lambda x: get_video_duration(x), self.video_paths))),
            self.video_paths
        )

    def test_incorrect_path_merge(self):
        self.base_raise_exception_test(
            merge_videos_and_save,
            IOError,
            self.video_paths + ['1']
        )

    def test_one_video_to_merge(self):
        self.base_raise_exception_test(
            merge_videos_and_save,
            ffmpeg.Error,
            self.video_paths[0]
        )
        self.base_raise_exception_test(
            merge_videos_and_save,
            ValueError,
            [self.video_paths[0]]
        )

    def test_insert(self):
        self.base_check_duration_test(
            insert_video_and_save,
            float(sum(map(lambda x: get_video_duration(x), self.video_paths))),
            self.video_paths[0],
            self.video_paths[1:],
            10
        )

    def test_incorrect_path_insert(self):
        self.base_raise_exception_test(
            insert_video_and_save,
            ffmpeg.Error,
            self.video_paths[0] + '123',
            self.video_paths[1:],
            3
        )
        self.base_raise_exception_test(
            insert_video_and_save,
            AttributeError,
            self.video_paths[0],
            self.video_paths[1:] + [1, 2, 3],
            3
        )

    def test_trim(self):
        start_time = 2
        end_time = 10
        self.base_check_duration_test(
            trim_and_save_video,
            float(end_time - start_time),
            self.video_paths[0],
            TimeInterval(start_time, end_time)
        )

    def test_incorrect_path_trim(self):
        time_interval = TimeInterval(1, 5)
        self.base_raise_exception_test(
            trim_and_save_video,
            ffmpeg.Error,
            '1',
            time_interval
        )

    def test_cut(self):
        time_interval = TimeInterval(1, 5)
        input_video_path = self.video_paths[0]
        intput_video_duration = get_video_duration(input_video_path)
        self.base_check_duration_test(
            cut_part_and_save_video,
            intput_video_duration - time_interval.get_duration_in_seconds(),
            input_video_path,
            TimeInterval(1, 7)
        )

    def test_incorrect_path_cut(self):
        self.base_raise_exception_test(
            cut_part_and_save_video,
            ffmpeg.Error,
            '1',
            TimeInterval(2, 10)
        )

    def test_incorrect_time_cut_interval(self):
        self.base_raise_exception_test(
            cut_part_and_save_video,
            ValueError,
            self.video_paths[0],
            TimeInterval(2, 10000000)
        )

    def test_set_speed(self):
        input_path = self.video_paths[0]
        video_duration = get_video_duration(input_path)
        speed = 3
        self.base_check_duration_test(
            set_video_speed_and_save,
            video_duration * (1 / speed),
            input_path,
            speed
        )

    def test_set_speed_of_interval(self):
        input_path = self.video_paths[0]
        time_interval = TimeInterval(1, 7)
        video_duration = get_video_duration(input_path)
        speed = 3
        expected_duration = (time_interval.begin +
                             time_interval.get_duration_in_seconds() * (1 / speed) +
                             video_duration - time_interval.end)
        self.base_check_duration_test(
            set_video_speed_and_save,
            expected_duration,
            input_path,
            speed,
            time_interval=time_interval
        )

    def test_incorrect_path_to_set_speed(self):
        self.base_raise_exception_test(
            set_video_speed_and_save,
            ffmpeg.Error,
            '1',
            3,
            time_interval=TimeInterval(2, 10)
        )
        self.base_raise_exception_test(
            set_video_speed_and_save,
            ffmpeg.Error,
            '1',
            3
        )

    def test_overlay(self):
        expected_duration = max(
            get_video_duration(self.video_paths[0]),
            get_video_duration(self.video_paths[1])
        )
        self.base_check_duration_test(
            overlay_video_on_another_and_save,
            expected_duration,
            self.video_paths[0],
            self.video_paths[1],
            x_shift=10,
            y_shift=15
        )

    def test_incorrect_path_overlay(self):
        self.base_raise_exception_test(
            overlay_video_on_another_and_save,
            ffmpeg.Error,
            '1',
            self.video_paths[0]
        )
        self.base_raise_exception_test(
            overlay_video_on_another_and_save,
            ffmpeg.Error,
            self.video_paths[0],
            '1'
        )

    def test_incorrect_shifts_in_overlay(self):
        self.base_raise_exception_test(
            overlay_video_on_another_and_save,
            ValueError,
            self.video_paths[1],
            self.video_paths[0],
            x_shift=100000,
            y_shift=15
        )
        self.base_raise_exception_test(
            overlay_video_on_another_and_save,
            ValueError,
            self.video_paths[1],
            self.video_paths[0],
            x_shift=100,
            y_shift=-15
        )

    def test_crop(self):
        input_path = self.video_paths[0]
        self.base_check_duration_test(
            crop_and_save,
            get_video_duration(input_path),
            input_path,
            point1=Point((100, 100)),
            point2=Point((200, 200))
        )

    def test_incorrect_path_to_crop(self):
        self.base_raise_exception_test(
            crop_and_save,
            ffmpeg.Error,
            '1',
            point1=Point((100, 100)),
            point2=Point((200, 200)),
        )

    def test_incorrect_crop_boundary(self):
        self.base_raise_exception_test(
            crop_and_save,
            ValueError,
            self.video_paths[0],
            point1=Point((100000, 100)),
            point2=Point((200, 200))
        )
        self.base_raise_exception_test(
            crop_and_save,
            ValueError,
            self.video_paths[0],
            point1=Point((-10, -100)),
            point2=Point((200, 200))
        )

    def base_raise_exception_test(self, func: Callable, error, *args, **kwargs):
        output_file = self.tmpdir + 'failed_{}.mp4'.format(func.__name__)
        self.assertRaises(
            error,
            func,
            *args,
            **kwargs,
            path_to_save=output_file,
            is_overwrite=True,
            mode=Usage.CONSOLE
        )

    def base_check_duration_test(self, func: Callable, expected_duration: float, *args, **kwargs):
        output_file = self.tmpdir + '{}.mp4'.format(func.__name__)
        func(
            *args,
            **kwargs,
            path_to_save=output_file,
            is_overwrite=True,
            mode=Usage.CONSOLE
        )
        actual_duration = get_video_duration(output_file)
        self.assertAlmostEqual(expected_duration, actual_duration, delta=0.2)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)


if __name__ == "__main__":
    unittest.main()
