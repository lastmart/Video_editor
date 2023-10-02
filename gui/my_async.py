import asyncio
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QPushButton, QSpinBox
from .constructor import get_point_edit_widget
from .qt_extensions import \
    MyDialogWindow, MyVideoWidget, \
    MyAsyncButton, MyAsyncButtonData


class MyAsyncDialogWindow(MyDialogWindow):
    def __init__(
        self,
        title: str,
        sender: MyVideoWidget,
        have_choice_button=True
    ):
        super().__init__(title, have_choice_button)
        self.sender = sender
        self.threadpool = QThreadPool()
        self.tip = "To do this, move the cursor to the desired location " \
                   "in the main window and click"

        self.x_edit, self.y_edit = get_point_edit_widget(self)
        self.location_button = MyAsyncButton(
            self,
            "Select location for upper left",
            self.tip,
            (self.x_edit, self.y_edit),
            self.slot,
        )

    def slot(self, data: MyAsyncButtonData):
        self.start_async_task(data)

    def start_async_task(self, button_data: MyAsyncButtonData):
        button = button_data.internal_button
        print(f"Current button name: {button.text()}")
        update_async_button(button, while_async=True)
        worker = AsyncCommutator(self.sender, button_data.edit_devices)
        worker.signals.finished.connect(
            lambda: update_async_button(button, False)
        )
        self.threadpool.start(worker)

    def get_result(self) -> tuple:
        pass


def update_async_button(button: QPushButton, while_async: bool) -> None:
    """
    If 'while_async' equals true, it is while my_async
    Else it is when async_finished
    """
    print(f"Updating '{button.text()}' button")
    text = "Go to main window" if while_async else "Select location"
    button.setEnabled(not while_async)
    button.setText(text)


class CommutatorSignals(QObject):
    finished = pyqtSignal()


class AsyncCommutator(QRunnable):
    def __init__(
        self,
        sender: MyVideoWidget,
        receiver_devices: tuple[QSpinBox, QSpinBox]
    ):
        super().__init__()
        self.sender = sender
        self.x_edit_receiver, self.y_edit_receiver = receiver_devices
        self.signals = CommutatorSignals()

    async def receive(self) -> None:
        self.sender.start_send()

        while True:
            await asyncio.sleep(1)
            position = self.sender.position
            if position is not None:
                print("Position received:", position)
                self.x_edit_receiver.setValue(int(position.x()))
                self.y_edit_receiver.setValue(int(position.y()))
                break

        self.sender.stop_send()

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def async_task_wrapper():
            await self.receive()
            self.signals.finished.emit()

        loop.run_until_complete(async_task_wrapper())
