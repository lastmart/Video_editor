from video_editor import \
    merge_and_save_videos, trim_and_save_video, \
    set_video_speed_and_save, is_paths_correct, copy_video
from supporting_windows import \
    run_trim_dialog_window, run_set_speed_dialog_window, _get_text_label
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import \
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, \
    QSlider, QStyle, QHBoxLayout, QMenu, QMenuBar
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from cache_handler import CacheHandler
from utils import OperationType
from message import *
import sys
import os


class VideoEditorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Editor")
        self.setGeometry(100, 100, 900, 600)

        self.media_player = QMediaPlayer(None)
        self.audio_output = QAudioOutput()

        self.video_widget = QVideoWidget()
        self.cache_handler = CacheHandler()

        self._set_up_play_button()
        self.prefix_text = _get_text_label(self, "00:00")
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
        self.play_button.clicked.connect(self._change_media_player_state)

    def _set_up_position_slider(self):
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self._set_position)

    def _set_up_layouts(self):
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.prefix_text)
        control_layout.addWidget(self.position_slider)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def _set_up_media_player(self):
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.sourceChanged.connect(self._change_play_button_icon)
        self.media_player.positionChanged.connect(self._update_time_dependent)
        self.media_player.durationChanged.connect(self._change_slider_duration)

    def _play_resulting_video(self):
        self.media_player.setSource(
            QUrl.fromLocalFile(self.cache_handler.get_current_path_to_look())
        )
        self.media_player.setAudioOutput(self.audio_output)
        self.play_button.setEnabled(True)

    def open_file(self):
        user_file_path, _ = QFileDialog.getOpenFileName(self)

        if user_file_path == "":
            return

        try:
            is_paths_correct(user_file_path)
            copy_video(
                user_file_path, self.cache_handler.get_current_path_to_save()
            )
        except IOError:
            raise_wrong_path_error(user_file_path)
        else:
            self._play_resulting_video()

    def save_file(self):
        user_file_path, _ = QFileDialog.getSaveFileName(self)

        if user_file_path == "":
            return

        try:
            is_paths_correct(user_file_path)
            self.cache_handler.save_from_cache(user_file_path)
        except IOError:
            raise_no_file_error()
        except ValueError:
            raise_wrong_path_error(user_file_path)
        else:
            get_success_message(user_file_path)

    def merge_with(self):
        user_file_paths, _ = QFileDialog.getOpenFileNames(self)

        if len(user_file_paths) == 0:
            return

        file_paths = [self.cache_handler.get_current_path_to_look()]
        file_paths.extend(user_file_paths)

        try:
            merge_and_save_videos(
                file_paths, self.cache_handler.get_current_path_to_save()
            )
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
            trim_and_save_video(
                self.cache_handler.get_current_path_to_look(),
                start_time,
                end_time,
                self.cache_handler.get_current_path_to_save()
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
            set_video_speed_and_save(
                self.cache_handler.get_current_path_to_look(),
                speed_float,
                self.cache_handler.get_current_path_to_save()
            )
        except FileNotFoundError:
            raise_no_file_error()
        except ZeroDivisionError:
            raise_wrong_speed_error()
        else:
            self._play_resulting_video()

    def _change_media_player_state(self):
        if self.media_player.isPlaying():
            self.media_player.pause()
        else:
            self.media_player.play()

        self._change_play_button_icon()

    def _change_play_button_icon(self):
        if self.media_player.isPlaying():
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.play_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def _set_position(self, position):
        self.media_player.setPosition(position)

    def _change_slider_duration(self, duration):
        self.position_slider.setRange(0, duration)

    def _update_slider_position(self, position):
        self.position_slider.setValue(position)

    def _update_prefix_text(self, position):
        minutes = int(position / 60000)
        seconds = int((position / 1000) % 60)

        self.prefix_text.setText(f"{minutes:02d}:{seconds:02d}")

    def _update_time_dependent(self, position):
        self._update_prefix_text(position)
        self._update_slider_position(position)

    def closeEvent(self, event):
        closeWindow = self._ask_confirmation()

        if closeWindow:
            self.cache_handler.clear_cache()
            event.accept()
        else:
            event.ignore()

    def _ask_confirmation(self) -> bool:
        # Здесь можно показать диалоговое окно подтверждения
        # или спросить у пользователя, хочет ли он выйти
        # Верните True, если пользователь подтвержд
        return True


def run_gui():
    application = QApplication(sys.argv)
    window = VideoEditorWindow()
    window.show()
    sys.exit(application.exec())


run_gui()
