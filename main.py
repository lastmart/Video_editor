from moviepy.editor import VideoFileClip, concatenate_videoclips
from video_editor import *
from PyQt5.QtWidgets import QApplication, QWidget
import sys

video_paths = [
   "/Users/dimasta/work/Video_editor/resources/fugu_eat_carrot.mp4",
   "/Users/dimasta/work/Video_editor/resources/shrek_dancing.mp4"
]
app = QApplication(sys.argv)
window = QWidget()
window.show()
app.exec()
print(123)
#merged = merge_clips(clips)
#save_clip(merged, "1.mp4")

#speeded = set_clip_speed(clips[0], 0.5)
#save_clip(speeded, "3.mp4")
