import asyncio
from .qt_extensions import MyVideoWidget, MyDialogWindowWithCommutator


class Commutator:
    def __init__(self, sender: MyVideoWidget, receiver: MyDialogWindowWithCommutator):
        self.sender = sender
        self.receiver = receiver

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.receive())
        loop.close()

    async def receive(self):
        while True:
            await asyncio.sleep(1)
            position = self.sender.position
            if position is not None:
                print("Position received:", position)
                self.receiver.x_edit.setValue(position.x())
                self.receiver.y_edit.setValue(position.y())
                break
