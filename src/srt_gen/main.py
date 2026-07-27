import sys
import ctranslate2
from pathlib import Path

from .utils import is_apple, is_linux
from .whisper import (
    whisper_transcribe,
    faster_whisper_transcribe,
    NotSupportedModelException,
)
from .models import mlx_models, fw_models
from .writer import write_to
from .languages import SUPPORTED_LANGUAGES
from .cli import build_parser

from .ui.app import start_ui


def build_progress_printer():
    """Report decode progress on stderr, one line per percent gained.

    Deliberately not a \\r-redrawn bar: both backends print segment text to stdout as
    they decode, which would scroll a single-line bar away every few seconds. Separate
    lines survive that interleaving, and keeping progress on stderr means `srt-gen ...
    > out.txt` still shows it.
    """
    last_percent = -1

    def report(fraction: float) -> None:
        nonlocal last_percent
        percent = int(fraction * 100)
        if percent != last_percent:
            last_percent = percent
            print(f"[{percent:3d}%]", file=sys.stderr, flush=True)

    return report


# Returns a shell exit code: 0 = success, non-zero = failure. Without this,
# `srt-gen ... && next-step` would run next-step even when we bailed out early.
def main(argv: list[str] | None = None) -> int:
    if is_linux():
        # The CUDA path ships cuBLAS/cuDNN as Windows-only wheels, so Linux would
        # still need a manual CUDA setup. Reject it rather than half-support it.
        print("Linux is not supported", file=sys.stderr)
        return 1

    args = build_parser().parse_args(argv)
    if args.ui:
        start_ui()
        return 0
    else:
        if args.input is None:
            print("Please input a file", file=sys.stderr)
            return 1

        input_path_and_file = Path(args.input)

        if not input_path_and_file.is_file():
            print("Input file is not a file", file=sys.stderr)
            return 1

        # Written next to the input, same name with an .srt suffix, whether the
        # input was given as a relative or an absolute path.
        output_path = input_path_and_file.with_suffix(".srt")

        if args.language is not None and args.language not in SUPPORTED_LANGUAGES:
            print("Please input a supported language code", file=sys.stderr)
            print(",".join(SUPPORTED_LANGUAGES), file=sys.stderr)
            return 1

        progress = build_progress_printer()

        if is_apple():
            try:
                texts = whisper_transcribe(
                    file_path=args.input,
                    language=args.language,
                    model=args.model,
                    translate=args.translate,
                    on_progress=progress,
                )
            except NotSupportedModelException as e:
                print(f"{e}\n", file=sys.stderr)
                print("\n".join(mlx_models), file=sys.stderr)
                return 1

        # CTranslate2 is what faster-whisper actually runs on, so ask it rather than
        # torch: its CUDA runtime is separate, and the two can disagree.
        elif ctranslate2.get_cuda_device_count() > 0:
            try:
                texts = faster_whisper_transcribe(
                    file_path=args.input,
                    language=args.language,
                    translate=args.translate,
                    model=args.model,
                    on_progress=progress,
                )
            except NotSupportedModelException as e:
                print(f"{e}\n", file=sys.stderr)
                print("\n".join(fw_models), file=sys.stderr)
                return 1
        else:
            print(
                "Your hardware is not supported. Only Apple silicon or NVIDIA GPU is supported",
                file=sys.stderr,
            )
            return 1

        write_to(output_path, texts, srt=True)
        print("Done!")
        return 0


# True only when run as a program (`python -m srt_gen.main`), not on import, so
# importing this module never kicks off a transcription. The `srt-gen` command
# skips this block and calls main() directly.
if __name__ == "__main__":
    raise SystemExit(main())
