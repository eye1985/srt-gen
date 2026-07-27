import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="srt-gen",
        description="Transcribe media files and generate a subtitle",
    )
    parser.add_argument("--input", type=str, help="eg. ./videos/video01.mp4")
    parser.add_argument("--model", type=str, default="", help="e.g --model large")
    parser.add_argument("--language", type=str, help="eg. en")
    parser.add_argument(
        "--translate", action="store_true", help="Translate text to english"
    )
    # No default: unset lets each backend use its own, rather than pinning every
    # decode to one fixed temperature.
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="eg. 0.8 (0.0 is greedy). Omit to use the backend default",
    )
    parser.add_argument(
        "--condition-on-previous-text",
        action="store_true",
        help="Feed each segment the previous one as context",
    )
    parser.add_argument("--ui", action="store_true", help="Use UI")
    return parser
