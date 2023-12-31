from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6.QtCore import QTime, QPointF
from .constructor import \
    get_text_label, get_choice_button, \
    get_speed_edit_widget, get_time_edit_widgets, \
    get_speed_edit_layout, get_time_edit_layout, \
    get_time_edit_widget, get_point_edit_layout, \
    get_point_edit_widget
from .my_async import MyAsyncDialogWindow
from .qt_extensions import \
    MyDialogWindow, MyVideoWidget, \
    OpenFilenameDialogMixin, MyAsyncButton


class TrimDialogWindow(MyDialogWindow):
    def __init__(self, current_time: int, text: str):
        super().__init__("trim dialog")

        main_text = get_text_label(
            self, text
        )
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        self.start_edit, self.end_edit = \
            get_time_edit_widgets(self, current_time)

        self._set_up_layouts(main_text, start_text, end_text)

    def _set_up_layouts(
        self,
        main_text,
        start_text,
        end_text,
    ) -> None:
        start_layout = get_time_edit_layout(start_text, self.start_edit)
        end_layout = get_time_edit_layout(end_text, self.end_edit)

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QTime, QTime]:
        return self.start_edit.time(), self.end_edit.time()


class SetSpeedDialogWindow(MyDialogWindow):
    def __init__(self):
        super().__init__("set speed dialog")

        main_text = get_text_label(
            self, "Set new video speed:"
        )
        self.speed_edit = get_speed_edit_widget(self)

        self._set_up_layouts(main_text)

    def _set_up_layouts(
        self,
        main_text,
    ):
        speed_edit_layout = get_speed_edit_layout(
            self, main_text, self.speed_edit
        )

        main_layout = QVBoxLayout()
        main_layout.addLayout(speed_edit_layout)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> QTime:
        return self.speed_edit.value()


class SetPartialSpeedDialogWindow(MyDialogWindow):
    def __init__(self, current_time: int):
        super().__init__("set speed dialog")

        time_text = get_text_label(self, "Select video fragment")
        start_text = get_text_label(self, "start time")
        end_text = get_text_label(self, "end time")

        speed_text = get_text_label(
            self, "Set new speed for fragment:"
        )

        self.start_edit, self.end_edit = \
            get_time_edit_widgets(self, current_time)
        self.speed_edit = get_speed_edit_widget(self)

        self._set_up_layouts(
            time_text,
            start_text,
            end_text,
            speed_text,
        )

    def _set_up_layouts(
        self,
        time_text,
        start_text,
        end_text,
        speed_text,
    ):
        start_layout = get_time_edit_layout(start_text, self.start_edit)
        end_layout = get_time_edit_layout(end_text, self.end_edit)
        speed_edit_layout = get_speed_edit_layout(
            self, speed_text, self.speed_edit
        )

        main_layout = QVBoxLayout()
        main_layout.addWidget(time_text)
        main_layout.addLayout(start_layout)
        main_layout.addLayout(end_layout)
        main_layout.addWidget(speed_text)
        main_layout.addLayout(speed_edit_layout)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QTime, QTime, QTime]:
        return self.start_edit.time(), \
               self.end_edit.time(), \
               self.speed_edit.value()


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


class MergeIntoDialogWindow(MyDialogWindow, OpenFilenameDialogMixin):
    def __init__(self, current_time: int):
        super().__init__("merge into dialog", have_choice_button=False)
        self.configurate(self, "Select file for merge")

        main_text = get_text_label(
            self, "Select the time at which the merge will be performed"
        )
        self.time_edit = get_time_edit_widget(self, current_time)

        self._set_up_layouts(main_text)

    def _set_up_layouts(self, main_text):
        time_edit_layout = get_time_edit_layout(main_text, self.time_edit)

        main_layout = QVBoxLayout()
        main_layout.addLayout(time_edit_layout)
        main_layout.addWidget(self.filename_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QTime, list[str]]:
        return self.time_edit.time(), self.filenames


class OverlayDialogWindow(MyAsyncDialogWindow, OpenFilenameDialogMixin):
    def __init__(self, sender: MyVideoWidget):
        super().__init__(
            "overlay dialog window",
            sender,
            have_choice_button=False
        )
        self.configurate(
            self,
            button_title="Select mp4, png, jpeg files for overlay",
            available_filters="(*.mp4 *.png *.jpeg)"
        )

        main_text = get_text_label(
            self,
            "Select the position of the upper left corner\n"
            "of the overlay media using the cursor"
        )

        self._set_up_layouts(main_text)

    def _set_up_layouts(self, main_text):
        point_edit_layout = get_point_edit_layout(
            self, self.x_edit, self.y_edit
        )

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addLayout(point_edit_layout)
        main_layout.addWidget(self.location_button.button_data.internal_button)
        main_layout.addWidget(self.filename_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QPointF, list[str]]:
        return QPointF(self.x_edit.value(), self.y_edit.value()), \
               self.filenames


class CropDialogWindow(MyAsyncDialogWindow):
    def __init__(self, sender: MyVideoWidget):
        super().__init__(
            "crop dialog window",
            sender,
            have_choice_button=True
        )

        main_text = get_text_label(
            self,
            "Select the position of the upper left\n"
            "and lower right corners to be cropped"
        )
        self.x2_edit, self.y2_edit = get_point_edit_widget(self)

        self.location2_button = MyAsyncButton(
            self,
            "Select location for lower right",
            self.tip,
            (self.x2_edit, self.y2_edit),
            self.slot
        )
        self.location2_button.clicked.connect(self.slot)

        self._set_up_layouts(main_text)

    def _set_up_layouts(self, main_text):
        point_edit_layout = get_point_edit_layout(
            self, self.x_edit, self.y_edit
        )
        point2_edit_layout = get_point_edit_layout(
            self, self.x2_edit, self.y2_edit
        )

        main_layout = QVBoxLayout()
        main_layout.addWidget(main_text)
        main_layout.addLayout(point_edit_layout)
        main_layout.addWidget(self.location_button.button_data.internal_button)
        main_layout.addLayout(point2_edit_layout)
        main_layout.addWidget(self.location2_button.button_data.internal_button)
        main_layout.addWidget(self.choice_button)

        self.setLayout(main_layout)

    def get_result(self) -> tuple[QPointF, QPointF]:
        return QPointF(self.x_edit.value(), self.y_edit.value()), \
               QPointF(self.x2_edit.value(), self.y2_edit.value())


def run_trim_dialog_window(
    current_time: int, main_text: str
) -> tuple[QTime, QTime]:
    window = TrimDialogWindow(current_time, main_text)
    return window.execute()


def run_merge_into_dialog_window(current_time: int) -> tuple[QTime, list[str]]:
    window = MergeIntoDialogWindow(current_time)
    return window.execute()


def run_set_speed_dialog_window() -> QTime:
    window = SetSpeedDialogWindow()
    return window.execute()


def run_set_partial_speed_dialog_window(current_time: int) -> QTime:
    window = SetPartialSpeedDialogWindow(current_time)
    return window.execute()


def run_overlay_dialog_window(
    sender: MyVideoWidget
) -> tuple[QPointF, list[str]]:
    window = OverlayDialogWindow(sender)
    return window.execute()


def run_crop_dialog_window(sender: MyVideoWidget):
    window = CropDialogWindow(sender)
    return window.execute()


def run_ask_confirmation_dialog_window(text: str) -> bool:
    window = AskConfirmationDialogWindow(text)
    window.show()
    return True if window.exec() == QDialog.DialogCode.Accepted else False
