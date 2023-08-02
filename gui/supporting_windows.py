from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QDialog, QDialogButtonBox, \
    QVBoxLayout, QLabel, QHBoxLayout
import sys


class TrimDialogWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("trim dialog")
        self.setMinimumWidth(250)

        main_text = QtWidgets.QLabel(self)
        main_text.setText("Select the fragment to be trimmed:")
        main_text.adjustSize()

        start_text = QtWidgets.QLabel(self)
        start_text.setText("start time")
        start_text.adjustSize()

        end_text = QtWidgets.QLabel(self)
        end_text.setText("end time")
        end_text.adjustSize()

        start_edit = QtWidgets.QTimeEdit(self)
        end_edit = QtWidgets.QTimeEdit(self)

        choice_button = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        choice_button.accepted.connect(self.accept)
        choice_button.rejected.connect(self.reject)

        start_layout = QHBoxLayout()
        start_layout.addWidget(start_text)
        start_layout.addWidget(start_edit)

        end_layout = QHBoxLayout()
        end_layout.addWidget(end_text)
        end_layout.addWidget(end_edit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(choice_button)

        self.setLayout(main_layout)


def run_trim_dialog_window():
    application = QApplication(sys.argv)
    window = TrimDialogWindow()
    window.show()
    if window.exec() == QDialog.DialogCode.Accepted:
        print("Dialog accepted")
    else:
        print("Dialog rejected")
    sys.exit(application.exec())


run_trim_dialog_window()
