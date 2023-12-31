import os
from os import getcwd
from pathlib import Path
from .utils import OperationType
from VideoEditor.video_editor import copy_video
from .message import raise_cache_error, get_success_clear_cache_message


class CacheHandler:
    def __init__(self):
        self.current_index = 0
        self.BASE_PATH_TO_SAVE = CacheHandler.get_base_path_to_save()
        self.index_from_previous_session = None

    def update_current_index(self, operation: OperationType) -> None:
        if operation == OperationType.INCREASE:
            self.current_index += 1
        elif operation == OperationType.DECREASE:
            self.current_index -= 1

    def get_current_path_to_look(self, additive=0) -> str:
        """
        The 'additive' is an argument that is 1 if the
        method is called from a 'get_current_path_to_save'
        """
        current_path = str(
            self.BASE_PATH_TO_SAVE /
            f'temp{self.current_index + additive}.mp4'
        )

        return current_path

    def get_current_path_to_save(self) -> str:
        return self.get_current_path_to_look(additive=1)

    def save_from_cache(self, output_path: str) -> None:
        try:
            copy_video(
                self.get_current_path_to_look(),
                self.get_current_path_to_save()
            )

            self.update_current_index(OperationType.INCREASE)

            os.rename(
                self.get_current_path_to_look(), output_path
            )
        except (
            FileNotFoundError, PermissionError,
            OSError, FileExistsError, IOError
        ):
            raise IOError
        else:
            self.update_current_index(OperationType.DECREASE)

    def undo(self) -> None:
        if self.current_index == 1 or self.current_index == 0:
            raise FileNotFoundError

        self.update_current_index(OperationType.DECREASE)

    def redo(self) -> None:
        if os.path.exists(self.get_current_path_to_save()):
            self.update_current_index(OperationType.INCREASE)
        else:
            raise FileNotFoundError

    def is_empty(self) -> bool:
        index = 1

        while True:
            current_path = str(
                self.BASE_PATH_TO_SAVE /
                f'temp{index}.mp4'
            )

            if os.path.exists(current_path):
                self.index_from_previous_session = index
                index += 1
            else:
                break

        return self.index_from_previous_session is None

    def restore_history(self) -> None:
        self.current_index = self.index_from_previous_session

    def prepare_cache_folder(self, start_index=1) -> None:
        """If the program was terminated incorrectly, the
        cache may not be empty. This method clears the cache
        in a special way before starting work with it
        """

        index = start_index

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

    def clear_cache(self, end_index: int = None) -> None:
        if end_index is None:
            end_index = self.current_index

        for index in range(1, end_index + 1):
            try:
                self._remove_video(index)
            except IOError as e:
                raise_cache_error(e.__str__())

        self.current_index = 0
        get_success_clear_cache_message()

    def _remove_video(self, index: int) -> None:
        current_path_to_remove = str(
            self.BASE_PATH_TO_SAVE /
            f'temp{index}.mp4'
        )

        if os.path.exists(current_path_to_remove):
            os.remove(current_path_to_remove)
        else:
            raise IOError(current_path_to_remove)

    @staticmethod
    def get_base_path_to_save() -> Path:
        base_path_to_save = str(
            Path(str(getcwd())) / 'gui' / 'cache'
        )

        '''This happens when the operating system is Windows'''
        if base_path_to_save.count("gui") == 2:
            base_path_to_save = str(
                Path(str(getcwd())) / 'cache'
            )

        return Path(base_path_to_save)


cache_handler = CacheHandler()
