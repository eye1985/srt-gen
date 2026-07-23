import argparse
import sys
import torch
from pathlib import Path

from .utils import is_apple, is_ffmpeg_available
from .whisper import whisper_transcribe, faster_whisper_transcribe
from .writer import write_to
from .languages import SUPPORTED_LANGUAGES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="srt-gen",
        description="Transcribe media files and generate a subtitle",
    )
    parser.add_argument(
        "--input", required=True, type=str, help="eg. ./videos/video01.mp4"
    )
    parser.add_argument("--language", type=str, help="eg. en")
    parser.add_argument(
        "--translate", action="store_true", help="Translate text to english"
    )
    return parser


# Returns a shell exit code: 0 = success, non-zero = failure. Without this,
# `srt-gen ... && next-step` would run next-step even when we bailed out early.
def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    input_path_and_file = Path(args.input)

    if not input_path_and_file.is_file():
        print("Input file is not a file", file=sys.stderr)
        return 1

    filename = args.input.split("/")[-1]
    path = "/".join(args.input.split("/")[:-1])

    if args.language is not None and args.language not in SUPPORTED_LANGUAGES:
        print("Please input a supported language code", file=sys.stderr)
        return 1

    if is_apple():
        print("Only Apple silicon is supported for now", file=sys.stderr)
        if not is_ffmpeg_available():
            print("ffmpeg not found in PATH", file=sys.stderr)
            return 1

        texts = whisper_transcribe(args.input, args.language, args.translate)
    elif torch.cuda.is_available():
        texts = faster_whisper_transcribe(args.input, args.language, args.translate)
    else:
        print(
            "Your hardware is not supported. Only Apple silicon or NVIDIA GPU is supported",
            file=sys.stderr,
        )
        return 1

    write_to(f".{path}/{filename.split('.')[0]}.srt", texts, srt=True)
    print("Done!")
    return 0


# True only when run as a program (`python -m srt_gen.main`), not on import, so
# importing this module never kicks off a transcription. The `srt-gen` command
# skips this block and calls main() directly.
if __name__ == "__main__":
    raise SystemExit(main())
