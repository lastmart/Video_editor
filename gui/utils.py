from enum import Enum


class MessageType(Enum):
    SUCCESS = 1
    ERROR = 2


class OperationType(Enum):
    Increase = 1
    Decrease = 2
