import argparse
import sys

from .utils import is_apple, is_ffmpeg_available
from .whisper import whisper_transcribe
from .writer import write_to

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="srt-gen",
        description="Transcribe media files and generate a subtitle",
    )
    parser.add_argument("--input", required=True, type=str, help="eg. ./videos/video01.mp4")
    parser.add_argument("--output", required=True, type=str, help="eg. ./results/video01.srt")
    parser.add_argument("--language", type=str, default="english", help="eg. english")
    return parser


def main(argv: list[str] | None = None) -> int:
    # Returns a shell exit code: 0 = success, non-zero = failure. Without this,
    # `srt-gen ... && next-step` would run next-step even when we bailed out early.
    args = build_parser().parse_args(argv)

    if not is_apple():
        print("Only Apple silicon is supported for now", file=sys.stderr)
        return 1

    if not is_ffmpeg_available():
        print("ffmpeg not found in PATH", file=sys.stderr)
        return 1

    texts = whisper_transcribe(args.input, args.language)
    write_to(args.output, texts, srt=True)
    print("Done!")
    return 0


# True only when run as a program (`python -m srt_gen.main`), not on import, so
# importing this module never kicks off a transcription. The `srt-gen` command
# skips this block and calls main() directly.
if __name__ == "__main__":
    raise SystemExit(main())