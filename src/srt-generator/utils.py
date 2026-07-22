import platform
import shutil


def is_apple():
    system = platform.system()
    machine = platform.machine()
    if system == "Darwin" and machine == "arm64":
        return True
    return False


def is_ffmpeg_available():
    ffmpeg = shutil.which("ffmpeg")
    return ffmpeg is not None


def to_hh_mm_ss_ms(seconds: float):
    total_ms = round(seconds * 1000)
    total_seconds, ms = divmod(total_ms, 1000)
    total_minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(total_minutes, 60)

    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"
