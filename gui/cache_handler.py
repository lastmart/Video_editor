import os
from os import getcwd
from pathlib import Path
from utils import OperationType
from video_editor import copy_video


def _get_base_path_to_save() -> Path:
    base_path_to_save = str(
        Path(str(getcwd())) / 'gui' / 'cache'
    )

    '''This happens when the operating system is Windows'''
    if base_path_to_save.count("gui") == 2:
        base_path_to_save = str(
            Path(str(getcwd())) / 'cache'
        )

    return Path(base_path_to_save)


class CacheHandler:
    def __init__(self):
        self.current_index = 0
        self.BASE_PATH_TO_SAVE = _get_base_path_to_save()

    def update_current_index(self, operation: OperationType) -> None:
        if operation == OperationType.Increase:
            self.current_index += 1
        elif operation == OperationType.Decrease:
            self.current_index -= 1

    def get_current_path_to_look(self) -> str:
        current_path = str(
            self.BASE_PATH_TO_SAVE /
            f'temp{self.current_index}.mp4'
        )

        return current_path

    def get_current_path_to_save(self) -> str:
        self.update_current_index(OperationType.Increase)

        return self.get_current_path_to_look()

    def save_from_cache(self, output_path: str) -> None:
        copy_video(
            self.get_current_path_to_look(),
            self.get_current_path_to_save()
        )
        os.rename(
            self.get_current_path_to_look(), output_path
        )
        self.update_current_index(OperationType.Decrease)

    def prepare_cache_folder(self) -> None:
        """If the program was terminated incorrectly, the
        cache may not be empty. This method clears the cache
        in a special way before starting work with it
        """

        index = 1

        while True:
            current_path_to_remove = str(
                self.BASE_PATH_TO_SAVE /
                f'temp{index}.mp4'
            )

            if os.path.exists(current_path_to_remove):
                os.remove(current_path_to_remove)
                index += 1
            else:
                break

    def clear_cache(self) -> None:
        for index in range(1, self.current_index + 1):
            current_path_to_remove = str(
                self.BASE_PATH_TO_SAVE /
                f'temp{index}.mp4'
            )

            if os.path.exists(current_path_to_remove):
                os.remove(current_path_to_remove)
            else:
                raise FileNotFoundError(current_path_to_remove)

        self.current_index = 0
