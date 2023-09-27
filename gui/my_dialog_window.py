from PyQt6.QtWidgets import QDialog
from gui.constructor import get_choice_button


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
