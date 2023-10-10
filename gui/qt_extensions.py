from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QDialog, QPushButton, QSpinBox
from .constructor import get_choice_button, get_button
from .utils import get_open_file_names


class MyDialogWindow(QDialog):
    def __init__(self, title: str, have_choice_button=True):
        super().__init__()

        self.setWindowTitle(title)
        self.setMinimumWidth(250)

        if have_choice_button:
            self.choice_button = get_choice_button(self)

    def get_result(self):
        pass

    def execute(self) -> tuple:
        self.show()
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.get_result()
        else:
            return None


class OpenFilenameDialogMixin:
    def __init__(self):
        self.available_filters = None
        self.target = None
        self.filenames = None
        self.filename_button = None

    def configurate(
        self,
        obj: MyDialogWindow,
        button_title: str,
        available_filters="(*.mp4)"
    ):
        self.target = obj
        self.filenames = None
        self.available_filters = available_filters

        self.filename_button = get_button(
            self.target,
            button_title,
            self.get_open_filenames_wrapper
        )

    def get_open_filenames_wrapper(self) -> None:
        self.filenames = get_open_file_names(
            self.target,
            self.available_filters
        )
        if len(self.filenames) == 0:
            return
        self.filename_button.setText("The files were selected")
        self.filename_button.setEnabled(False)
        self.target.done(1)


class MyVideoWidget(QVideoWidget):
    def __init__(self):
        super().__init__()
        self._need_to_start_send = False
        self.position = None

    def start_send(self) -> None:
        self._need_to_start_send = True
        self.position = None

    def stop_send(self) -> None:
        self._need_to_start_send = False

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            position = event.position()

            print(
                "Clicking on coordinates:",
                position.x(), position.y()
            )
            self.position = position

        super().mousePressEvent(event)


class MyAsyncButtonData:
    def __init__(
        self,
        obj: QDialog,
        title: str,
        tip: str,
        edit_devices: tuple[QSpinBox, QSpinBox],
    ):
        super().__init__()
        self.internal_button = QPushButton(title, obj)
        self.internal_button.setToolTip(tip)
        self.edit_devices = edit_devices


class MyAsyncButton(QObject):
    clicked = pyqtSignal(MyAsyncButtonData)

    def __init__(
        self,
        obj: QDialog,
        title: str,
        tip: str,
        edit_devices: tuple[QSpinBox, QSpinBox],
        slot: callable
    ):
        super().__init__()
        self.button_data = MyAsyncButtonData(obj, title, tip, edit_devices)
        self.button_data.internal_button.clicked.connect(self.emitClicked)
        self.clicked.connect(slot)

    def emitClicked(self):
        self.clicked.emit(self.button_data)
