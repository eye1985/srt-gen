import os
import platform
import sys
from pathlib import Path


def add_cuda_dll_dirs() -> None:
    # The nvidia-*-cu12 wheels drop cuBLAS/cuDNN into site-packages\nvidia\*\bin,
    # but CTranslate2 won't search there on its own (PyTorch registers these dirs
    # for you; faster-whisper doesn't). Without this the CUDA path dies with
    # "cublas64_12.dll is not found or cannot be loaded".
    #
    # CTranslate2 pulls cuBLAS/cuDNN in with a plain LoadLibrary("cublas64_12.dll")
    # at inference time, which uses the standard Windows search order. That order
    # consults PATH but ignores os.add_dll_directory(), so we prepend the wheels'
    # bin dirs to PATH. Windows is the only CUDA platform we support (Linux is
    # rejected in main), so this no-ops elsewhere and if the wheels are absent.
    if sys.platform != "win32":
        return

    # `nvidia` is the namespace package that the nvidia-cublas-cu12 and
    # nvidia-cudnn-cu12 wheels (in pyproject.toml) install into.
    try:
        import nvidia
    except ImportError:
        return

    bin_dirs = [
        str(bin_dir)
        for root in nvidia.__path__
        for bin_dir in Path(root).glob("*/bin")
        if bin_dir.is_dir()
    ]
    if not bin_dirs:
        return

    os.environ["PATH"] = os.pathsep.join(bin_dirs + [os.environ.get("PATH", "")])


def is_apple():
    system = platform.system()
    machine = platform.machine()
    if system == "Darwin" and machine == "arm64":
        return True
    return False


def is_linux():
    return platform.system() == "Linux"


def to_hh_mm_ss_ms(seconds: float):
    total_ms = round(seconds * 1000)
    total_seconds, ms = divmod(total_ms, 1000)
    total_minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"
