from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import \
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QLabel, QSlider, QStyle, QSizePolicy, QHBoxLayout
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer
import sys


class VideoEditorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Editor")
        self.setGeometry(100, 100, 800, 600)
        self.mediaPlayer = QMediaPlayer(None)

        videoWidget = QVideoWidget()

        openButton = QPushButton("Open Video")
        openButton.clicked.connect(self.openFile)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.playVideo)

        self.positionSlider = QSlider(Qt.Orientation.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.sourceChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filePath != '':
            self.mediaPlayer.setSource(QUrl.fromLocalFile(filePath))
            self.playButton.setEnabled(True)

    def playVideo(self):
        if self.mediaPlayer.isPlaying():
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.isPlaying():
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)


def run_gui():
    application = QApplication(sys.argv)
    window = VideoEditorWindow()
    window.show()
    sys.exit(application.exec())


run_gui()
