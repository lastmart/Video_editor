from moviepy.editor import VideoFileClip, concatenate_videoclips
from video_editor import *


video_paths = [
   "/Users/dimasta/work/Video_editor/resources/fugu_eat_carrot.mp4",
   "/Users/dimasta/work/Video_editor/resources/shrek_dancing.mp4"
]

clips = open_clips(video_paths)
#merged = merge_clips(clips)
#save_clip(merged, "1.mp4")
trimed = trim_clip(clips[0], (0, 1), (0, 3))
save_clip(trimed, "2.mp4")
#speeded = set_clip_speed(clips[0], 0.5)
#save_clip(speeded, "3.mp4")
