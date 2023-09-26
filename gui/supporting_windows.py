from PyQt6 import QtWidgets
from PyQt6.QtWidgets import \
    QDialog, QVBoxLayout, QHBoxLayout, QDoubleSpinBox
from PyQt6.QtCore import QTime, QLocale
from .constructor import \
    get_text_label, get_choice_button, \
    get_filename_button, get_speed_edit_widgets, get_time_edit_widgets
from .utils import process_time, get_open_file_names


class TrimDialogWindow(QDialog):
    def __init__(self, current_time: int, text: str):
        super().__init__()

        self.setWindowTitle("trim dialog")
        self.setMinimumWidth(250)

        main_text = get_text_label(
            self, text
        )
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        self.start_edit, self.end_edit = \
            get_time_edit_widgets(self, current_time)
        choice_button = get_choice_button(self)

        self._set_up_layouts(choice_button, end_text, main_text, start_text)

    def _set_up_layouts(self, choice_button, end_text, main_text, start_text):
        start_layout = QHBoxLayout()
        start_layout.addWidget(start_text)
        start_layout.addWidget(self.start_edit)

        end_layout = QHBoxLayout()
        end_layout.addWidget(end_text)
        end_layout.addWidget(self.end_edit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)

    def get_fragment_time(self) -> list:
        return [self.start_edit.time(), self.end_edit.time()]


class SetSpeedDialogWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("set speed dialog")
        self.setMinimumWidth(250)

        main_text = get_text_label(
            self, "Set new video speed:"
        )
        postfix_text = get_text_label(self, "X")

        self.speed_edit = get_speed_edit_widgets(self)
        choice_button = get_choice_button(self)

        self._set_up_layouts(
            main_text,
            postfix_text,
            choice_button
        )

    def _set_up_layouts(
        self,
        main_text,
        postfix_text,
        choice_button
    ):
        time_edit_layout = QHBoxLayout()
        time_edit_layout.addWidget(main_text)
        time_edit_layout.addWidget(self.speed_edit)
        time_edit_layout.addWidget(postfix_text)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_edit_layout)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)

    def get_speed(self) -> QTime:
        return self.speed_edit.value()


class SetPartialSpeedDialogWindow(QDialog):
    def __init__(self, current_time: int):
        super().__init__()

        self.setWindowTitle("set speed dialog")
        self.setMinimumWidth(250)

        time_text = get_text_label(self, "Select video fragment")
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        speed_text = get_text_label(
            self, "Set new speed for fragment:"
        )
        postfix_text = get_text_label(self, "X")

        self.start_edit, self.end_edit = \
            get_time_edit_widgets(self, current_time)
        self.speed_edit = get_speed_edit_widgets(self)
        choice_button = get_choice_button(self)

        self._set_up_layouts(
            time_text,
            start_text,
            end_text,
            speed_text,
            postfix_text,
            choice_button
        )

    def _set_up_layouts(
        self,
        time_text,
        start_text,
        end_text,
        speed_text,
        postfix_text,
        choice_button
    ):
        start_layout = QHBoxLayout()
        start_layout.addWidget(start_text)
        start_layout.addWidget(self.start_edit)

        end_layout = QHBoxLayout()
        end_layout.addWidget(end_text)
        end_layout.addWidget(self.end_edit)

        time_edit_layout = QHBoxLayout()
        time_edit_layout.addWidget(speed_text)
        time_edit_layout.addWidget(self.speed_edit)
        time_edit_layout.addWidget(postfix_text)

        main_layout = QVBoxLayout()
        main_layout.addWidget(time_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(speed_text)
        main_layout.addLayout(time_edit_layout)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)

    def get_set_speed_information(self) -> tuple[QTime, QTime, QTime]:
        return self.start_edit.time(), \
               self.end_edit.time(), \
               self.speed_edit.value()


class AskConfirmationDialogWindow(QDialog):
    def __init__(self, text: str):
        super().__init__()

        self.setWindowTitle("ask confirmation dialog")
        self.setMinimumWidth(250)

        main_text = get_text_label(
            self, text
        )
        choice_button = get_choice_button(self)

        self._set_up_layouts(main_text, choice_button)

    def _set_up_layouts(self, main_text, choice_button):
        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)


class MergeIntoDialogWindow(QDialog):
    def __init__(self, current_time: int):
        super().__init__()

        self.setWindowTitle("merge into dialog")
        self.setMinimumWidth(250)
        self.filenames = None

        main_text = get_text_label(
            self, "Select the time at which the merge will be performed"
        )

        self._set_up_time_edit_widgets(current_time)
        choice_button = get_choice_button(self)
        filename_button = get_filename_button(
            self,
            self._get_open_filenames_wrapper
        )

        self._set_up_layouts(choice_button, filename_button, main_text)

    def _set_up_time_edit_widgets(self, current_time):
        self.time_edit = QtWidgets.QTimeEdit(self)
        self.time_edit.setDisplayFormat("mm:ss")
        self.time_edit.setTime(QTime(*process_time(current_time)))

    def _set_up_layouts(self, choice_button, filename_button, main_text):
        time_layout = QHBoxLayout()
        time_layout.addWidget(main_text)
        time_layout.addWidget(self.time_edit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_layout)
        main_layout.addWidget(filename_button)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)

    def _get_open_filenames_wrapper(self) -> None:
        self.filenames = get_open_file_names(self)

    def get_merge_information(self) -> tuple[QTime, list[str]]:
        return self.time_edit.time(), self.filenames


def run_trim_dialog_window(current_time: int, main_text: str) -> list:
    window = TrimDialogWindow(current_time, main_text)
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        return window.get_fragment_time()
    else:
        return None


def run_merge_into_dialog_window(current_time: int) -> tuple[QTime, list[str]]:
    window = MergeIntoDialogWindow(current_time)
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        return window.get_merge_information()
    else:
        return None


def run_set_speed_dialog_window() -> QTime:
    window = SetSpeedDialogWindow()
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        return window.get_speed()
    else:
        return None


def run_set_partial_speed_dialog_window(current_time: int) -> QTime:
    window = SetPartialSpeedDialogWindow(current_time)
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        return window.get_set_speed_information()
    else:
        return None


def run_ask_confirmation_dialog_window(text: str) -> bool:
    window = AskConfirmationDialogWindow(text)
    window.show()
    return True if window.exec() == QDialog.DialogCode.Accepted else False
