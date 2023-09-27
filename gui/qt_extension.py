from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QDialog
from .constructor import get_choice_button


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


class MyVideoWidgets(QVideoWidget):
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            position = event.position()

            print(
                "Нажатие в главном окне на координаты:",
                position.x(), position.y()
            )

        super().mousePressEvent(event)
