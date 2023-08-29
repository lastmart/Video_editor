from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import \
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QSlider, QStyle, QHBoxLayout, QMenu, QMenuBar, QLabel
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


def get_volume_icon(obj: QWidget) -> QLabel:
    icon = QLabel()
    icon.setPixmap(
        obj.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume).pixmap(
            16, 16
        )
    )
    return icon
