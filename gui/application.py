from video_editor import \
    merge_clips, trim_clip, set_clip_speed, \
    save_clip, open_clips
from moviepy.editor import VideoFileClip
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import \
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QLabel, QSlider, QStyle, QSizePolicy, QHBoxLayout, QMenu, QMenuBar, \
    QToolBar, QMessageBox, QDialog
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer
from base import BASE_PATH_TO_SAVE
from message import *
import sys


class VideoEditorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Editor")
        self.setGeometry(100, 100, 800, 600)

        self.current_video = None

        self.media_player = QMediaPlayer(None)
        self.video_widget = QVideoWidget()

        self._set_up_play_button()
        self._set_up_position_slider()
        self._set_up_layout()
        self._set_up_media_player()
        self._set_up_menu_bar()

    def _set_up_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(True)

        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)

        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)

        edit_menu = QMenu("&Edit", self)
        self.menu_bar.addMenu(edit_menu)

        edit_menu.addAction("Merge with", self.merge_with)
        #edit_menu.addAction("Trim", self.trim)

    def _set_up_play_button(self):
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self.play_video)

    def _set_up_position_slider(self):
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

    def _set_up_layout(self):
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def _set_up_media_player(self):
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.sourceChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self)

        try:
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.play_button.setEnabled(True)
            self.current_video = open_clips(file_path)
        except IOError:
            raise_wrong_path_error(file_path)

    def save_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self)

        try:
            save_clip(self.current_video, file_path)
        except IOError:
            raise_no_file_error()
        except ValueError:
            raise_wrong_path_error(file_path)
        else:
            get_success_message(file_path)

    def merge_with(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self)

        videos = [self.current_video]
        for file_path in file_paths:
            try:
                videos.append(open_clips(file_path))
            except IOError:
                raise_wrong_path_error(file_path)
                break

        self.current_video = merge_clips(videos)
        save_clip(self.current_video, BASE_PATH_TO_SAVE)
        self.media_player.setSource(QUrl.fromLocalFile(BASE_PATH_TO_SAVE))

    def trim(self):
        trim_dialog_window = QDialog()

    def play_video(self):
        if self.media_player.isPlaying():
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self):
        if self.media_player.isPlaying():
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def position_changed(self, position):
        self.position_slider.setValue(position)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)


def run_gui():
    application = QApplication(sys.argv)
    window = VideoEditorWindow()
    window.show()
    sys.exit(application.exec())


run_gui()
