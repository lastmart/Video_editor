from moviepy.editor import VideoFileClip, concatenate_videoclips
from video_editor_parser import Parser
from video_editor import *

# from PyQt6.QtWidgets import QApplication, QWidget


video_paths = [
    r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/fugu_eat_carrot.mp4",
    r'/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4'
]

# app = QApplication(sys.argv)
# window = QWidget()
# window.show()
# app.exec()
# print(123)
# clips = open_clips(video_paths)
# merged = merge_clips(clips)
# save_clip(merged, "1.mp4")
# trim = trim_clip(clips[0], (0,), (30,))
# save_clip(trim, "3.mp4")

if __name__ == "__main__":
    parser = Parser()
    args = parser.parse_args()
    args.func(args)
