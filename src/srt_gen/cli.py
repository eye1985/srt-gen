import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="srt-gen",
        description="Transcribe media files and generate a subtitle",
    )
    parser.add_argument(
        "--input", required=True, type=str, help="eg. ./videos/video01.mp4"
    )
    parser.add_argument("--model", type=str, default="", help="e.g --model large")
    parser.add_argument("--language", type=str, help="eg. en")
    parser.add_argument(
        "--translate", action="store_true", help="Translate text to english"
    )
    return parser
