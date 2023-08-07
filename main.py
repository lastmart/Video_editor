from video_editor_parser import Parser


if __name__ == "__main__":
    parser = Parser()
    args = parser.parse_args()
    args.func(args)
