from PyQt6 import QtWidgets
from PyQt6.QtWidgets import \
    QDialog, QVBoxLayout, QHBoxLayout, QDoubleSpinBox
from PyQt6.QtCore import QTime, QLocale
from .constructor import \
    get_text_label, get_choice_button, \
    get_filename_button, get_speed_edit_widgets, get_time_edit_widgets, \
    get_speed_edit_layout, get_time_edit_layout, get_time_edit_widget
from .utils import process_time, get_open_file_names
from .my_dialog_window import MyDialogWindow


class TrimDialogWindow(MyDialogWindow):
    def __init__(self, current_time: int, text: str):
        super().__init__("trim dialog")

        main_text = get_text_label(
            self, text
        )
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        self.start_edit, self.end_edit = \
            get_time_edit_widgets(self, current_time)

        self._set_up_layouts(main_text, start_text, end_text)

    def _set_up_layouts(
        self,
        main_text,
        start_text,
        end_text,
    ) -> None:
        start_layout = get_time_edit_layout(start_text, self.start_edit)
        end_layout = get_time_edit_layout(end_text, self.end_edit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QTime, QTime]:
        return self.start_edit.time(), self.end_edit.time()


class SetSpeedDialogWindow(MyDialogWindow):
    def __init__(self):
        super().__init__("set speed dialog")

        main_text = get_text_label(
            self, "Set new video speed:"
        )
        self.speed_edit = get_speed_edit_widgets(self)

        self._set_up_layouts(main_text)

    def _set_up_layouts(
        self,
        main_text,
    ):
        speed_edit_layout = get_speed_edit_layout(
            self, main_text, self.speed_edit
        )

        main_layout = QVBoxLayout()
        main_layout.addLayout(speed_edit_layout)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> QTime:
        return self.speed_edit.value()


class SetPartialSpeedDialogWindow(MyDialogWindow):
    def __init__(self, current_time: int):
        super().__init__("set speed dialog")

        time_text = get_text_label(self, "Select video fragment")
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        speed_text = get_text_label(
            self, "Set new speed for fragment:"
        )

        self.start_edit, self.end_edit = \
            get_time_edit_widgets(self, current_time)
        self.speed_edit = get_speed_edit_widgets(self)

        self._set_up_layouts(
            time_text,
            start_text,
            end_text,
            speed_text,
        )

    def _set_up_layouts(
        self,
        time_text,
        start_text,
        end_text,
        speed_text,
    ):
        start_layout = get_time_edit_layout(start_text, self.start_edit)
        end_layout = get_time_edit_layout(end_text, self.end_edit)
        speed_edit_layout = get_speed_edit_layout(
            self, speed_text, self.speed_edit
        )

        main_layout = QVBoxLayout()
        main_layout.addWidget(time_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(speed_text)
        main_layout.addLayout(speed_edit_layout)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QTime, QTime, QTime]:
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


class MergeIntoDialogWindow(MyDialogWindow):
    def __init__(self, current_time: int):
        super().__init__("merge into dialog", have_choice_button=False)
        self.filenames = None

        main_text = get_text_label(
            self, "Select the time at which the merge will be performed"
        )
        self.time_edit = get_time_edit_widget(self, current_time)

        self.filename_button = get_filename_button(
            self,
            self._get_open_filenames_wrapper
        )

        self._set_up_layouts(main_text)

    def _set_up_layouts(self, main_text):
        time_edit_layout = get_time_edit_layout(main_text, self.time_edit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_edit_layout)
        main_layout.addWidget(self.filename_button)

        self.setLayout(main_layout)

    def _get_open_filenames_wrapper(self) -> None:
        self.filenames = get_open_file_names(self)
        self.filename_button.setText("The files were selected")
        self.filename_button.setEnabled(False)
        self.done(1)

    def get_result(self) -> tuple[QTime, list[str]]:
        return self.time_edit.time(), self.filenames


def run_trim_dialog_window(current_time: int, main_text: str) -> list:
    window = TrimDialogWindow(current_time, main_text)
    return window.execute()


def run_merge_into_dialog_window(current_time: int) -> tuple[QTime, list[str]]:
    window = MergeIntoDialogWindow(current_time)
    return window.execute()


def run_set_speed_dialog_window() -> QTime:
    window = SetSpeedDialogWindow()
    return window.execute()


def run_set_partial_speed_dialog_window(current_time: int) -> QTime:
    window = SetPartialSpeedDialogWindow(current_time)
    return window.execute()


def run_ask_confirmation_dialog_window(text: str) -> bool:
    window = AskConfirmationDialogWindow(text)
    window.show()
    return True if window.exec() == QDialog.DialogCode.Accepted else False
