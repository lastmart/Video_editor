from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QDialog
from .constructor import get_choice_button, get_speed_edit_widgets, get_button


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
