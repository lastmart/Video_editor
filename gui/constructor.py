from PyQt6 import QtWidgets
from PyQt6.QtCore import QLocale, QTime
from PyQt6.QtWidgets import \
    QStyle, QLabel, QDialog, QDialogButtonBox, QWidget, QPushButton, \
    QDoubleSpinBox, QHBoxLayout
from typing import Union
from .utils import process_time


def get_volume_icon(obj: QWidget) -> QLabel:
    icon = QLabel()
    icon.setPixmap(
        obj.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume).pixmap(
            16, 16
        )
    )
    return icon


def get_text_label(
    obj: Union[QDialog, QWidget], text: str
) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(obj)
    label.setText(text)
    label.adjustSize()

    return label


def get_choice_button(obj: QDialog) -> QDialogButtonBox:
    choice_button = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok |
        QDialogButtonBox.StandardButton.Cancel
    )
    choice_button.accepted.connect(obj.accept)
    choice_button.rejected.connect(obj.reject)

    return choice_button


def get_filename_button(obj: QDialog, func: callable) -> QPushButton:
    button = QPushButton("Select file for merge", obj)
    button.clicked.connect(func)

    return button


def get_speed_edit_widgets(obj: QDialog) -> QDoubleSpinBox:
    speed_edit = QDoubleSpinBox(obj)
    speed_edit.setDecimals(1)
    speed_edit.setValue(1.0)
    speed_edit.setLocale(QLocale("C"))

    return speed_edit


def get_time_edit_widgets(
    obj: QDialog,
    current_time: int
) -> tuple[QtWidgets.QTimeEdit, QtWidgets.QTimeEdit]:
    start_edit = QtWidgets.QTimeEdit(obj)
    start_edit.setDisplayFormat("mm:ss")
    start_edit.setTime(QTime(0, 0, 0, 0))

    end_edit = QtWidgets.QTimeEdit(obj)
    end_edit.setDisplayFormat("mm:ss")
    end_edit.setTime(QTime(*process_time(current_time)))

    return start_edit, end_edit


def get_speed_edit_layout(
    speed_text: str,
    speed_edit: QDoubleSpinBox,
    postfix_text="X"
) -> QHBoxLayout:
    speed_edit_layout = QHBoxLayout()
    speed_edit_layout.addWidget(speed_text)
    speed_edit_layout.addWidget(speed_edit)
    speed_edit_layout.addWidget(postfix_text)

    return speed_edit_layout


def get_time_edit_layout(
    text: str,
    time_edit: QtWidgets.QTimeEdit
) -> QHBoxLayout:
    time_edit_layout = QHBoxLayout()
    time_edit_layout.addWidget(text)
    time_edit_layout.addWidget(time_edit)

    return time_edit_layout
