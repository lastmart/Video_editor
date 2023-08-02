from video_editor import \
    merge_clips, trim_clip, set_clip_speed, \
    save_clip, open_clips
from supporting_windows import \
    run_trim_dialog_window, run_set_speed_dialog_window
from moviepy.editor import VideoFileClip
from PyQt6.QtCore import Qt, QUrl, QTime
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
        self._set_up_layouts()
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
        edit_menu.addAction("Trim", self.trim)
        edit_menu.addAction("Set speed", self.set_speed)

    def _set_up_play_button(self):
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self._play_video)

    def _set_up_position_slider(self):
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self._set_position)

    def _set_up_layouts(self):
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def _set_up_media_player(self):
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.sourceChanged.connect(self._media_state_changed)
        self.media_player.positionChanged.connect(self._position_changed)
        self.media_player.durationChanged.connect(self._duration_changed)

    def _play_resulting_video(self):
        save_clip(self.current_video, BASE_PATH_TO_SAVE)
        self.media_player.setSource(QUrl.fromLocalFile(BASE_PATH_TO_SAVE))

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

        try:
            self.current_video = merge_clips(videos)
        except FileNotFoundError:
            raise_no_file_error()
        else:
            self._play_resulting_video()

    def trim(self):
        fragment_time = run_trim_dialog_window()

        if fragment_time is None:
            return

        start = fragment_time[0]
        end = fragment_time[1]

        start_time = (start.minute(), start.second())
        end_time = (end.minute(), end.second())

        try:
            self.current_video = trim_clip(
                self.current_video, start_time, end_time
            )
        except FileNotFoundError:
            raise_no_file_error()
        except IOError:
            raise_wrong_time_error()
        else:
            self._play_resulting_video()

    def set_speed(self):
        speed = run_set_speed_dialog_window()

        if speed is None:
            return

        speed_float = speed.minute() + speed.second()/10

        try:
            self.current_video = set_clip_speed(
                self.current_video, speed_float
            )
        except FileNotFoundError:
            raise_no_file_error()
        except ZeroDivisionError:
            raise_wrong_speed_error()
        else:
            self._play_resulting_video()

    def _play_video(self):
        if self.media_player.isPlaying():
            self.media_player.pause()
        else:
            self.media_player.play()

    def _media_state_changed(self):
        if self.media_player.isPlaying():
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def _position_changed(self, position):
        self.position_slider.setValue(position)

    def _duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def _set_position(self, position):
        self.media_player.setPosition(position)


def run_gui():
    application = QApplication(sys.argv)
    window = VideoEditorWindow()
    window.show()
    sys.exit(application.exec())


run_gui()
