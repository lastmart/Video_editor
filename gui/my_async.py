import asyncio
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable
from PyQt6.QtCore import QThreadPool
from PyQt6.QtWidgets import QPushButton
from .constructor import get_button, get_point_edit_widget
from .qt_extensions import MyDialogWindow, MyVideoWidget


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

        self.x_edit, self.y_edit = get_point_edit_widget(self)

        self.location_button = get_button(
            self, "Select location", self.start_async_task
            )
        tip = (
            "To do this, move the cursor to the desired "
            "location in the main window and click"
        )
        self.location_button.setToolTip(tip)

    def start_async_task(self):
        update_async_button(self.location_button, while_async=True)
        worker = AsyncCommutator(self.sender, receiver=self)
        worker.signals.finished.connect(self.on_async_task_finished)
        self.threadpool.start(worker)

    def on_async_task_finished(self):
        update_async_button(self.location_button, while_async=False)

    def get_result(self) -> tuple:
        pass


def update_async_button(button: QPushButton, while_async: bool) -> None:
    """
    If 'while_async' equals true, it is while my_async
    Else it is when async_finished
    """
    text = "Go to main window" if while_async else "Select location"
    button.setEnabled(not while_async)
    button.setText(text)


class CommutatorSignals(QObject):
    finished = pyqtSignal()


class AsyncCommutator(QRunnable):
    def __init__(self, sender: MyVideoWidget, receiver: MyAsyncDialogWindow):
        super().__init__()
        self.sender = sender
        self.receiver = receiver
        self.signals = CommutatorSignals()

    async def receive(self) -> None:
        self.sender.start_send()

        while True:
            await asyncio.sleep(1)
            position = self.sender.position
            if position is not None:
                print("Position received:", position)
                self.receiver.x_edit.setValue(int(position.x()))
                self.receiver.y_edit.setValue(int(position.y()))
                break

        self.sender.stop_send()

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def async_task_wrapper():
            await self.receive()
            self.signals.finished.emit()

        loop.run_until_complete(async_task_wrapper())
