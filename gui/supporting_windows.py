from PyQt6 import QtWidgets
from PyQt6.QtWidgets import \
    QDialog, QVBoxLayout, QHBoxLayout, QDoubleSpinBox
from PyQt6.QtCore import QTime, QLocale, Qt
from .constructor import get_text_label, get_choice_button


class TrimDialogWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("trim dialog")
        self.setMinimumWidth(250)

        main_text = get_text_label(
            self, "Select the fragment that will remain:"
        )
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        self._set_up_time_edit_widgets()
        choice_button = get_choice_button(self)

        self._set_up_layouts(choice_button, end_text, main_text, start_text)

    def _set_up_time_edit_widgets(self):
        self.start_edit = QtWidgets.QTimeEdit(self)
        self.start_edit.setDisplayFormat("mm:ss")

        self.end_edit = QtWidgets.QTimeEdit(self)
        self.end_edit.setDisplayFormat("mm:ss")

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
        print(self.start_edit.time().second())
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

        self._set_up_time_edit_widgets()
        choice_button = get_choice_button(self)

        self._set_up_layouts(main_text, postfix_text, choice_button)

    def _set_up_time_edit_widgets(self):
        self.speed_edit = QDoubleSpinBox(self)
        self.speed_edit.setDecimals(1)
        self.speed_edit.setValue(1.0)
        self.speed_edit.setLocale(QLocale("C"))

    def _set_up_layouts(self, main_text, postfix_text, choice_button):
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


def run_trim_dialog_window() -> list:
    window = TrimDialogWindow()
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        return window.get_fragment_time()
    else:
        return None


def run_set_speed_dialog_window() -> QTime:
    window = SetSpeedDialogWindow()
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        return window.get_speed()
    else:
        return None


def run_close_event_dialog_window() -> bool:
    text = "You have unsaved changes.\nAre you sure you want to exit?"
    window = AskConfirmationDialogWindow(text)
    window.show()
    return True if window.exec() == QDialog.DialogCode.Accepted else False


def run_undo_dialog_window() -> bool:
    text = "Are you sure you want to undo last action?"
    window = AskConfirmationDialogWindow(text)
    window.show()
    return True if window.exec() == QDialog.DialogCode.Accepted else False
