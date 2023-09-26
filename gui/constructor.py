from PyQt6 import QtWidgets
from PyQt6.QtWidgets import \
    QStyle, QLabel, QDialog, QDialogButtonBox, QWidget, QPushButton
from typing import Union


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
