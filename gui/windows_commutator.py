import gevent
from .qt_extensions import MyVideoWidget, MyDialogWindowWithCommutator


class Commutator:
    def __init__(self, sender: MyVideoWidget, receiver: MyDialogWindowWithCommutator):
        self.sender = sender
        self.receiver = receiver

    def start(self):
        receiver_greenlet = gevent.spawn(self.receive)
        receiver_greenlet.join()

    def receive(self):
        while True:
            position = self.sender.position
            if position is not None:
                print("Position received:", position)
                self.receiver.x_edit.setValue(position.x())
                self.receiver.y_edit.setValue(position.y())
                break
