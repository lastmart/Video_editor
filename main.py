from moviepy.editor import VideoFileClip, concatenate_videoclips


def merge_videos(video_paths, output_path):
    clips = []
    for path in video_paths:
        clip = VideoFileClip(path)
        clips.append(clip)

    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path)


# Пример использования:
video_paths = [
    "/Users/dimasta/work/Video_editor/resources/fugu_eat_carrot.mp4",
    "/Users/dimasta/work/Video_editor/resources/shrek_dancing.mp4"
]

output_path = "merged_video.mp4"
merge_videos(video_paths, output_path)
