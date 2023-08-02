from enum import Enum
from os import getcwd
from pathlib import Path


class MessageType(Enum):
    SUCCESS = 1
    ERROR = 2


BASE_PATH_TO_SAVE = str(Path(str(getcwd())) / 'gui' / 'cache' / 'temp.mp4')
