import sys
import ctranslate2
from pathlib import Path

from .utils import is_apple, is_linux
from .whisper import (
    whisper_transcribe,
    faster_whisper_transcribe,
    mlx_models,
    fw_models,
    NotSupportedModelException,
)
from .writer import write_to
from .languages import SUPPORTED_LANGUAGES
from .cli import build_parser


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
        print(",".join(SUPPORTED_LANGUAGES), file=sys.stderr)
        return 1

    if is_linux():
        # The CUDA path ships cuBLAS/cuDNN as Windows-only wheels, so Linux would
        # still need a manual CUDA setup. Reject it rather than half-support it.
        print("Linux is not supported", file=sys.stderr)
        return 1

    if is_apple():
        try:
            texts = whisper_transcribe(
                file_path=args.input,
                language=args.language,
                model=args.model,
                translate=args.translate,
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

    write_to(f".{path}/{filename.split('.')[0]}.srt", texts, srt=True)
    print("Done!")
    return 0


# True only when run as a program (`python -m srt_gen.main`), not on import, so
# importing this module never kicks off a transcription. The `srt-gen` command
# skips this block and calls main() directly.
if __name__ == "__main__":
    raise SystemExit(main())
