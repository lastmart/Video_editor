import sys
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import \
    QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, \
    QStyle, QHBoxLayout, QMenu, QMenuBar, QSpacerItem, QSizePolicy
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from VideoEditor.video_editor import \
    merge_videos_and_save, trim_and_save_video, \
    set_video_speed_and_save, copy_video
from .supporting_windows import \
    run_trim_dialog_window, run_set_speed_dialog_window, \
    run_ask_confirmation_dialog_window, run_merge_into_dialog_window, run_set_partial_speed_dialog_window, run_overlay_dialog_window
from .cache_handler import cache_handler
from .utils import \
    OperationType, OperationSystem, OS_TYPE, get_open_file_name, \
    get_open_file_names, get_save_file_name, process_time
from .constructor import get_volume_icon, get_text_label
from .qt_extensions import MyVideoWidget
from .message import *


class VideoEditorWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Editor")
        self.setGeometry(100, 100, 900, 600)

        self.media_player = QMediaPlayer(None)
        self.video_widget = MyVideoWidget()
        self.audio_output = QAudioOutput()

        self._set_up_play_button()
        self.prefix_text = get_text_label(self, "00:00")
        self._set_up_video_slider()
        self._set_up_audio_slider()
        self._set_up_layouts()
        self._set_up_media_player()
        self._set_up_menu_bar()

        self.have_unsaved_changes = False
        self.configurate_cache_handler()

    def configurate_cache_handler(self) -> None:
        if not cache_handler.is_empty():
            text = "Do you want to restore history from your previous session?"
            need_to_restore = run_ask_confirmation_dialog_window(text)
            if need_to_restore:
                cache_handler.restore_history()
                self.have_unsaved_changes = True
                self._play_resulting_video()
            else:
                cache_handler.clear_cache(
                    cache_handler.index_from_previous_session
                )

    def _set_up_menu_bar(self):
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setNativeMenuBar(True)

        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)

        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)

        edit_menu = QMenu("&Edit", self)
        self.menu_bar.addMenu(edit_menu)

        tools_submenu = QMenu("&Tools", self)
        edit_menu.addMenu(tools_submenu)

        tools_submenu.addAction("Merge with", self.merge_with)
        tools_submenu.addAction("Trim", self.trim)
        tools_submenu.addAction("Set speed", self.set_speed)
        tools_submenu.addAction("Overlay", self.overlay)

        partial_tools_submenu = QMenu("&Partial tools", self)
        edit_menu.addMenu(partial_tools_submenu)

        partial_tools_submenu.addAction("Merge into", self.merge_into)
        partial_tools_submenu.addAction("Cut out", self.cut_out)
        partial_tools_submenu.addAction("Set speed", self.set_partial_speed)

        history_submenu = QMenu("&History", self)
        edit_menu.addMenu(history_submenu)

        history_submenu.addAction("Undo", self.undo)
        history_submenu.addAction("Redo", self.redo)
        history_submenu.addAction("Clear history", self.clear_history)

    def _set_up_play_button(self):
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.clicked.connect(self._change_media_player_state)

    def _set_up_video_slider(self):
        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setRange(0, 0)
        self.video_slider.sliderMoved.connect(
            lambda position: self.media_player.setPosition(position)
        )

    def _set_up_audio_slider(self):
        self.audio_slider = QSlider(Qt.Orientation.Horizontal)
        self.audio_slider.setRange(0, 100)
        self.audio_slider.setValue(50)
        self.audio_slider.sliderMoved.connect(
            lambda position: self.audio_output.setVolume(position / 100)
        )

    def _set_up_layouts(self):
        y_offset = 20 if OS_TYPE != OperationSystem.MACOS else 0
        spacer = QSpacerItem(
            0, y_offset, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        upper_control_layout = QHBoxLayout()
        upper_control_layout.addWidget(self.play_button)
        upper_control_layout.addWidget(get_volume_icon(self))
        upper_control_layout.addWidget(self.audio_slider)

        lower_control_layout = QHBoxLayout()
        lower_control_layout.addWidget(self.prefix_text)
        lower_control_layout.addWidget(self.video_slider)

        main_layout = QVBoxLayout()
        main_layout.addItem(spacer)
        main_layout.addWidget(self.video_widget)
        main_layout.addLayout(upper_control_layout)
        main_layout.addLayout(lower_control_layout)

        self.setLayout(main_layout)

    def _set_up_media_player(self):
        self.media_player.sourceChanged.connect(self._change_play_button_icon)
        self.media_player.positionChanged.connect(self._update_time_dependent)
        self.media_player.durationChanged.connect(
            lambda duration: self.video_slider.setRange(0, duration)
        )
        self.media_player.mediaStatusChanged.connect(
            self._process_media_status_changed
        )

    def _play_resulting_video(self):
        self.media_player.setSource(
            QUrl.fromLocalFile(cache_handler.get_current_path_to_look())
        )
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        self.play_button.setEnabled(True)

    def undo(self):
        text = "Are you sure you want to undo last action?"
        need_to_undo = run_ask_confirmation_dialog_window(text)

        if need_to_undo:
            try:
                cache_handler.undo()
            except FileNotFoundError:
                raise_nothing_to_undo_error()
            except IOError as e:
                raise_cache_error(e.__str__())
            else:
                self.have_unsaved_changes = True
                self._play_resulting_video()

    def redo(self):
        text = "Are you sure you want to redo previous action?"
        need_to_redo = run_ask_confirmation_dialog_window(text)

        if need_to_redo:
            try:
                cache_handler.redo()
            except FileNotFoundError:
                raise_nothing_to_redo_error()
            else:
                self.have_unsaved_changes = True
                self._play_resulting_video()

    def clear_history(self):
        cache_handler.clear_cache()
        self.play_button.setEnabled(False)
        self.have_unsaved_changes = False

    def open_file(self):
        user_file_path = get_open_file_name(self)

        if user_file_path == "":
            return

        try:
            cache_handler.prepare_cache_folder(
                cache_handler.current_index + 1
            )

            copy_video(
                user_file_path, cache_handler.get_current_path_to_save()
            )
        except IOError:
            raise_open_error(user_file_path)
        except ValueError:
            raise_wrong_extension_error(user_file_path)
        else:
            cache_handler.update_current_index(OperationType.INCREASE)
            self.have_unsaved_changes = False
            self._play_resulting_video()

    def save_file(self):
        if cache_handler.current_index == 0:
            raise_no_file_error()
            return

        user_file_path = get_save_file_name(self)

        if user_file_path == "":
            return

        try:
            cache_handler.save_from_cache(user_file_path)
        except IOError:
            raise_save_error(user_file_path)
        else:
            self.have_unsaved_changes = False
            get_success_save_message(user_file_path)

    def merge_with(self):
        if cache_handler.current_index == 0:
            raise_no_file_error()
            return

        user_file_paths = get_open_file_names(self)

        if len(user_file_paths) == 0:
            return

        file_paths = [cache_handler.get_current_path_to_look()]
        file_paths.extend(user_file_paths)

        try:
            cache_handler.prepare_cache_folder(
                cache_handler.current_index + 1
            )

            merge_videos_and_save(
                file_paths, cache_handler.get_current_path_to_save()
            )
        except IOError as e:
            raise_open_error(e.__str__())
        else:
            cache_handler.update_current_index(OperationType.INCREASE)
            self.have_unsaved_changes = True
            self._play_resulting_video()

    # TODO
    def merge_into(self):
        print(run_merge_into_dialog_window(self.video_slider.value()))

    def _base_merge(self, get_users_data: callable):
        pass

    def trim(self):
        main_text = "Select the fragment that will remain:"
        self._base_cut(main_text, trim_and_save_video)

    def cut_out(self):
        main_text = "Select the fragment that will be deleted:"
        # TODO
        self._base_cut(main_text, trim_and_save_video)

    def _base_cut(self,
                  main_text: str,
                  cut_func: callable([str, int, int, str])
                  ) -> None:
        if cache_handler.current_index == 0:
            raise_no_file_error()
            return

        fragment_time = run_trim_dialog_window(
            self.video_slider.value(),
            main_text
        )

        if fragment_time is None:
            return

        start = fragment_time[0]
        end = fragment_time[1]

        start_time = (start.minute(), start.second())
        end_time = (end.minute(), end.second())

        try:
            cache_handler.prepare_cache_folder(
                cache_handler.current_index + 1
            )

            cut_func(
                cache_handler.get_current_path_to_look(),
                start_time,
                end_time,
                cache_handler.get_current_path_to_save()
            )
        except RuntimeError:
            raise_wrong_time_error()
        else:
            cache_handler.update_current_index(OperationType.INCREASE)
            self.have_unsaved_changes = True
            self._play_resulting_video()

    def set_speed(self):
        if cache_handler.current_index == 0:
            raise_no_file_error()
            return

        speed = run_set_speed_dialog_window()

        if speed is None:
            return

        try:
            cache_handler.prepare_cache_folder(
                cache_handler.current_index + 1
            )

            set_video_speed_and_save(
                cache_handler.get_current_path_to_look(),
                speed,
                cache_handler.get_current_path_to_save()
            )
        except (ZeroDivisionError, ValueError):
            raise_wrong_speed_error()
        else:
            cache_handler.update_current_index(OperationType.INCREASE)
            self.have_unsaved_changes = True
            self._play_resulting_video()

    def set_partial_speed(self):
        print(run_set_partial_speed_dialog_window(self.video_slider.value()))

    def overlay(self):
        print(run_overlay_dialog_window(self.video_widget))

    def _process_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self._change_play_button_icon()

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

    def _update_prefix_text(self, position):
        minutes, seconds = process_time(position)[1:3]

        self.prefix_text.setText(f"{minutes:02d}:{seconds:02d}")

    def _update_time_dependent(self, position):
        self._update_prefix_text(position)
        self.video_slider.setValue(position)

    def closeEvent(self, event):
        need_to_close_window = True
        if self.have_unsaved_changes:
            text = "You have unsaved changes.\nAre you sure you want to exit?"
            need_to_close_window = run_ask_confirmation_dialog_window(text)

        if need_to_close_window:
            event.accept()
        else:
            event.ignore()


def run_gui():
    application = QApplication(sys.argv)
    window = VideoEditorWindow()
    window.show()
    sys.exit(application.exec())
