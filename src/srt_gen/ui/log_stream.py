import io
import sys
from contextlib import contextmanager
from typing import Callable, Optional

# Called once per completed line of captured output.
LineCallback = Callable[[str], None]


class _LineStream(io.TextIOBase):
    """A file-like stand-in for sys.stdout that reports whole lines to a callback.

    The backend has no logging hooks of its own, it just prints: mlx_whisper runs
    with verbose=True and prints every segment as it decodes, and whisper.py prints
    the detected language and the elapsed time. Standing in for the stream is what
    makes that visible in the UI without threading a callback through every layer.

    Output is still forwarded to the original stream, so running from a terminal
    keeps behaving exactly as before.
    """

    def __init__(self, on_line: LineCallback, original: Optional[io.TextIOBase]):
        self.__on_line = on_line
        self.__original = original
        self.__pending = ""

    def write(self, text: str) -> int:
        if self.__original is not None:
            self.__original.write(text)

        self.__pending += text
        while "\n" in self.__pending:
            line, self.__pending = self.__pending.split("\n", 1)
            self.__on_line(line.rstrip("\r"))
        return len(text)

    def flush(self):
        if self.__original is not None:
            self.__original.flush()

    def drain(self):
        """Report whatever is left over from a line that never got its newline."""
        if self.__pending:
            self.__on_line(self.__pending.rstrip("\r"))
            self.__pending = ""

    @property
    def encoding(self) -> str:
        return getattr(self.__original, "encoding", "utf-8")

    def writable(self) -> bool:
        return True


@contextmanager
def capture_output(on_line: LineCallback):
    """Route everything printed inside the block to on_line, one call per line.

    sys.stdout is process-wide, so this catches prints from any thread for as long
    as the block runs. That is fine here because the UI disables its buttons for
    the duration of a transcribe, leaving the worker as the only thing printing.

    Both streams are always restored, including when the block raises. In a bundled
    app the originals can be None, which the stand-in handles by simply not
    forwarding.
    """
    stdout = _LineStream(on_line, sys.stdout)
    stderr = _LineStream(on_line, sys.stderr)

    original_stdout, original_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = stdout, stderr
    try:
        yield
    finally:
        stdout.drain()
        stderr.drain()
        sys.stdout, sys.stderr = original_stdout, original_stderr
