from PyQt6 import QtWidgets
from PyQt6.QtWidgets import \
    QDialog, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import QTime
from typing import Union


class TrimDialogWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("trim dialog")
        self.setMinimumWidth(250)

        main_text = _get_text_label(
            self, "Select the fragment that will remain:"
        )
        start_text = _get_text_label(self, "start time")
        end_text = _get_text_label(self, "end time")

        self._set_up_time_edit_widgets()
        choice_button = _get_choice_button(self)

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

        main_text = _get_text_label(
            self, "Set new video speed:"
        )
        postfix_text = _get_text_label(self, "X")

        self._set_up_time_edit_widgets()
        choice_button = _get_choice_button(self)

        self._set_up_layouts(main_text, postfix_text, choice_button)

    def _set_up_time_edit_widgets(self):
        self.time_edit = QtWidgets.QTimeEdit(self)
        self.time_edit.setDisplayFormat("mm:ss")

    def _set_up_layouts(self, main_text, postfix_text, choice_button):
        time_edit_layout = QHBoxLayout()
        time_edit_layout.addWidget(main_text)
        time_edit_layout.addWidget(self.time_edit)
        time_edit_layout.addWidget(postfix_text)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_edit_layout)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)

    def get_speed(self) -> QTime:
        return self.time_edit.time()


def _get_text_label(obj: Union[QDialog, QWidget], text: str):
    label = QtWidgets.QLabel(obj)
    label.setText(text)
    label.adjustSize()

    return label


def _get_choice_button(obj: QDialog):
    choice_button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )
    choice_button.accepted.connect(obj.accept)
    choice_button.rejected.connect(obj.reject)

    return choice_button


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
