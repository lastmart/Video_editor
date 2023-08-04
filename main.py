from video_editor_parser import Parser


video_paths = [
    r"/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/fugu_eat_carrot.mp4",
    r'/mnt/c/Users/egore/OneDrive/Документы/python/python_task/Video_editor/resources/shrek_dancing.mp4'
]


if __name__ == "__main__":
    parser = Parser()
    args = parser.parse_args()
    args.func(args)
