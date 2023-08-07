from PyQt6.QtWidgets import QMessageBox
from .utils import MessageType


def raise_wrong_path_error(file_path):
    text = f"No such file:'{file_path}'"
    get_base_message(text, MessageType.ERROR)


def raise_no_file_error():
    text = "There is no file to work with, please open it"
    get_base_message(text, MessageType.ERROR)


def raise_wrong_time_error():
    text = "Start or end time is incorrect"
    get_base_message(text, MessageType.ERROR)


def raise_wrong_speed_error():
    text = "Speed is incorrect"
    get_base_message(text, MessageType.ERROR)


def raise_nothing_to_undo_error():
    text = "There's nothing to undo here"
    get_base_message(text, MessageType.ERROR)


def get_success_message(file_path):
    text = f"The file was successfully saved to the path:\n'{file_path}'"
    get_base_message(text, MessageType.SUCCESS)


def get_base_message(text: str, mode: MessageType):
    base_message = QMessageBox()
    base_message.setWindowTitle("Error") \
        if mode is MessageType.ERROR \
        else base_message.setWindowTitle("Success")
    base_message.setText(text)
    base_message.setIcon(QMessageBox.Icon.Critical) \
        if mode is MessageType.ERROR \
        else base_message.setIcon(QMessageBox.Icon.Information)
    base_message.setStandardButtons(QMessageBox.StandardButton.Ok)

    base_message.exec()
